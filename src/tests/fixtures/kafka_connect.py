import json
import requests

from typing import Dict
from testcontainers.core.waiting_utils import wait_for_logs
from ..testcontainers.kafka_connect import KafkaConnectContainer
from ..testcontainers.mssql import SqlServerContainer
from ..fixtures.kafka import *
from ..fixtures.salkku_mysql import *

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
logger = logging.getLogger(__name__)
extra_libs = [
            "https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.34/mysql-connector-java-5.1.34.jar",
            "https://packages.confluent.io/maven/io/confluent/kafka-connect-jdbc/10.2.5/kafka-connect-jdbc-10.2.5.jar"
           ]


@pytest.fixture(scope="session")
def kafka_connect(request, salkku_mysql: MySqlContainer, funds_mssql: SqlServerContainer, kafka: KafkaContainer):
    """Kafka Connect fixture

    Args:
        request (FixtureRequest): A fixture request object
        salkku_mysql (MySqlContainer): Salkku DB container
        funds_mssql (SqlServerContainer): Funds DB container
        kafka (KafkaContainer): Kafka container

    Returns:
        KafkaConnectContainer: Reference to Kafka Connect container
    """
    kafka_connect = KafkaConnectContainer(kafkaIp=kafka.get_kafka_ip(), BOOTSTRAP_SERVERS=kafka.get_kafka_url())
    kafka_connect.start()

    for extra_lib in extra_libs:
        download_command = f'bash -c "cd /kafka/libs && curl -sO {extra_lib}"'
        download_result = kafka_connect.exec(download_command)
        assert download_result.exit_code == 0

    def teardown():
        """Stops the containers after session"""
        kafka_connect.stop()

    def get_salkku_connector() -> Dict:
        with open(f"{data_dir}/salkku-kafka-connector.json") as json_file:
            db_container_id = salkku_mysql._container.id
            result: Dict = json.load(json_file)
            result["config"]["database.hostname"] = salkku_mysql.get_docker_client().bridge_ip(db_container_id)
            result["config"]["database.port"] = 3306
            result["config"]["database.user"] = "root"
            result["config"]["database.password"] = "test"  # NOSONAR
            result["config"]["database.history.kafka.bootstrap.servers"] = kafka.get_kafka_url()
            return result

    def get_funds_connector() -> Dict:
        with open(f"{data_dir}/funds-kafka-connector.json") as json_file:
            db_container_id = funds_mssql._container.id
            result: Dict = json.load(json_file)
            result["config"]["database.hostname"] = funds_mssql.get_docker_client().bridge_ip(db_container_id)
            result["config"]["database.port"] = 1433
            result["config"]["database.user"] = "sa"
            result["config"]["database.password"] = "Test1234."  # NOSONAR
            result["config"]["database.history.kafka.bootstrap.servers"] = kafka.get_kafka_url()
            return result

    def add_connector(connector: Dict):
        connectors_url = f"{kafka_connect.get_kafka_connect_url()}/connectors/"
        response = requests.post(connectors_url, json=connector)
        if response.status_code != 201:
            import pdb
            pdb.set_trace()
        assert response.status_code == 201

    request.addfinalizer(teardown)

    add_connector(get_salkku_connector())
    add_connector(get_funds_connector())

    wait_for_logs(kafka_connect, "Connected to MySQL binlog")

    return kafka_connect
