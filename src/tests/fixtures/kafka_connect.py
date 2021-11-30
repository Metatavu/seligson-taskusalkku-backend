from typing import Dict
import pytest
import json
import logging
import os
import requests

from testcontainers.mysql import MySqlContainer

from testcontainers.core.waiting_utils import wait_for_logs
from ..testcontainers.kafka_connect import KafkaConnectContainer
from ..testcontainers.kafka import KafkaContainer

from ..fixtures.kafka import *
from ..fixtures.salkku_mysql import *

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
logger = logging.getLogger(__name__)
extra_libs = [
            "https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.34/mysql-connector-java-5.1.34.jar",
            "https://packages.confluent.io/maven/io/confluent/kafka-connect-jdbc/10.2.5/kafka-connect-jdbc-10.2.5.jar"
           ]


@pytest.fixture(scope="session")
def kafka_connect(request, salkku_mysql: MySqlContainer, kafka: KafkaContainer):
    """Kafka Connect fixture

    Args:
        request (FixtureRequest): A fixture request object

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
        """Stops the containers after session
        """
        kafka_connect.stop()

    def get_main_mysql_connector():
        with open(f"{data_dir}/test-kafka-connector.json") as json_file:
            result: Dict = json.load(json_file)
            result["config"]["database.hostname"] = salkku_mysql.get_docker_client().bridge_ip(salkku_mysql._container.id)
            result["config"]["database.port"] = 3306
            result["config"]["database.user"] = "root"
            result["config"]["database.password"] = "test"
            result["config"]["database.history.kafka.bootstrap.servers"] = kafka.get_kafka_url()
            return result

    request.addfinalizer(teardown)

    main_mysql_connector = get_main_mysql_connector()
    connectors_url = f"{kafka_connect.get_kafka_connect_url()}/connectors/"
    response = requests.post(connectors_url, json=main_mysql_connector)
    assert response.status_code == 201

    wait_for_logs(kafka_connect, "Connected to MySQL binlog")

    return kafka_connect