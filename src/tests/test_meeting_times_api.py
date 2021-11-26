from csv import reader
from starlette.testclient import TestClient
import datetime

from .fixtures.client import *  # noqa


class TestMeetingTimes:
    """Tests for meeting times endpoints"""

    def test_find_meeting_times(self, client: TestClient):
        now_datetime = datetime.datetime.now()
        with open(os.environ["HOLIDAYS_CSV"]) as csv_file:
            rows = reader(csv_file, delimiter=",")
            row1 = next(rows)
            holidays = row1

        # if the start, end date span more than one day, 400
        start_date = now_datetime.replace(hour=11) + datetime.timedelta(days=1)
        end_date = now_datetime.replace(hour=12) + datetime.timedelta(days=2)
        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 400

        # start datetime is earlier than end datetime, 400
        start_date = now_datetime.replace(hour=11) + datetime.timedelta(days=1)
        end_date = now_datetime.replace(hour=10) + datetime.timedelta(days=1)
        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 400

        # date in holiday day array, 400
        for date_string in holidays:
            parsed_date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            if parsed_date > now_datetime:
                start_date = parsed_date.replace(hour=10)
                end_date = parsed_date.replace(hour=11)
                break

        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 400

        # date in the weekend (next Monday), 400
        start_date = now_datetime.replace(hour=11) + datetime.timedelta(days=7 - now_datetime.weekday())
        end_date = now_datetime.replace(hour=12) + datetime.timedelta(days=7 - now_datetime.weekday())
        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 400

        # datetime is in the past, 400
        start_date = now_datetime.replace(hour=11) + datetime.timedelta(days=-1)
        end_date = now_datetime.replace(hour=12) + datetime.timedelta(days=-1)
        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 400

        # check successful request, 200
        start_date = now_datetime.replace(hour=11) + datetime.timedelta(days=1)

        while start_date.strftime("%Y-%m-%d") in holidays or start_date.weekday() in [6, 7]:
            start_date + datetime.timedelta(days=1)
        end_date = start_date.replace(hour=12)
        response = client.get("/v1/meetingTimes", startDate=start_date, endDate=end_date)
        assert response.status_code == 200
