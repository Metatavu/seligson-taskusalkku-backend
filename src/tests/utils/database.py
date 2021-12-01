import logging

from testcontainers.mysql import MySqlContainer

logger = logging.getLogger(__name__)
container_import_folder = "/tmp/import"  # NOSONAR


def mysql_import_sql(mysql: MySqlContainer, sql_import_file: str):
    """Import SQL file into test database

    Args:
        mysql (MySqlContainer): database container
        sql_import_file (str): file
    """
    logger.info(f"Importing SQL file {sql_import_file}...")
    import_command = f'bash -c "mysql -uroot -ptest test < {container_import_folder}/{sql_import_file}"'
    import_result = mysql.exec(import_command)
    if import_result.exit_code != 0:
        logger.error(import_result.output.decode("utf-8"))

    assert import_result.exit_code == 0