# coding: utf-8
import os
from fastapi_utils.cbv import cbv
from spec.apis.meetings_api import MeetingsApiSpec, router as meetings_api_router
from spec.models.meeting_time import MeetingTime
from spec.models.meeting import Meeting
from typing import List
from csv import reader
from datetime import date, datetime, timedelta, time
from spec.models.extra_models import TokenModel
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


@cbv(meetings_api_router)
class MeetingsApiImpl(MeetingsApiSpec):

    async def create_meeting(
        self,
        meeting: Meeting,
        token_bearer: TokenModel
    ) -> Meeting:

        mail_username = os.environ["MAIL_USERNAME"]
        mail_password = os.environ["MAIL_PASSWORD"]
        use_credentials = bool(mail_username) and bool(mail_password)
        validate_certs = use_credentials

        email_conf = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=os.environ["MAIL_FROM"],
            MAIL_PORT=os.environ["MAIL_PORT"],
            MAIL_SERVER=os.environ["MAIL_SERVER"],
            MAIL_TLS=eval(os.environ["MAIL_TLS"]),
            MAIL_SSL=eval(os.environ["MAIL_SSL"]),
            USE_CREDENTIALS=use_credentials,
            VALIDATE_CERTS=validate_certs
        )

        email_body = ""
        email_body += f"Päivämäärä ja aika: {str(meeting.time.date())} klo {str(meeting.time.time())}"
        email_body += f"\nKielivalinta: {meeting.language}"
        email_body += f"\nKielivalinta: {meeting.language}"
        email_body += f"\nTyyppi: {'Puhelinkeskustelu' if meeting.type == 'PHONE' else 'Tapaaminen'}"
        email_body += f"\nOsallistujia: {meeting.participantCount}"

        if meeting.contact.email or meeting.contact.phone:
            email_body += "\n\nHUOM! Kirjautunut käyttäjä on ilmoittanut yhteystietonsa erikseen tällä lomakkeella!"

        email_body += f"\n\nEtunimi: {meeting.contact.firstName}"
        email_body += f"\nSukunimi: {meeting.contact.lastName}"
        email_body += f"\nEmail: {meeting.contact.email}"
        email_body += f"\nPuhelinnumero: {meeting.contact.phone}"
        email_body += f"\n\nViesti: {meeting.additionalInformation}"

        message = MessageSchema(
            subject="UUSI AJANVARAUS (Taskusalkun kautta)",
            recipients=os.environ["MAIL_TO"].split(","),
            body=email_body)

        fm = FastMail(email_conf)
        try:
            await fm.send_message(message)
        except Exception:
            raise HTTPException(
                                status_code=500,
                                detail="Failed to send email due to invalid credentials."
                              )

        return meeting

    async def list_meeting_times(self,
                                 start_date: date,
                                 end_date: date,
                                 token_bearer: TokenModel
                                 ) -> List[MeetingTime]:

        if end_date < start_date:
            raise HTTPException(
                                status_code=400,
                                detail="End date before start date"
                              )

        if end_date < date.today() or start_date < date.today():
            raise HTTPException(
                                status_code=400,
                                detail="End date and start date can not be in the past"
                              )

        with open(os.environ["HOLIDAYS_CSV"]) as csv_file:
            rows = reader(csv_file, delimiter=",")
            row1 = next(rows)
            holidays = row1

        result = []

        first_available_date = start_date if start_date > date.today() else date.today()

        while first_available_date <= end_date:
            if str(first_available_date) in holidays or first_available_date.weekday() >= 5:
                first_available_date += timedelta(days=1)
                continue

            for hour in self.settings.MEETING_TIME_PERIOD:
                result.append(self.construct_meeting_time(first_available_date, hour, hour + 1))

            result.append(self.construct_meeting_time_from_time(first_available_date, time(hour=16, minute=30),
                                                                time(hour=17, minute=30)))

            first_available_date += timedelta(days=1)

        return result

    @staticmethod
    def construct_meeting_time(meeting_data: date, start_hour: int, end_hour: int) -> MeetingTime:
        meeting_start_time = datetime.combine(meeting_data, time(hour=start_hour))
        meeting_end_time = datetime.combine(meeting_data, time(hour=end_hour))

        return MeetingTime(startTime=meeting_start_time, endTime=meeting_end_time)

    @staticmethod
    def construct_meeting_time_from_time(meeting_data: date, start_time: time, end_time: time) -> MeetingTime:
        meeting_start_time = datetime.combine(meeting_data, start_time)
        meeting_end_time = datetime.combine(meeting_data, end_time)

        return MeetingTime(startTime=meeting_start_time, endTime=meeting_end_time)
