CREATE DATABASE testDB;
GO

USE testDB;
EXEC sys.sp_cdc_enable_db;

CREATE TABLE TABLE_RATE (
  MARKCODE varchar(4),
  SECID varchar(20) not null,
  RDATE datetime not null,
  BID decimal(18,16),
  ASK decimal(18,16),
  LOW decimal(18,16),
  HIGH decimal(18,16),
  RCLOSE decimal(18,16),
  MID decimal(18,16),
  VOL decimal(17,15),
  RINDEX decimal(18,16),
  SNAPSHOT varchar(5) not null,
  UPDATE_STAMP timestamp not null,
  UPD_DATE datetime,
  TIS decimal(18,16)
);

EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'TABLE_RATE', @role_name = NULL, @supports_net_changes = 0;
GO