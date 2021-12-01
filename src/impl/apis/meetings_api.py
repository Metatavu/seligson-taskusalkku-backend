# coding: utf-8
import os
from fastapi_utils.cbv import cbv
from spec.apis.meetings_api import MeetingsApiSpec, router as meetings_api_router
from spec.models.meeting_time import MeetingTime
from spec.models.meeting import Meeting
from typing import List
from csv import reader
from datetime import *
from spec.models.extra_models import TokenModel
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.app import email_conf

@cbv(meetings_api_router)
class MeetingsApiImpl(MeetingsApiSpec):

    async def create_meeting(
        self,
        meeting: Meeting,
        token_bearer: TokenModel
    ) -> Meeting:
        import pdb
        pdb.set_trace()
        email_body = ""
        email_body += f"Päivämäärä ja aika: {str(meeting.time.date())} klo {str(meeting.time.time())}"
        email_body += f"\nKielivalinta: {meeting.language}"
        email_body += f"\nKielivalinta: {meeting.language}"
        email_body += f"\nTyyppi: {'Puhelinkeskustelu' if meeting.type == 'PHONE' else 'Tapaaminen'}"
        email_body += f"\nOsallistujia: {meeting.participantCount}"
        # TODO check customer number

        if meeting.contact.email or meeting.contact.phone:
            email_body += "\n\nHUOM! Kirjautunut käyttäjä on ilmoittanut yhteystietonsa erikseen tällä lomakkeella!";

        email_body += f"\n\nEtunimi: {meeting.contact.firstName}"
        email_body += f"\nSukunimi: {meeting.contact.lastName}"
        email_body += f"\nEmail: {meeting.contact.email}"
        email_body += f"\nPuhelinnumero: {meeting.contact.phone}"
        email_body += f"\n\nViesti: {meeting.additionalInformation}"

        message = MessageSchema(
            subject="UUSI AJANVARAUS (Taskusalkun kautta)",
            recipients=os.environ["MAIL_TO"],
            body=email_body,
            subtype="html"
            )

        fm = FastMail(email_conf)
        await fm.send_message(message)
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

            result.append(self.construct_meeting_time(first_available_date, 9, 10))
            result.append(self.construct_meeting_time(first_available_date, 10, 11))
            result.append(self.construct_meeting_time(first_available_date, 11, 12))
            result.append(self.construct_meeting_time(first_available_date, 12, 13))
            result.append(self.construct_meeting_time(first_available_date, 13, 14))
            result.append(self.construct_meeting_time(first_available_date, 14, 15))
            result.append(self.construct_meeting_time(first_available_date, 16, 17))
            result.append(self.construct_meeting_time_from_time(first_available_date, time(hour=16, minute=30), time(hour=17, minute=30)))

            first_available_date += timedelta(days=1)

        return result

    def construct_meeting_time(self, meeting_data: date, start_hour: int, end_hour: int) -> MeetingTime:
        meeting_start_time = datetime.combine(meeting_data, time(hour=start_hour))
        meeting_end_time = datetime.combine(meeting_data, time(hour=end_hour))

        return MeetingTime(startTime=meeting_start_time, endTime=meeting_end_time)

    def construct_meeting_time_from_time(self, meeting_data: date, start_time: time, end_time: time) -> MeetingTime:
        meeting_start_time = datetime.combine(meeting_data, start_time)
        meeting_end_time = datetime.combine(meeting_data, end_time)

        return MeetingTime(startTime=meeting_start_time, endTime=meeting_end_time)
