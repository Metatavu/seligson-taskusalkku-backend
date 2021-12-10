import time

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.mssql import SqlServerContainer as SqlServerContainerBase


class SqlServerContainer(SqlServerContainerBase):

    def _connect(self):
        wait_for_logs(self, r'SQL Server is now ready for client connections', timeout=60)
        time.sleep(10)

    def _configure(self):
        self.with_env("MSSQL_AGENT_ENABLED", "true")
        super()._configure()
