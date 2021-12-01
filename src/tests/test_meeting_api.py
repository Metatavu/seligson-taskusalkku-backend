from csv import reader
from starlette.testclient import TestClient
import datetime
from .fixtures.client import *  # noqa
from .auth.auth import BearerAuth  # noqa
from .fixtures.users import *  # noqa
from .fixtures.smtp import *  # noqa
import json

class TestMeeting:
    """Tests for meeting endpoints"""

    def test_create_meeting(self, client: TestClient, user_1_auth: BearerAuth, smtp: SmtpContainer):
        meeting = {
            "type": "MEETING",
            "time": "2021-12-01T13:11:24.565341",
            "language": "fi",
            "participantCount": 1,
            "additionalInformation": "additional info",
            "contact": {
                "firstName": "tommi",
                "lastName": "tommi",
                "email": "tommi@example.fi",
                "phone": "00000",
            }
        }
        response = client.post(f"/v1/meetings", auth=user_1_auth, data=json.dumps(meeting))

        assert response.status_code == 200

    def test_find_meeting_times(self, client: TestClient, user_1_auth: BearerAuth):
        today = datetime.date.today()
        with open(os.environ["HOLIDAYS_CSV"]) as csv_file:
            rows = reader(csv_file, delimiter=",")
            row1 = next(rows)
            holidays = row1

        start_date = today
        while start_date.weekday() >= 6 or str(start_date) in holidays:
            start_date += datetime.timedelta(days=1)

        end_date = start_date + datetime.timedelta(days=30)
        response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                              auth=user_1_auth)

        assert response.status_code == 200
        result = response.json()
        assert len(result) != 0

    def test_find_meeting_times_invalid_range(self, client: TestClient, user_1_auth: BearerAuth):
        today = datetime.date.today()

        # start date is earlier than end date, 400
        start_date = today + datetime.timedelta(days=2)
        end_date = today + datetime.timedelta(days=1)
        response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                              auth=user_1_auth)
        assert response.status_code == 400

    def test_find_meeting_times_past(self, client: TestClient, user_1_auth: BearerAuth):
        today = datetime.date.today()

        # start date or end date in the past, 400
        start_date = today + datetime.timedelta(days=-2)
        end_date = today + datetime.timedelta(days=1)
        response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                              auth=user_1_auth)
        assert response.status_code == 400

    def test_find_meeting_times_holiday(self, client: TestClient, user_1_auth: BearerAuth):
        response = client.get("/v1/meetingTimes/?startDate=2024-01-01&endDate=2024-01-01",
                              auth=user_1_auth)
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0
