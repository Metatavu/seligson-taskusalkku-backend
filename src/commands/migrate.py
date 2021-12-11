import sys
import logging
import os
import time
import click
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session, Query
from memory_profiler import profile


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import salkku_models as source_models
from database import models as destination_models


logger = logging.getLogger(__name__)

"""
mapper = {
    source_models.FundSecurity: {
        "destination_tables": [(destination_models.Fund,
        "field_mapping": {
            "fundID": "original_id"
        "securityID": ""
        "securityName_fi" = Column(String(255))
        "securityName_sv" = Column(String(255))
    }

}
"""


MIGRATION_DATABASE_SOURCE = "MIGRATION_DATABASE_SOURCE"
MIGRATION_DATABASE_DESTINATION = "MIGRATION_DATABASE_DESTINATION"
DESTINATION_ENTITIES = [ destination_models.Fund]
SOURCE_ENTITIES = [source_models.FundSecurity]

class MigrateHandler:

    def __init__(self, sleep, debug, batch):
        self.delay_in_second = sleep / 1000
        self.debug = debug
        self.batch = batch
        self.iteration = 0
        self.source_engine, self.destination_engine = self.get_sessions()

    def handle(self):
        with click.progressbar(length=self.batch,
                               label='processing the batch') as self.progress_status:
            with Session(self.source_engine) as source_session, Session(
                    self.destination_engine) as destination_session:

                self.process_fund(source_session=source_session, destination_session=destination_session)
                self.process_security(source_session=source_session, destination_session=destination_session)
                #self.process_security_rate(source_session=source_session, destination_session=destination_session)

                if not self.debug:
                    destination_session.commit()
                    click.echo(f"Finished the batch, Inserted {self.iteration} rows to the database")
                else:
                    click.echo("Finished the batch, nohting changed(in debug mode)")

    @staticmethod
    def get_sessions() -> (MockConnection, MockConnection):
        migration_source = os.environ.get(MIGRATION_DATABASE_SOURCE, "")
        migration_destination = os.environ.get(MIGRATION_DATABASE_DESTINATION, "")

        if not migration_source or not migration_destination:
            raise Exception("environment variables are not set")
        else:
            source_engine = create_engine(migration_source)
            destination_engine = create_engine(migration_destination)
            return source_engine, destination_engine

    def process_fund(self, source_session, destination_session):
        page = 0
        page_size = 1000
        number_of_rows = 100
        while self.iteration < self.batch:
            fund_securities = list(self.generate_query(session=source_session,entity=source_models.FundSecurity, page=page, page_size=page_size,number_of_rows=number_of_rows))
            page += 1
            if len(fund_securities) == 0:
                break

            for _, fund_security in enumerate(fund_securities):
                existing_fund = destination_session.query(destination_models.Fund).filter(
                    destination_models.Fund.original_id == fund_security.fundID).one_or_none()
                if not existing_fund:
                    new_fund = destination_models.Fund()
                    new_fund.original_id = fund_security.fundID
                    destination_session.add(new_fund)
                    self.iteration += 1
                    if self.iteration >= self.batch:
                        break
                    self.progress_status.update(1)
                    self.delay()

    @profile
    def process_security(self, source_session, destination_session):
        page = 0
        page_size = 1000
        number_of_rows = 100
        while self.iteration < self.batch:
            securities = list(self.generate_query(session=source_session, entity=source_models.SECURITYrah, page=page, page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(securities) == 0:
                break

            for _, security in enumerate(list(securities)):
                existing_security: destination_models.Security = destination_session.query(destination_models.Security).filter(
                    destination_models.Security.original_id == security.SECID).one_or_none()
                if not existing_security:
                    original_fund: source_models.FundSecurity = source_session.query(source_models.FundSecurity).filter(
                        source_models.FundSecurity.securityID == security.SECID).one_or_none()
                    if not original_fund:
                        # this is a security without fund
                        fund_id = None
                    else:
                        fund_id = destination_session.query(destination_models.Fund.id).filter(
                            destination_models.Fund.original_id == original_fund.fundID).scalar()

                    new_security = destination_models.Security()
                    new_security.original_id = security.SECID
                    new_security.fund_id = fund_id
                    new_security.currency = security.CURRENCY
                    new_security.name_fi = security.NAME1
                    new_security.name_sv = security.NAME2
                    destination_session.add(new_security)

                    self.iteration += 1
                    if self.iteration >= self.batch:
                        break
                    self.progress_status.update(1)
                    self.delay()

    def process_security_rate(self, source_session, destination_session):
        page = 0
        page_size = 1000
        number_of_rows = 100
        while self.iteration < self.batch:
            rates = list(self.generate_query(session=source_session, entity=source_models.RATErah, page=page,
                                             page_size=page_size, number_of_rows=number_of_rows))
            page += 1
            if len(rates) == 0:
                break
            for _, rate in enumerate(rates):
                existing_rate: destination_models.SecurityRate = destination_session.query(
                    destination_models.SecurityRate).filter(
                    destination_models.SecurityRate.original_id == security.SECID).one_or_none()

    def delay(self):
        if self.iteration % 10000 == 0:
            time.sleep(self.delay_in_second)

    @staticmethod
    def generate_query(session: Session,  entity,filters=None, page=None, page_size=None, number_of_rows=None):
        query: Query = session.query(entity)
        if filters:
            query = query.filter_by(**filters)
        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)

        return query.yield_per(number_of_rows) if number_of_rows else query.all()



@click.command()
@click.option("--debug", default=True, help="Debug, readonly for testing purposes")
@click.option("--sleep", default=1000, help="sleep delay in miliseconds")
@click.option("--batch", default=1, help="number of rows that are read and migrated into new database")
def main(debug, sleep, batch):
    """Migration method"""
    handler = MigrateHandler(sleep=sleep, debug=debug, batch=batch)
    handler.handle()


if __name__ == '__main__':
    main()
