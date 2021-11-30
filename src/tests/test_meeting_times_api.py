from csv import reader
from starlette.testclient import TestClient
import datetime
from .fixtures.client import *  # noqa
from .auth.auth import BearerAuth
from .fixtures.users import *  # noqa

class TestMeetingTimes:
    """Tests for meeting times endpoints"""

    def test_find_meeting_times(self, client: TestClient, user_1_auth: BearerAuth):
        today = datetime.date.today()
        with open(os.environ["HOLIDAYS_CSV"]) as csv_file:
            rows = reader(csv_file, delimiter=",")
            row1 = next(rows)
            holidays = row1

        start_date = today
        while start_date.weekday() >= 6 or str(start_date) in holidays:
            start_date += datetime.timedelta(days=1)

        end_date = start_date + datetime.timedelta(days=1)
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

        # start date is earlier than end date, 400
        start_date = today + datetime.timedelta(days=-2)
        end_date = today + datetime.timedelta(days=1)
        response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                              auth=user_1_auth)
        assert response.status_code == 400
