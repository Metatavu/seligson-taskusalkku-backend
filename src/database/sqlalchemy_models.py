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


class COMPANYrah(Base):
    __tablename__ = 'COMPANYrah'

    COM_CODE = Column(String(20), index=True, primary_key=True)
    SHORTNAME = Column(String(50))
    NAME1 = Column(String(255))
    NAME2 = Column(String(255))
    NAME3 = Column(String(255))
    SO_SEC_NR = Column(String(11))
    LANGCODE = Column(CHAR(1))
    CNTRY_CODE = Column(CHAR(3))
    COM_CLASS = Column(CHAR(2))
    REMARK = Column(LONGTEXT)
    CREA_DATE = Column(DateTime)
    REF = Column(CHAR(3))
    NATIONALITY = Column(String(3))
    FIRST_NAME = Column(String(40))
    LAST_NAME = Column(String(40))
    IDENT_METH_ID = Column(Integer)


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


class PORTFOLrah(Base):
    __tablename__ = 'PORTFOLrah'

    PORID = Column(String(20), primary_key=True)
    COM_CODE = Column(String(20), index=True)
    NAME1 = Column(String(255))
    NAME2 = Column(String(255))
    NAME3 = Column(String(255))
    POR_TYPE = Column(CHAR(2))
    POR_STATUS = Column(CHAR(2))
    BDATE = Column(DateTime, index=True)
    EDATE = Column(DateTime, index=True)
    VALUATION = Column(Integer)
    CHARGE = Column(CHAR(2))
    PASSWORD = Column(String(12))
    TIMELIMIT = Column(Integer)
    NOTE = Column(String(4000))
    COMBINED = Column(String(20))
    TRUSTACC = Column(String(30))
    BKACCOUNT = Column(String(30))
    CON_CODE = Column(String(12))
    OWN_TYPE = Column(CHAR(1))
    TRUSTACC2 = Column(String(30))
    TRUSTACC3 = Column(String(30))
    LIMITEDUSE = Column(String(1))
    VALUEDATE = Column(Integer)
    MINFEE = Column(DECIMAL(15, 2))
    BASICFEE = Column(DECIMAL(15, 2))
    PCNT_CVAL = Column(DECIMAL(8, 4))
    TR_PRICE = Column(DECIMAL(12, 2))
    DRV_PRICE = Column(DECIMAL(12, 2))
    SEC_PRICE = Column(DECIMAL(12, 2))
    PHYS_PRICE = Column(DECIMAL(12, 2))
    FORE_PRICE = Column(DECIMAL(12, 2))
    FEEGROUP = Column(CHAR(1))
    REG1_PRICE = Column(DECIMAL(12, 2))
    REG2_PRICE = Column(DECIMAL(12, 2))
    LIMIT_IND = Column(String(15))
    CMPR_IND = Column(String(20))
    PERIOD = Column(DateTime)
    NXTVOUCHER = Column(Integer)
    INV_GRP = Column(Integer)
    TRADEACCLIMITED = Column(CHAR(1))
    PAWN_CODE = Column(String(10))


class PORTLOGrah(Base):
    __tablename__ = 'PORTLOGrah'

    TRANS_NR = Column( Integer, index=True, primary_key=True)
    PREV_NR = Column( Integer, index=True)
    ACT_NR = Column( Integer, index=True)
    TRANS_CODE = Column( CHAR(2), index=True)
    COM_CODE = Column( String(20), index=True)
    CCOM_CODE = Column( String(20), index=True)
    PORID = Column( String(20), index=True)
    CPORID = Column( String(20))
    SEC_TYPE = Column( CHAR(2), index=True)
    SECID = Column( String(20), index=True)
    CSECID = Column( String(20), index=True)
    ISSUE = Column( Integer, index=True)
    OISSUE = Column( Integer)
    BROKID = Column( String(20))
    TRUSTID = Column( String(50))
    TRUST_NMBR = Column( Integer)
    TRANS_DATE = Column( DateTime, index=True)
    PMT_DATE = Column( DateTime)
    ORDER_VAL = Column( DateTime)
    ORDER_TIME = Column( String(8))
    CURRENCY1 = Column( CHAR(3))
    AMOUNT = Column( DECIMAL(19, 6))
    PRICE = Column( DECIMAL(16, 6))
    EXPENSES = Column( DECIMAL(15, 2))
    VALUE = Column( DECIMAL(15, 2))
    SPURVALUE2 = Column( DECIMAL(15, 2))
    FEE = Column( DECIMAL(15, 2))
    PROVISION = Column( DECIMAL(15, 2))
    TAX = Column( DECIMAL(15, 2))
    OWN_TAX = Column( DECIMAL(15, 2))
    EMISSION = Column( DECIMAL(15, 2))
    TOT_EXP = Column( DECIMAL(15, 2))
    ROUNDING = Column( DECIMAL(15, 2))
    CURRENCY2 = Column( CHAR(3))
    CUR_RATE = Column( DECIMAL(16, 6))
    SPROFIT = Column( DECIMAL(15, 2))
    BDATE = Column( DateTime)
    EDATE = Column( DateTime)
    VOUCHER = Column( Integer)
    PAWN_CODE = Column( String(10))
    PAWN_AM = Column( DECIMAL(19, 6))
    SPL_RATIO = Column( DECIMAL(15, 9))
    SPL_RATIO2 = Column( DECIMAL(15, 9))
    SPL_DATE = Column( DateTime)
    DIV_AMNT = Column( DECIMAL(15, 2))
    DIV_DATE = Column( DateTime)
    PRELIMTAX = Column( DECIMAL(15, 2))
    POFF_DATE = Column( DateTime)
    POFF_PRICE = Column( DECIMAL(16, 6))
    POFF_VALUE = Column( DECIMAL(15, 2))
    ISS_PRINT = Column( DateTime)
    TEMP_NR = Column( String(30))
    TRLEVEL = Column( CHAR(1))
    ACCOUNT = Column( String(35))
    CAN_NMBR = Column( Integer)
    PREV_CODE = Column( CHAR(2))
    CURRENCY = Column( CHAR(3))
    CUR_RATE2 = Column( DECIMAL(16, 6))
    PRINTED = Column( Integer)
    NOTE = Column( String(255))
    STATUS = Column( CHAR(1), index=True)
    CURR_CODE = Column( Integer)
    EFF_YIELD = Column( DECIMAL(16, 6))
    INT_PERIOD = Column( Integer)
    TAX_CODE = Column( Integer)
    SCAP_DIFF = Column( DECIMAL(15, 2))
    INTEREST = Column( DECIMAL(12, 6))
    TAX_PCNT = Column( DECIMAL(8, 4))
    STAMP_DUTY = Column( DECIMAL(15, 2))
    UPD_USER = Column( String(30))
    UPD_DATE = Column( DateTime)
    UPD_TIME = Column( String(8))
    ORIG_NMBR = Column( Integer)
    CLEAR_CODE = Column( CHAR(10))
    CLEAR_DATE = Column( DateTime)
    CLEAR_STAT = Column( CHAR(1))
    BE_ACCOUNT = Column( String(20))
    EXT_NR = Column( String(250), index=True)
    CAGIO = Column( DECIMAL(15, 2))
    SBK_RETURN = Column( DECIMAL(15, 2))
    EXT_NAME = Column( String(10))
    EXT_CODE = Column( String(15))
    ISIN = Column( String(12))
    SETTLSTAT = Column( String(4))
    DEALTYPE = Column( CHAR(2))
    TR_STATUS = Column( CHAR(2))
    ERRORCODE = Column( String(5))
    SWIFT_ADDR = Column( String(15))
    EXT_TYPE = Column( String(10))
    KATIREF = Column( String(18), index=True)
    FREECODE = Column( CHAR(5))
    TOT_VALUE = Column( DECIMAL(15, 2))
    DATE1 = Column( DateTime)
    DATE2 = Column( DateTime)
    VALUE1 = Column( DECIMAL(15, 2))
    VALUE2 = Column( DECIMAL(15, 2))
    VALUE3 = Column( DECIMAL(10, 6))
    VALUE4 = Column( DECIMAL(10, 6))
    CODE1 = Column( Integer)
    CODE2 = Column( Integer)
    CODE3 = Column( CHAR(2))
    CODE4 = Column( String(12))
    CODE5 = Column( String(30))
    PMT_TRANS = Column( CHAR(1))
    PMTERROR = Column( String(16))
    BENOFSECA = Column( String(12))
    BENOFSECD = Column( String(35))
    SHORTCODE = Column( CHAR(1))
    STATCODE = Column( String(10))
    CPROFIT = Column( DECIMAL(15, 2))
    AVG_RATE = Column( DECIMAL(16, 6))
    FILTERSTAT = Column( String(255))
    CUR_RATE1 = Column( DECIMAL(16, 6))
    CAMOUNT = Column( DECIMAL(19, 6))
    SAMOUNT = Column( DECIMAL(19, 6))
    CPRICE = Column( DECIMAL(16, 6))
    SPRICE = Column( DECIMAL(16, 6))
    CEXPENSES = Column( DECIMAL(15, 2))
    SEXPENSES = Column( DECIMAL(15, 2))
    CVALUE = Column( DECIMAL(15, 2))
    SVALUE = Column( DECIMAL(15, 2))
    CPURVALUE2 = Column( DECIMAL(15, 2))
    CFEE = Column( DECIMAL(15, 2))
    SFEE = Column( DECIMAL(15, 2))
    CPROVISION = Column( DECIMAL(15, 2))
    SPROVISION = Column( DECIMAL(15, 2))
    CTAX = Column( DECIMAL(15, 2))
    STAX = Column( DECIMAL(15, 2))
    COWN_TAX = Column( DECIMAL(15, 2))
    SOWN_TAX = Column( DECIMAL(15, 2))
    CEMISSION = Column( DECIMAL(15, 2))
    SEMISSION = Column( DECIMAL(15, 2))
    CTOT_EXP = Column( DECIMAL(15, 2))
    STOT_EXP = Column( DECIMAL(15, 2))
    CROUNDING = Column( DECIMAL(15, 2))
    SROUNDING = Column( DECIMAL(15, 2))
    CDIV_AMNT = Column( DECIMAL(15, 2))
    SDIV_AMNT = Column( DECIMAL(15, 2))
    CPRELIMTAX = Column( DECIMAL(15, 2))
    SPRELIMTAX = Column( DECIMAL(15, 2))
    CSTAMPDUTY = Column(DECIMAL(15, 2))
    SSTAMPDUTY = Column(DECIMAL(15, 2))
    CTOT_VALUE = Column(DECIMAL(15, 2))
    STOT_VALUE = Column(DECIMAL(15, 2))
    SVALUE1 = Column(DECIMAL(15, 2))
    CVALUE1 = Column(DECIMAL(15, 2))
    SVALUE2 = Column(DECIMAL(15, 2))
    CVALUE2 = Column(DECIMAL(15, 2))
    OWN_DATE = Column(DateTime)
    CCAP_DIFF = Column(DECIMAL(15, 2))
    CBK_RETURN = Column(DECIMAL(15, 2))
    UNIT = Column(String(20))
    ACT_CODE = Column(Integer)
    PAWN_CURR = Column(CHAR(3))
    DIV_BIT = Column(Integer)
    ACC_CODE = Column(String(20))
    BORROWED = Column(Integer)
    PAID = Column(Integer)
    SETTLAMNT = Column(DECIMAL(19, 6))
    T_ENTRYDATE = Column(DateTime)
    P_ENTRYDATE = Column(DateTime)


class PORTRANSrah(Base):
    __tablename__ = 'PORTRANSrah'

    TRANS_NR = Column(Integer, primary_key=True)
    COM_CODE = Column(String(20), index=True)
    PORID = Column(String(20), index=True)
    SECID = Column(String(20), index=True)
    TRANS_DATE = Column(DateTime)
    VAL_END = Column(DateTime)
    PMT_DATE = Column(DateTime)
    AVG_DATE = Column(DateTime, index=True)
    AMOUNT = Column(DECIMAL(19, 6))
    PUR_VALUE = Column(DECIMAL(15, 2))
    PUR_PRICE = Column(DECIMAL(16, 6))
    PAWN_CODE = Column(String(10))
    PUR_CVALUE = Column(DECIMAL(15, 2))
    PAWN_AM = Column(DECIMAL(19, 6))
    OWN_BEGIN = Column(DateTime)
    OWN_END = Column(DateTime)
    PUR_CPRICE = Column(DECIMAL(16, 6))


class RATELASTrah(Base):
    __tablename__ = 'RATELASTrah'

    SECID = Column(String(20), index=True, primary_key=True)
    RDATE = Column(DateTime, index=True)
    RCLOSE = Column(DECIMAL(16, 6))


class SECURITYrah(Base):
    __tablename__ = 'SECURITYrah'

    SECID = Column(String(20), index=True, primary_key=True)
    NAME1 = Column(String(255))
    NAME2 = Column(String(255))
    NAME3 = Column(String(255))
    CURRENCY = Column(CHAR(3))
    PE_CORR = Column(DECIMAL(8, 4))
    ISIN = Column(String(12))


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
