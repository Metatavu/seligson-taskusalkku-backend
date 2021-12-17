import sys
import logging
import os
import time
import math
from datetime import datetime, timedelta
from typing import List

import click
from sqlalchemy import create_engine, and_, func
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session, Query

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import salkku_models as source_models
from database import models as destination_models

logger = logging.getLogger(__name__)


class MigrateHandler:

    def __init__(self, sleep, timeout, debug, batch, target, update, create_missing_relations):
        self.skip_caches = False
        self.start_time = datetime.now()
        self.timeout = datetime.now() + timedelta(minutes=timeout)
        self.delay_in_second = sleep / 1000
        self.debug = debug
        self.batch = batch
        self.iteration = 0
        self.counter = 0
        self.target = target
        self.update = update
        self.create_missing_relations = create_missing_relations
        self.source_engine, self.destination_engine = self.get_sessions()
        self.misc_entities = []
        self.current_target = ""
        self.fund_id_cache = {}
        self.security_id_cache = {}
        self.portfolio_id_cache = {}
        self.company_id_cache = {}
        self.existing_security_rates = {}
        self.destination_targets = [destination_models.Fund, destination_models.Security,
                                    destination_models.SecurityRate, destination_models.Company,
                                    destination_models.LastRate, destination_models.Portfolio,
                                    destination_models.PortfolioLog, destination_models.PortfolioTransaction]

    def get_fund_id(self, destination_session, original_id):
        result = None

        if not self.skip_caches:
            result = self.fund_id_cache.get(original_id, None)

        if not result:
            result = destination_session.query(destination_models.Fund.id).filter(
                destination_models.Fund.original_id == original_id).scalar()

            if result:
                self.fund_id_cache[original_id] = result

        return result

    def should_timeout(self):
        result = self.timeout < datetime.now()

        if result:
            self.print_message("Timeout reached, stopping...")

        return result

    def call_process(self, function_name, **kwargs):
        if hasattr(self, function_name) and callable(function := getattr(self, function_name)):
            function(**kwargs)
        else:
            self.print_message("Not a valid model as target")

    def handle(self):
        self.start_time = datetime.now()
        self.print_message(f"Start time: {self.start_time}")

        with Session(self.source_engine) as source_session, Session(
                self.destination_engine) as destination_session:
            kwargs = {"source_session": source_session, "destination_session": destination_session}
            function_name = f"process_{self.target}"
            for target in self.destination_targets:
                target_table = target.__tablename__
                self.current_target = target_table
                self.print_message(f"\nStarting {target_table}")

                if not self.target:
                    function_name = f"process_{target_table}"
                    self.call_process(function_name=function_name, **kwargs)
                elif self.target and self.target == target_table:
                    self.call_process(function_name=function_name, **kwargs)
                else:
                    self.print_message(f"skipping {target_table}")
                if not self.debug:
                    destination_session.commit()
                    self.print_message(f"\nFinished {target_table}")
                else:
                    self.print_message(F"\nFinished {target_table} nothing changed(in debug mode)")

            end_time = datetime.now()
            total_time = end_time - self.start_time

            self.print_message(f"End time: {end_time}, total time: {total_time}")

            self.report_misc()

    def process_fund(self, source_session, destination_session):
        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=0)
        while self.iteration < self.batch and not self.should_timeout():
            fund_securities = list(
                self.generate_query(session=source_session, entity=source_models.FundSecurity, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(fund_securities) == 0:
                break

            for _, fund_security in enumerate(fund_securities):
                self.update_progress_bar_info()
                existing_fund: destination_models.Fund = destination_session.query(destination_models.Fund).filter(
                    destination_models.Fund.original_id == fund_security.fundID).one_or_none()
                if not existing_fund or self.update:
                    self.upsert_fund(session=destination_session, fund=existing_fund if self.update else None,
                                     original_id=fund_security.fundID)
                    if self.has_the_progress_completed(session=destination_session):
                        break

    def process_security(self, source_session, destination_session):
        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=0)
        while self.iteration < self.batch and not self.should_timeout():
            securities: List[source_models.SECURITYrah] = list(
                self.generate_query(session=source_session, entity=source_models.SECURITYrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(securities) == 0:
                break

            for _, security in enumerate(list(securities)):
                original_security_id = security.SECID
                existing_security: destination_models.Security = self.get_security_from_original_id(
                    session=destination_session, original_security_id=original_security_id)
                if not existing_security or self.update:
                    original_fund: source_models.FundSecurity = source_session.query(source_models.FundSecurity).filter(
                        source_models.FundSecurity.securityID == security.SECID).one_or_none()
                    if not original_fund:
                        # this is a security without fund
                        fund_id = None
                    else:
                        fund_id = self.get_fund_id(destination_session=destination_session,
                                                   original_id=original_fund.fundID)

                    self.upsert_security(session=destination_session,
                                         security=existing_security if self.update else None,
                                         original_id=original_security_id,
                                         fund_id=fund_id,
                                         currency=security.CURRENCY, name_fi=security.NAME1,
                                         name_sv=security.NAME2)
                    if self.has_the_progress_completed(session=destination_session):
                        break

    def process_security_rate(self, source_session, destination_session):
        initial_rates = destination_session.query(destination_models.SecurityRate).yield_per(1000)

        for _, rate in enumerate(initial_rates):
            key = f"{rate.security_id}-{rate.rate_date}"
            self.existing_security_rates[key] = rate

        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=len(self.existing_security_rates.keys()))
        while self.iteration < self.batch and not self.should_timeout():
            rates: List[source_models.RATErah] = list(
                self.generate_query(session=source_session, entity=source_models.RATErah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(rates) == 0:
                break

            for _, rate in enumerate(rates):
                original_security_id = rate.SECID
                self.update_progress_bar_info()
                _, security_id = self.get_or_create_security(session=destination_session,
                                                             original_id=original_security_id)
                if security_id:
                    existing_security_rate = self.get_existing_security_rate(destination_session,
                                                                             security_id,
                                                                             rate.RDATE)

                    if not existing_security_rate or self.update:
                        self.upsert_security_rate(session=destination_session, security_rate=existing_security_rate,
                                                  security_id=security_id, rate_date=rate.RDATE, rate_close=rate.RCLOSE)
                        if self.has_the_progress_completed(session=destination_session):
                            break

    def get_existing_security_rate(self, destination_session, security_id, rate_date):
        key = f"{security_id}-{rate_date.date()}"
        existing_security_rate = None

        if not self.skip_caches:
            existing_security_rate = self.existing_security_rates.get(key, None)

        if not existing_security_rate:
            existing_security_rate: destination_models.SecurityRate = destination_session.query(
                destination_models.SecurityRate).filter(
                and_(destination_models.SecurityRate.security_id == security_id,
                     destination_models.SecurityRate.rate_date == rate_date)).one_or_none()

        if existing_security_rate:
            self.existing_security_rates[key] = existing_security_rate

        return existing_security_rate

    def process_company(self, source_session, destination_session):
        row_count = destination_session.query(func.count(destination_models.Company.id)).scalar()
        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=row_count)
        while self.iteration < self.batch and not self.should_timeout():
            companies: List[source_models.COMPANYrah] = list(
                self.generate_query(session=source_session, entity=source_models.COMPANYrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(companies) == 0:
                print("finished")
                break

            for _, company in enumerate(companies):
                self.update_progress_bar_info()
                existing_company: destination_models.Company = self.get_company_from_original_id(
                    session=destination_session, original_company_id=company.COM_CODE)
                if not existing_company or self.update:
                    self.upsert_company(session=destination_session, company=existing_company,
                                        original_id=company.COM_CODE, ssn=company.SO_SEC_NR)
                    if self.has_the_progress_completed(session=destination_session):
                        break

    def process_last_rate(self, source_session, destination_session):
        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=0)
        while self.iteration < self.batch and not self.should_timeout():
            last_rates: List[source_models.RATELASTrah] = list(
                self.generate_query(session=source_session, entity=source_models.RATELASTrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(last_rates) == 0:
                break

            for _, last_rate in enumerate(last_rates):
                self.update_progress_bar_info()
                original_security_id = last_rate.SECID
                _, security_id = self.get_or_create_security(session=destination_session,
                                                             original_id=original_security_id)
                if security_id:
                    existing_last_rate: destination_models.LastRate = destination_session.query(
                        destination_models.LastRate).filter(
                        destination_models.LastRate.security_id == security_id).one_or_none()

                    if not existing_last_rate or self.update:
                        self.upsert_last_rate(session=destination_session, last_rate=existing_last_rate,
                                              security_id=security_id, rate_close=last_rate.RCLOSE)
                        if self.has_the_progress_completed(session=destination_session):
                            break

    def process_portfolio(self, source_session, destination_session):
        row_count = destination_session.query(func.count(destination_models.Portfolio.id)) \
            .filter(destination_models.Portfolio.name != "UNDEFINED") \
            .scalar()

        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=row_count)
        while self.iteration < self.batch and not self.should_timeout():
            portfolios: List[source_models.PORTFOLrah] = list(
                self.generate_query(session=source_session, entity=source_models.PORTFOLrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(portfolios) == 0:
                break

            for _, portfolio in enumerate(portfolios):
                company_original_id = portfolio.COM_CODE
                self.update_progress_bar_info()
                _, company_id = self.get_or_create_company(session=destination_session,
                                                           original_id=company_original_id)

                if company_id:
                    existing_portfolio = self.get_portfolio_from_original_id(session=destination_session,
                                                                             original_portfolio_id=portfolio.PORID)
                    if not existing_portfolio or self.update:
                        self.upsert_portfolio(session=destination_session, portfolio=existing_portfolio,
                                              original_id=portfolio.PORID, company_id=company_id,
                                              name=portfolio.NAME1)
                        if self.has_the_progress_completed(session=destination_session):
                            break

    def process_portfolio_log(self, source_session, destination_session):
        row_count = destination_session.query(func.count(destination_models.PortfolioLog.id)).scalar()

        unix_time = datetime(1970, 1, 1, 0, 0)
        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=row_count)
        while self.iteration < self.batch and not self.should_timeout():
            portfolio_logs: List[source_models.PORTLOGrah] = list(
                self.generate_query(session=source_session, entity=source_models.PORTLOGrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(portfolio_logs) == 0:
                break

            for _, portfolio_log in enumerate(portfolio_logs):
                self.update_progress_bar_info()
                security_original_id = portfolio_log.SECID
                _, security_id = self.get_or_create_security(session=destination_session,
                                                             original_id=security_original_id)
                if security_id:
                    c_security_original_id = portfolio_log.CSECID
                    if c_security_original_id.strip():  # for the case that null is inserted as SECID = ' '
                        _, c_security_id = self.get_or_create_security(session=destination_session,
                                                                       original_id=c_security_original_id)
                    else:
                        c_security_id = None
                    portfolio_original_id = portfolio_log.PORID
                    if portfolio_original_id:
                        _, portfolio_id = self.get_or_create_portfolio(session=destination_session,
                                                                       original_id=portfolio_original_id,
                                                                       com_code=portfolio_log.COM_CODE)

                    else:
                        # without the portfolio key we cant do anything, we try to grab the right portfolio from
                        # portfolio table considering the company code. If there are more than one portfolio then
                        # we should alert and ask how to resolve the situation manually.
                        company = self.get_company_from_original_id(session=destination_session,
                                                                    original_company_id=portfolio_log.COM_CODE)
                        portfolios = self.get_portfolios_from_company(session=destination_session, company_id=company.id)
                        if len(portfolios) != 1:
                            portfolio_id = None
                            self.alert(entity="portfolio_log", key="after row", value=self.counter)
                            self.alert(entity=portfolio_log.__dict__, key="original_id", value=portfolio_log.PORID)

                        else:
                            portfolio = portfolios[0]
                            portfolio_id = portfolio.id
                            self.alert(entity="portfolio_log", key="after row", value=self.counter)
                            self.alert(entity="mapped company to portfolio", key=portfolio.company_id,
                                       value=portfolio.id)

                    if portfolio_id:
                        existing_portfolio_log = destination_session.query(destination_models.PortfolioLog).filter(
                            destination_models.PortfolioLog.transaction_number == portfolio_log.TRANS_NR).one_or_none()
                        if not existing_portfolio_log or self.update:
                            # payment dates are supposed to exist but there are cases without them,
                            # check if date is before 1970

                            logged_date = portfolio_log.PMT_DATE
                            if logged_date and logged_date > unix_time:
                                payment_date = logged_date
                            else:
                                payment_date = None

                            self.upsert_portfolio_log(session=destination_session,
                                                      portfolio_log=existing_portfolio_log,
                                                      transaction_number=portfolio_log.TRANS_NR,
                                                      transaction_code=portfolio_log.TRANS_CODE,
                                                      transaction_date=portfolio_log.TRANS_DATE,
                                                      c_total_value=portfolio_log.CTOT_VALUE,
                                                      portfolio_id=portfolio_id,
                                                      security_id=security_id,
                                                      c_security_id=c_security_id,
                                                      amount=portfolio_log.AMOUNT,
                                                      c_price=portfolio_log.CPRICE,
                                                      payment_date=payment_date,
                                                      c_value=portfolio_log.CVALUE,
                                                      provision=portfolio_log.PROVISION,
                                                      status=portfolio_log.STATUS)
                            if self.has_the_progress_completed(session=destination_session):
                                break

    def alert(self, entity, key, value):
        alert_message = {"entity": entity, "key": key, "value": value}
        self.misc_entities.append(alert_message)
        print(alert_message)

    def print_message(self, message):
        if self.debug:
            click.echo(f"{message}")
        else:
            logger.warning(message)

    def process_portfolio_transaction(self, source_session, destination_session):
        row_count = destination_session.query(func.count(destination_models.PortfolioTransaction.id)).scalar()

        page, page_size, number_of_rows = self.calculate_starting_point(starting_row=row_count)
        while self.iteration < self.batch and not self.should_timeout():
            portfolio_transactions: List[source_models.PORTRANSrah] = list(
                self.generate_query(session=source_session, entity=source_models.PORTRANSrah, page=page,
                                    page_size=page_size, number_of_rows=number_of_rows))

            page += 1
            if len(portfolio_transactions) == 0:
                break

            for _, portfolio_transaction in enumerate(portfolio_transactions):
                self.update_progress_bar_info()
                security_original_id = portfolio_transaction.SECID
                _, security_id = self.get_or_create_security(session=destination_session,
                                                             original_id=security_original_id)

                portfolio_original_id = portfolio_transaction.PORID

                _, portfolio_id = self.get_or_create_portfolio(session=destination_session,
                                                               original_id=portfolio_original_id,
                                                               com_code=portfolio_transaction.COM_CODE)

                existing_portfolio_transaction = destination_session.query(
                    destination_models.PortfolioTransaction).filter(
                    destination_models.PortfolioTransaction.transaction_number == portfolio_transaction.TRANS_NR)

                if not existing_portfolio_transaction or self.update:
                    self.upsert_portfolio_transaction(session=destination_session,
                                                      portfolio_transaction=existing_portfolio_transaction,
                                                      transaction_number=portfolio_transaction.TRANS_NR,
                                                      transaction_date=portfolio_transaction.TRANS_DATE,
                                                      amount=portfolio_transaction.AMOUNT,
                                                      purchase_c_value=portfolio_transaction.PUR_CVALUE,
                                                      portfolio_id=portfolio_id,
                                                      security_id=security_id
                                                      )

                    if self.has_the_progress_completed(session=destination_session):
                        break

    @staticmethod
    def get_company_from_original_id(session, original_company_id) -> destination_models.Company:
        return session.query(destination_models.Company).filter(
            destination_models.Company.original_id == original_company_id).one_or_none()

    @staticmethod
    def get_security_from_original_id(session, original_security_id) -> destination_models.Security:
        return session.query(destination_models.Security).filter(
            destination_models.Security.original_id == original_security_id).one_or_none()

    @staticmethod
    def get_portfolio_from_original_id(session, original_portfolio_id) -> destination_models.Portfolio:
        return session.query(destination_models.Portfolio).filter(
            destination_models.Portfolio.original_id == original_portfolio_id).one_or_none()

    @staticmethod
    def get_portfolios_from_company(session, company_id) -> List[destination_models.Portfolio]:
        return session.query(destination_models.Portfolio).filter(
            destination_models.Portfolio.company_id == company_id).all()

    def get_or_create_security(self, session, original_id):
        cached_id = None

        if not self.skip_caches:
            cached_id = self.security_id_cache.get(original_id, None)

        if cached_id:
            return False, cached_id

        existing_security = self.get_security_from_original_id(session=session,
                                                               original_security_id=original_id)
        if not existing_security:
            self.alert(entity=destination_models.Security, key="original_id", value=original_id)
            if self.create_missing_relations:

                new_security = self.upsert_security(session=session, security=existing_security,
                                                    original_id=original_id,
                                                    fund_id=None, currency="",
                                                    name_fi="", name_sv="", )
                security_id = new_security.id
                created = True
            else:
                created = False
                security_id = None
        else:
            security_id = existing_security.id
            created = False

        if not self.skip_caches and original_id and security_id:
            self.security_id_cache[original_id] = security_id

        return created, security_id

    def get_or_create_portfolio(self, session, original_id, com_code):
        cached_id = None

        if not self.skip_caches and original_id:
            cached_id = self.portfolio_id_cache.get(original_id)

        if cached_id:
            return False, cached_id

        existing_portfolio = self.get_portfolio_from_original_id(session=session,
                                                                 original_portfolio_id=original_id)
        if not existing_portfolio:
            # this should not happen at this stage. It means there are portfolios that are not in PORTFOLrah!
            # so we add them as missing ones, since we do not have any information about them anyway.

            # we check if com code exists before moving on

            company_original_id = com_code
            _, company_id = self.get_or_create_company(session=session, original_id=company_original_id)
            if company_id:
                if self.create_missing_relations:
                    _, new_portfolio = self.upsert_portfolio(session=session, portfolio=existing_portfolio,
                                                             original_id=original_id, company_id=company_id)

                    portfolio_id = new_portfolio.id

                    self.alert(entity=destination_models.Portfolio.__dict__, key="original_id", value=portfolio_id)
                    self.misc_entities.append({"entity": destination_models.Portfolio, "value": original_id})

                    created = True
                else:
                    portfolio_id = None
                    created = False
            else:
                portfolio_id = None
                created = False

        else:
            portfolio_id = existing_portfolio.id
            created = False

        if not self.skip_caches and original_id and portfolio_id:
            self.security_id_cache[original_id] = portfolio_id

        return created, portfolio_id

    def get_or_create_company(self, session, original_id):
        cached_id = None

        if not self.skip_caches and original_id:
            cached_id = self.company_id_cache.get(original_id)

        if cached_id:
            return False, cached_id

        company_original_id = original_id
        existing_company = self.get_company_from_original_id(session=session, original_company_id=company_original_id)
        if not existing_company:
            # this should not happen at this stage. It means there are companies that are not in COMPANYrah!
            # so we add them as missing ones, since we do not have any information about them anyway.
            # and alert
            self.alert(entity=destination_models.Company, key="original_id", value=company_original_id)
            if self.create_missing_relations:

                new_company = self.upsert_company(session=session, company=existing_company,
                                                  original_id=company_original_id)
                company_id = new_company.id
                created = True
            else:
                company_id = None
                created = False
        else:
            company_id = existing_company.id
            created = False

        if not self.skip_caches and original_id and company_id:
            self.company_id_cache[original_id] = company_id

        return created, company_id

    @staticmethod
    def upsert_security(session, security, original_id, fund_id=None, currency="", name_fi="",
                        name_sv="") -> destination_models.Security:
        new_security = security if security else destination_models.Security()
        new_security.original_id = original_id
        new_security.fund_id = fund_id
        new_security.currency = currency
        new_security.name_fi = name_fi
        new_security.name_sv = name_sv
        session.add(new_security)
        session.flush()
        return new_security

    @staticmethod
    def upsert_security_rate(session, security_rate, security_id, rate_date,
                             rate_close) -> destination_models.SecurityRate:
        new_security_rate = security_rate if security_rate else destination_models.SecurityRate()
        new_security_rate.security_id = security_id
        new_security_rate.rate_date = rate_date
        new_security_rate.rate_close = rate_close
        session.add(new_security_rate)
        session.flush()
        return new_security_rate

    @staticmethod
    def upsert_last_rate(session, last_rate, security_id, rate_close) -> destination_models.LastRate:

        new_last_rate = last_rate if last_rate else destination_models.LastRate()
        new_last_rate.security_id = security_id
        new_last_rate.rate_close = rate_close
        session.add(new_last_rate)
        session.flush()
        return new_last_rate

    @staticmethod
    def upsert_company(session, company, original_id, ssn="") -> destination_models.Company:
        new_company = company if company else destination_models.Company()
        new_company.original_id = original_id
        new_company.ssn = ssn
        session.add(new_company)
        session.flush()
        return new_company

    @staticmethod
    def upsert_portfolio(session, portfolio, original_id, company_id, name) -> destination_models.Portfolio:
        new_portfolio = portfolio if portfolio else destination_models.Portfolio()
        new_portfolio.original_id = original_id
        new_portfolio.company_id = company_id
        new_portfolio.name = name
        session.add(new_portfolio)
        session.flush()
        return new_portfolio

    @staticmethod
    def upsert_fund(session, fund, original_id):
        new_fund = fund if fund else destination_models.Fund()
        new_fund.original_id = original_id
        session.add(new_fund)
        session.flush()
        return new_fund

    @staticmethod
    def upsert_portfolio_log(session, portfolio_log, transaction_number, transaction_code, transaction_date,
                             c_total_value,
                             portfolio_id, security_id, c_security_id, amount, c_price, payment_date, c_value,
                             provision, status):
        new_portfolio_log = portfolio_log if portfolio_log else destination_models.PortfolioLog()
        new_portfolio_log.transaction_number = transaction_number
        new_portfolio_log.transaction_code = transaction_code
        new_portfolio_log.transaction_date = transaction_date
        new_portfolio_log.c_total_value = c_total_value
        new_portfolio_log.portfolio_id = portfolio_id
        new_portfolio_log.security_id = security_id
        new_portfolio_log.c_security_id = c_security_id
        new_portfolio_log.amount = amount
        new_portfolio_log.c_price = c_price
        new_portfolio_log.payment_date = payment_date
        new_portfolio_log.c_value = c_value
        new_portfolio_log.provision = provision
        new_portfolio_log.status = status
        session.add(new_portfolio_log)
        session.flush()
        return new_portfolio_log

    @staticmethod
    def upsert_portfolio_transaction(session, portfolio_transaction, transaction_number, transaction_date, amount,
                                     purchase_c_value,
                                     portfolio_id, security_id):
        new_port_trans = portfolio_transaction if portfolio_transaction else destination_models.PortfolioTransaction()
        new_port_trans.transaction_number = transaction_number
        new_port_trans.transaction_date = transaction_date
        new_port_trans.amount = amount
        new_port_trans.purchase_c_value = purchase_c_value
        new_port_trans.portfolio_id = portfolio_id
        new_port_trans.security_id = security_id
        session.add(new_port_trans)
        session.flush()
        return new_port_trans

    def calculate_starting_point(self, starting_row=0) -> (int, int, int):
        page_size = 1000
        page = starting_row // page_size
        number_of_rows = 1000  # recommended value by docs for performance

        self.print_message(f"Info: starting fow {starting_row}, starting from page {page}")

        return page, page_size, number_of_rows

    def has_the_progress_completed(self, session) -> bool:
        self.iteration += 1
        if not self.debug and self.iteration % 10000 == 0:
            session.commit()
            time.sleep(self.delay_in_second)

        self.update_progress_bar_info()
        return True if self.iteration >= self.batch else False

    def update_progress_bar_info(self):
        self.counter += 1
        if self.counter % 10000 == 0:
            elapsed = datetime.now() - self.start_time
            progress_percentage = int(self.iteration / self.batch * 100)
            progress = f"{self.iteration}/{self.batch}"
            percentage = f"{progress_percentage}%"
            elapsed_text = f"elapsed time: {elapsed.seconds // 3600}:{elapsed.seconds // 60 % 60}:{elapsed.seconds % 60}"
            info = f"processing the batch for {self.current_target}"
            self.print_message(f"Info: {info} select count:{self.counter}  "
                               f"insert/update count={progress},{percentage} {elapsed_text}")
            self.delay()

    def delay(self):
        time.sleep(self.delay_in_second)


    def report_misc(self):
        if self.misc_entities:
            self.print_message("Issues with the following inserted rows:")

        for misc_entity in self.misc_entities:
            entity = misc_entity.get("entity")
            key = misc_entity.get("key")
            value = misc_entity.get("value")
            alert_message = f'{entity},{key}:{value}'
            if self.debug:
                print(alert_message)
            else:
                logger.warning(alert_message)

    @staticmethod
    def generate_query(session: Session, entity, filters=None, page=None, page_size=None,
                       number_of_rows=None) -> Query:
        query: Query = session.query(entity)
        if filters:
            query = query.filter_by(**filters)
        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)

        return query.yield_per(number_of_rows) if number_of_rows else query.all()

    @staticmethod
    def get_sessions() -> (MockConnection, MockConnection):
        migration_source = os.environ.get("SALKKU_DATABASE_URL", "")
        migration_destination = os.environ.get("BACKEND_DATABASE_URL", "")
        if not migration_source or not migration_destination:
            raise Exception("environment variables are not set")
        else:
            source_engine = create_engine(migration_source)
            destination_engine = create_engine(migration_destination)
            return source_engine, destination_engine


@click.command()
@click.option("--debug", default=True, help="Debug, readonly for testing purposes")
@click.option("--sleep", default=1000, help="sleep delay in milliseconds")
@click.option("--timeout", default=15, help="maximum run time in minutes")
@click.option("--batch", default=1, help="number of rows that are read and migrated into new database")
@click.option("--target", default="", help="Only migrates the target model")
@click.option("--update", default=False, help="updates existing rows from source, in case of difference")
@click.option("--create_missing_relations", default=False, help="create missing entities in other tables")
def main(debug, sleep, timeout, batch, target, update, create_missing_relations):
    """Migration method"""
    handler = MigrateHandler(sleep=sleep, timeout=timeout, debug=debug, batch=batch, target=target, update=update,
                             create_missing_relations=create_missing_relations)
    handler.handle()


if __name__ == '__main__':
    main()
