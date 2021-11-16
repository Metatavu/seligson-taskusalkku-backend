# coding: utf-8
from sqlalchemy import BigInteger, CHAR, Column, DECIMAL, Date, DateTime, Integer, String, TIMESTAMP, Table, text
from sqlalchemy.dialects.mysql import BIT, INTEGER, LONGTEXT, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_ADDRESSrah = Table(
    'ADDRESSrah', metadata,
    Column('CON_CODE', String(12)),
    Column('ADDRESS1', String(100)),
    Column('ADDRESS2', String(100)),
    Column('ZIP', String(9)),
    Column('ADDRESS3', String(100)),
    Column('ADDRESS4', String(100)),
    Column('PHONE', String(20)),
    Column('TELEFAX', String(20)),
    Column('TELEX', String(20)),
    Column('DEF_ADDR', CHAR(1), index=True),
    Column('ADDR_NR', Integer, index=True),
    Column('COM_CODE', String(20), index=True),
    Column('EMAIL', String(50)),
    Column('TRADEACCLIMITED', CHAR(1)),
    Column('PHONE2', String(20)),
    Column('CONTACT', String(100)),
    Column('OWNER_TYPE', CHAR(1)),
    Column('ADDRESS_TYPE', String(12)),
    Column('ADDRESS_CODE', Integer),
    Column('MOBILE', String(20)),
    Column('USER_ID', String(30)),
    Column('PORID', String(20), index=True),
    Column('BEGIN_DATE', DateTime),
    Column('END_DATE', DateTime),
    Column('DUAL_USER', String(30)),
    Column('A_COM_CODE', String(20), index=True),
    Column('ACC_CODE', String(20), index=True),
    Column('COM_TYPE', String(2), index=True),
    Column('EXT_SYSTEM_ID', Integer),
    Column('EXT_SYSTEM_UNIQUE_ID', String(50))
)


class Authorization(Base):
    __tablename__ = 'Authorization'

    id = Column(Integer, primary_key=True)
    comCode = Column(Integer, nullable=False, index=True)
    authorizedSSN = Column(String(11), nullable=False, index=True)
    authorizedComCode = Column(Integer, index=True)
    authorizedName = Column(String(120), nullable=False, index=True)
    authorizedFirstName = Column(String(60))
    authorizedLastName = Column(String(60))
    address = Column(String(100))
    zip = Column(String(20))
    city = Column(String(100))
    country = Column(CHAR(2), index=True)
    email = Column(String(100))
    phone = Column(String(100))
    createdTime = Column(DateTime, index=True)
    validity = Column(TINYINT, index=True)
    duration = Column(String(30))
    expires = Column(DateTime, index=True)
    origin = Column(String(30))
    os_deny = Column(TINYINT, index=True)
    external_deny = Column(TINYINT)
    deleteFlag = Column(TINYINT)
    version = Column(String(50), index=True)
    internalGroup = Column(String(50), index=True)
    handledStamp = Column(DateTime, index=True)
    ownedBy = Column(String(50), index=True)
    ownedStamp = Column(DateTime, index=True)
    bankEventID = Column(String(50), index=True)
    bankEventInternalID = Column(String(50))
    bankEventDate = Column(DateTime)
    bankEventSSN = Column(String(20))
    bankEventFirstName = Column(String(60))
    bankEventLastName = Column(String(60))
    hiddenAuth = Column(TINYINT, index=True)
    deleteStamp = Column(DateTime)
    deletedBy = Column(String(30))


t_COMPANYrah = Table(
    'COMPANYrah', metadata,
    Column('COM_CODE', String(20), index=True),
    Column('SHORTNAME', String(50)),
    Column('NAME1', String(255)),
    Column('NAME2', String(255)),
    Column('NAME3', String(255)),
    Column('SO_SEC_NR', String(11)),
    Column('LANGCODE', CHAR(1)),
    Column('CNTRY_CODE', CHAR(3)),
    Column('COM_CLASS', CHAR(2)),
    Column('REMARK', LONGTEXT),
    Column('CREA_DATE', DateTime),
    Column('REF', CHAR(3)),
    Column('NATIONALITY', String(3)),
    Column('FIRST_NAME', String(40)),
    Column('LAST_NAME', String(40)),
    Column('IDENT_METH_ID', Integer)
)


class LoginMobileLog(Base):
    __tablename__ = 'LoginMobileLog'

    ID = Column(Integer, primary_key=True)
    accountName = Column(String(30))
    deviceModel = Column(String(255))
    deviceUuid = Column(String(64))
    deviceVersion = Column(String(64))
    devicePlatform = Column(String(64))
    COMCODE = Column(Integer)
    IP = Column(String(64))
    SUCCES = Column(Integer)
    TIME = Column(TIMESTAMP, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    IPForwarded = Column(String(255))
    deviceBrowser = Column(String(255))
    denyLoginReason = Column(String(255))
    appVersion = Column(String(20))
    RandSet = Column(TINYINT(1))


t_OS_ALERT_STATUS_MOBILE = Table(
    'OS_ALERT_STATUS_MOBILE', metadata,
    Column('STATUS_CODE', Integer),
    Column('TARGET', String(20)),
    Column('FI_message', String(5000)),
    Column('SV_message', String(5000))
)


t_PORTFOLrah = Table(
    'PORTFOLrah', metadata,
    Column('PORID', String(20)),
    Column('COM_CODE', String(20), index=True),
    Column('NAME1', String(255)),
    Column('NAME2', String(255)),
    Column('NAME3', String(255)),
    Column('POR_TYPE', CHAR(2)),
    Column('POR_STATUS', CHAR(2)),
    Column('BDATE', DateTime, index=True),
    Column('EDATE', DateTime, index=True),
    Column('VALUATION', Integer),
    Column('CHARGE', CHAR(2)),
    Column('PASSWORD', String(12)),
    Column('TIMELIMIT', Integer),
    Column('NOTE', String(4000)),
    Column('COMBINED', String(20)),
    Column('TRUSTACC', String(30)),
    Column('BKACCOUNT', String(30)),
    Column('CON_CODE', String(12)),
    Column('OWN_TYPE', CHAR(1)),
    Column('TRUSTACC2', String(30)),
    Column('TRUSTACC3', String(30)),
    Column('LIMITEDUSE', String(1)),
    Column('VALUEDATE', Integer),
    Column('MINFEE', DECIMAL(15, 2)),
    Column('BASICFEE', DECIMAL(15, 2)),
    Column('PCNT_CVAL', DECIMAL(8, 4)),
    Column('TR_PRICE', DECIMAL(12, 2)),
    Column('DRV_PRICE', DECIMAL(12, 2)),
    Column('SEC_PRICE', DECIMAL(12, 2)),
    Column('PHYS_PRICE', DECIMAL(12, 2)),
    Column('FORE_PRICE', DECIMAL(12, 2)),
    Column('FEEGROUP', CHAR(1)),
    Column('REG1_PRICE', DECIMAL(12, 2)),
    Column('REG2_PRICE', DECIMAL(12, 2)),
    Column('LIMIT_IND', String(15)),
    Column('CMPR_IND', String(20)),
    Column('PERIOD', DateTime),
    Column('NXTVOUCHER', Integer),
    Column('INV_GRP', Integer),
    Column('TRADEACCLIMITED', CHAR(1)),
    Column('PAWN_CODE', String(10))
)


t_PORTLOGrah = Table(
    'PORTLOGrah', metadata,
    Column('TRANS_NR', Integer, index=True),
    Column('PREV_NR', Integer, index=True),
    Column('ACT_NR', Integer, index=True),
    Column('TRANS_CODE', CHAR(2), index=True),
    Column('COM_CODE', String(20), index=True),
    Column('CCOM_CODE', String(20), index=True),
    Column('PORID', String(20), index=True),
    Column('CPORID', String(20)),
    Column('SEC_TYPE', CHAR(2), index=True),
    Column('SECID', String(20), index=True),
    Column('CSECID', String(20), index=True),
    Column('ISSUE', Integer, index=True),
    Column('OISSUE', Integer),
    Column('BROKID', String(20)),
    Column('TRUSTID', String(50)),
    Column('TRUST_NMBR', Integer),
    Column('TRANS_DATE', DateTime, index=True),
    Column('PMT_DATE', DateTime),
    Column('ORDER_VAL', DateTime),
    Column('ORDER_TIME', String(8)),
    Column('CURRENCY1', CHAR(3)),
    Column('AMOUNT', DECIMAL(19, 6)),
    Column('PRICE', DECIMAL(16, 6)),
    Column('EXPENSES', DECIMAL(15, 2)),
    Column('VALUE', DECIMAL(15, 2)),
    Column('SPURVALUE2', DECIMAL(15, 2)),
    Column('FEE', DECIMAL(15, 2)),
    Column('PROVISION', DECIMAL(15, 2)),
    Column('TAX', DECIMAL(15, 2)),
    Column('OWN_TAX', DECIMAL(15, 2)),
    Column('EMISSION', DECIMAL(15, 2)),
    Column('TOT_EXP', DECIMAL(15, 2)),
    Column('ROUNDING', DECIMAL(15, 2)),
    Column('CURRENCY2', CHAR(3)),
    Column('CUR_RATE', DECIMAL(16, 6)),
    Column('SPROFIT', DECIMAL(15, 2)),
    Column('BDATE', DateTime),
    Column('EDATE', DateTime),
    Column('VOUCHER', Integer),
    Column('PAWN_CODE', String(10)),
    Column('PAWN_AM', DECIMAL(19, 6)),
    Column('SPL_RATIO', DECIMAL(15, 9)),
    Column('SPL_RATIO2', DECIMAL(15, 9)),
    Column('SPL_DATE', DateTime),
    Column('DIV_AMNT', DECIMAL(15, 2)),
    Column('DIV_DATE', DateTime),
    Column('PRELIMTAX', DECIMAL(15, 2)),
    Column('POFF_DATE', DateTime),
    Column('POFF_PRICE', DECIMAL(16, 6)),
    Column('POFF_VALUE', DECIMAL(15, 2)),
    Column('ISS_PRINT', DateTime),
    Column('TEMP_NR', String(30)),
    Column('TRLEVEL', CHAR(1)),
    Column('ACCOUNT', String(35)),
    Column('CAN_NMBR', Integer),
    Column('PREV_CODE', CHAR(2)),
    Column('CURRENCY', CHAR(3)),
    Column('CUR_RATE2', DECIMAL(16, 6)),
    Column('PRINTED', Integer),
    Column('NOTE', String(255)),
    Column('STATUS', CHAR(1), index=True),
    Column('CURR_CODE', Integer),
    Column('EFF_YIELD', DECIMAL(16, 6)),
    Column('INT_PERIOD', Integer),
    Column('TAX_CODE', Integer),
    Column('SCAP_DIFF', DECIMAL(15, 2)),
    Column('INTEREST', DECIMAL(12, 6)),
    Column('TAX_PCNT', DECIMAL(8, 4)),
    Column('STAMP_DUTY', DECIMAL(15, 2)),
    Column('UPD_USER', String(30)),
    Column('UPD_DATE', DateTime),
    Column('UPD_TIME', String(8)),
    Column('ORIG_NMBR', Integer),
    Column('CLEAR_CODE', CHAR(10)),
    Column('CLEAR_DATE', DateTime),
    Column('CLEAR_STAT', CHAR(1)),
    Column('BE_ACCOUNT', String(20)),
    Column('EXT_NR', String(250), index=True),
    Column('CAGIO', DECIMAL(15, 2)),
    Column('SBK_RETURN', DECIMAL(15, 2)),
    Column('EXT_NAME', String(10)),
    Column('EXT_CODE', String(15)),
    Column('ISIN', String(12)),
    Column('SETTLSTAT', String(4)),
    Column('DEALTYPE', CHAR(2)),
    Column('TR_STATUS', CHAR(2)),
    Column('ERRORCODE', String(5)),
    Column('SWIFT_ADDR', String(15)),
    Column('EXT_TYPE', String(10)),
    Column('KATIREF', String(18), index=True),
    Column('FREECODE', CHAR(5)),
    Column('TOT_VALUE', DECIMAL(15, 2)),
    Column('DATE1', DateTime),
    Column('DATE2', DateTime),
    Column('VALUE1', DECIMAL(15, 2)),
    Column('VALUE2', DECIMAL(15, 2)),
    Column('VALUE3', DECIMAL(10, 6)),
    Column('VALUE4', DECIMAL(10, 6)),
    Column('CODE1', Integer),
    Column('CODE2', Integer),
    Column('CODE3', CHAR(2)),
    Column('CODE4', String(12)),
    Column('CODE5', String(30)),
    Column('PMT_TRANS', CHAR(1)),
    Column('PMTERROR', String(16)),
    Column('BENOFSECA', String(12)),
    Column('BENOFSECD', String(35)),
    Column('SHORTCODE', CHAR(1)),
    Column('STATCODE', String(10)),
    Column('CPROFIT', DECIMAL(15, 2)),
    Column('AVG_RATE', DECIMAL(16, 6)),
    Column('FILTERSTAT', String(255)),
    Column('CUR_RATE1', DECIMAL(16, 6)),
    Column('CAMOUNT', DECIMAL(19, 6)),
    Column('SAMOUNT', DECIMAL(19, 6)),
    Column('CPRICE', DECIMAL(16, 6)),
    Column('SPRICE', DECIMAL(16, 6)),
    Column('CEXPENSES', DECIMAL(15, 2)),
    Column('SEXPENSES', DECIMAL(15, 2)),
    Column('CVALUE', DECIMAL(15, 2)),
    Column('SVALUE', DECIMAL(15, 2)),
    Column('CPURVALUE2', DECIMAL(15, 2)),
    Column('CFEE', DECIMAL(15, 2)),
    Column('SFEE', DECIMAL(15, 2)),
    Column('CPROVISION', DECIMAL(15, 2)),
    Column('SPROVISION', DECIMAL(15, 2)),
    Column('CTAX', DECIMAL(15, 2)),
    Column('STAX', DECIMAL(15, 2)),
    Column('COWN_TAX', DECIMAL(15, 2)),
    Column('SOWN_TAX', DECIMAL(15, 2)),
    Column('CEMISSION', DECIMAL(15, 2)),
    Column('SEMISSION', DECIMAL(15, 2)),
    Column('CTOT_EXP', DECIMAL(15, 2)),
    Column('STOT_EXP', DECIMAL(15, 2)),
    Column('CROUNDING', DECIMAL(15, 2)),
    Column('SROUNDING', DECIMAL(15, 2)),
    Column('CDIV_AMNT', DECIMAL(15, 2)),
    Column('SDIV_AMNT', DECIMAL(15, 2)),
    Column('CPRELIMTAX', DECIMAL(15, 2)),
    Column('SPRELIMTAX', DECIMAL(15, 2)),
    Column('CSTAMPDUTY', DECIMAL(15, 2)),
    Column('SSTAMPDUTY', DECIMAL(15, 2)),
    Column('CTOT_VALUE', DECIMAL(15, 2)),
    Column('STOT_VALUE', DECIMAL(15, 2)),
    Column('SVALUE1', DECIMAL(15, 2)),
    Column('CVALUE1', DECIMAL(15, 2)),
    Column('SVALUE2', DECIMAL(15, 2)),
    Column('CVALUE2', DECIMAL(15, 2)),
    Column('OWN_DATE', DateTime),
    Column('CCAP_DIFF', DECIMAL(15, 2)),
    Column('CBK_RETURN', DECIMAL(15, 2)),
    Column('UNIT', String(20)),
    Column('ACT_CODE', Integer),
    Column('PAWN_CURR', CHAR(3)),
    Column('DIV_BIT', Integer),
    Column('ACC_CODE', String(20)),
    Column('BORROWED', Integer),
    Column('PAID', Integer),
    Column('SETTLAMNT', DECIMAL(19, 6)),
    Column('T_ENTRYDATE', DateTime),
    Column('P_ENTRYDATE', DateTime)
)


t_PORTRANSrah = Table(
    'PORTRANSrah', metadata,
    Column('TRANS_NR', Integer),
    Column('COM_CODE', String(20), index=True),
    Column('PORID', String(20), index=True),
    Column('SECID', String(20), index=True),
    Column('TRANS_DATE', DateTime),
    Column('VAL_END', DateTime),
    Column('PMT_DATE', DateTime),
    Column('AVG_DATE', DateTime, index=True),
    Column('AMOUNT', DECIMAL(19, 6)),
    Column('PUR_VALUE', DECIMAL(15, 2)),
    Column('PUR_PRICE', DECIMAL(16, 6)),
    Column('PAWN_CODE', String(10)),
    Column('PUR_CVALUE', DECIMAL(15, 2)),
    Column('PAWN_AM', DECIMAL(19, 6)),
    Column('OWN_BEGIN', DateTime),
    Column('OWN_END', DateTime),
    Column('PUR_CPRICE', DECIMAL(16, 6))
)


t_RATELASTrah = Table(
    'RATELASTrah', metadata,
    Column('SECID', String(20), index=True),
    Column('RDATE', DateTime, index=True),
    Column('RCLOSE', DECIMAL(16, 6))
)


t_SECURITYrah = Table(
    'SECURITYrah', metadata,
    Column('SECID', String(20), index=True),
    Column('NAME1', String(255)),
    Column('NAME2', String(255)),
    Column('NAME3', String(255)),
    Column('CURRENCY', CHAR(3)),
    Column('PE_CORR', DECIMAL(8, 4)),
    Column('ISIN', String(12))
)


class RATErah(Base):
    __tablename__ = 'RATErah'

    SECID = Column(String(20), primary_key=True)
    RDATE = Column(DateTime, primary_key=True)
    RCLOSE = Column(DECIMAL(16, 6))


class UserAccount(Base):
    __tablename__ = 'UserAccount'

    id = Column(Integer, primary_key=True)
    userName = Column(String(48), nullable=False, unique=True)
    hash = Column(String(48), nullable=False)
    random = Column(CHAR(22))
    comCode = Column(Integer, nullable=False, unique=True)
    __contractID = Column(Integer, unique=True)
    disabled = Column(BIT(1), nullable=False)
    readOnly = Column(BIT(1), nullable=False)
    notificationEnabled = Column(BIT(1), nullable=False)
    contractUpdateOverride = Column(BIT(1), nullable=False)
    lastPasswordChange = Column(DateTime)
    notificationEmail = Column(String(64))
    lastRedemptionExitPollResponse = Column(DateTime)
    portfolioCreateEnabled = Column(TINYINT, server_default=text("'0'"))
    contractUpdateDate = Column(DateTime, index=True)
    bankAccountChangeDisabled = Column(BIT(1))
    bankIdRedemptionValidation = Column(String(10))
    accountStatus = Column(TINYINT, index=True)
    notificationEnabledMobile = Column(BIT(1))
    traditionalLoginDisabled = Column(TINYINT)


class UserAccountSharedAcces(Base):
    __tablename__ = 'UserAccountSharedAccess'

    grantAccess = Column(Integer, primary_key=True, nullable=False, index=True)
    comCode = Column(Integer, primary_key=True, nullable=False, index=True)
    expires = Column(Date)
    readOnly = Column(TINYINT, server_default=text("'0'"))


class UserAccountSharedAccessLog(Base):
    __tablename__ = 'UserAccountSharedAccessLog'

    id = Column(INTEGER, primary_key=True)
    comCode = Column(Integer, nullable=False)
    name = Column(String(256))
    accessedComCode = Column(Integer, nullable=False)
    readOnly = Column(BigInteger)
    mobileApp = Column(TINYINT(1))
    time = Column(DateTime, nullable=False)


t_disableMobileDevice = Table(
    'disableMobileDevice', metadata,
    Column('deviceUuid', String(50)),
    Column('comCode', String(20)),
    Column('disabled', String(5)),
    Column('date', TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
)


t_lastReplicationDate = Table(
    'lastReplicationDate', metadata,
    Column('ID', Integer),
    Column('lastUpdateDate', String(20))
)


class MobileSession(Base):
    __tablename__ = 'mobileSession'

    id = Column(INTEGER, primary_key=True)
    comCode = Column(String(20))
    sessionKey = Column(String(20))
    timeStamp = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
