CREATE DATABASE testDB;
GO

USE testDB;
EXEC sys.sp_cdc_enable_db;

CREATE TABLE RATErah (
  SECID varchar(20) DEFAULT NULL,
  RDATE datetime DEFAULT NULL,
  RCLOSE decimal(16,6) DEFAULT NULL
);

EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'RATErah', @role_name = NULL, @supports_net_changes = 0;
GO