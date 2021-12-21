from csv import reader
import datetime
from typing import Optional, Any

from .constants import invalid_auths
from .fixtures.client import *  # noqa
from .auth.auth import BearerAuth  # noqa
from .fixtures.users import *  # noqa
from .fixtures.smtp import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from .fixtures.client import *  # noqa

import json


class TestMeeting:
    """Tests for meeting endpoints"""

    def setup_method(self):
        self.example_meeting = {
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

    def test_create_meeting(self, client: TestClient, user_1_auth: BearerAuth, smtp: SmtpContainer):
        response = client.post(f"/v1/meetings", auth=user_1_auth, data=json.dumps(self.example_meeting))
        assert response.status_code == 200
        assert self.example_meeting == response.json()

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_create_meeting_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                         keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_create_meeting_fail(
            client=client,
            expected_status=403,
            auth=auth,
            payload=self.example_meeting
        )

    def test_create_meeting_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                      keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        response = client.post(f"/v1/meetings", auth=anonymous_auth, data=json.dumps(self.example_meeting))
        assert response.status_code == 200
        assert self.example_meeting == response.json()

    def test_create_meeting_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                         keycloak: KeycloakContainer):
        self.assert_create_meeting_fail(
            client=client,
            expected_status=403,
            auth=None,
            payload=self.example_meeting
        )

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

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_meeting_times_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                             keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_meeting_times_fail(
            client=client,
            expected_status=403,
            auth=auth
        )

    def test_list_meeting_times_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)
        response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                              auth=anonymous_auth)
        assert response.status_code == 200

    def test_list_meeting_times_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                             keycloak: KeycloakContainer):
        self.assert_list_meeting_times_fail(
            client=client,
            expected_status=403,
            auth=None
        )

    @staticmethod
    def assert_create_meeting_fail(client: TestClient, expected_status: int, payload: Any, auth: Optional[BearerAuth]):
        if auth is None:
            response = client.post(f"/v1/meetings", auth=auth, data=json.dumps(payload))
        else:
            response = client.post(f"/v1/meetings", data=json.dumps(payload))

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_meeting_times_fail(client: TestClient, expected_status: int, auth: Optional[BearerAuth]):
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)

        if auth is None:
            response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}")
        else:
            response = client.get(f"/v1/meetingTimes/?startDate={str(start_date)}&endDate={str(end_date)}",
                                  auth=auth)

        assert expected_status == response.status_code
