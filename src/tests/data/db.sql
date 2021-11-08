-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: 0.0.0.0    Database: test
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.29-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ADDRESSrah`
--

DROP TABLE IF EXISTS `ADDRESSrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ADDRESSrah` (
  `CON_CODE` varchar(12) DEFAULT NULL,
  `ADDRESS1` varchar(100) DEFAULT NULL,
  `ADDRESS2` varchar(100) DEFAULT NULL,
  `ZIP` varchar(9) DEFAULT NULL,
  `ADDRESS3` varchar(100) DEFAULT NULL,
  `ADDRESS4` varchar(100) DEFAULT NULL,
  `PHONE` varchar(20) DEFAULT NULL,
  `TELEFAX` varchar(20) DEFAULT NULL,
  `TELEX` varchar(20) DEFAULT NULL,
  `DEF_ADDR` char(1) DEFAULT NULL,
  `ADDR_NR` int(10) DEFAULT NULL,
  `COM_CODE` varchar(20) DEFAULT NULL,
  `EMAIL` varchar(50) DEFAULT NULL,
  `TRADEACCLIMITED` char(1) DEFAULT NULL,
  `PHONE2` varchar(20) DEFAULT NULL,
  `CONTACT` varchar(100) DEFAULT NULL,
  `OWNER_TYPE` char(1) DEFAULT NULL,
  `ADDRESS_TYPE` varchar(12) DEFAULT NULL,
  `ADDRESS_CODE` int(10) DEFAULT NULL,
  `MOBILE` varchar(20) DEFAULT NULL,
  `USER_ID` varchar(30) DEFAULT NULL,
  `PORID` varchar(20) DEFAULT NULL,
  `BEGIN_DATE` datetime DEFAULT NULL,
  `END_DATE` datetime DEFAULT NULL,
  `DUAL_USER` varchar(30) DEFAULT NULL,
  `A_COM_CODE` varchar(20) DEFAULT NULL,
  `ACC_CODE` varchar(20) DEFAULT NULL,
  `COM_TYPE` varchar(2) DEFAULT NULL,
  `EXT_SYSTEM_ID` int(10) DEFAULT NULL,
  `EXT_SYSTEM_UNIQUE_ID` varchar(50) DEFAULT NULL,
  KEY `DEF_ADDR` (`DEF_ADDR`),
  KEY `ADDR_NR` (`ADDR_NR`),
  KEY `COM_CODE` (`COM_CODE`),
  KEY `PORID` (`PORID`),
  KEY `A_COM_CODE` (`A_COM_CODE`),
  KEY `ACC_CODE` (`ACC_CODE`),
  KEY `COM_TYPE` (`COM_TYPE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ADDRESSrah`
--

LOCK TABLES `ADDRESSrah` WRITE;
/*!40000 ALTER TABLE `ADDRESSrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `ADDRESSrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Authorization`
--

DROP TABLE IF EXISTS `Authorization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Authorization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comCode` int(11) NOT NULL,
  `authorizedSSN` varchar(11) NOT NULL,
  `authorizedComCode` int(11) DEFAULT NULL,
  `authorizedName` varchar(120) NOT NULL,
  `authorizedFirstName` varchar(60) DEFAULT NULL,
  `authorizedLastName` varchar(60) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `zip` varchar(20) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` char(2) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `createdTime` datetime DEFAULT NULL,
  `validity` tinyint(4) DEFAULT NULL,
  `duration` varchar(30) DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `origin` varchar(30) DEFAULT NULL,
  `os_deny` tinyint(4) DEFAULT NULL,
  `external_deny` tinyint(4) DEFAULT NULL,
  `deleteFlag` tinyint(4) DEFAULT NULL,
  `version` varchar(50) DEFAULT NULL,
  `internalGroup` varchar(50) DEFAULT NULL,
  `handledStamp` datetime DEFAULT NULL,
  `ownedBy` varchar(50) DEFAULT NULL,
  `ownedStamp` datetime DEFAULT NULL,
  `bankEventID` varchar(50) DEFAULT NULL,
  `bankEventInternalID` varchar(50) DEFAULT NULL,
  `bankEventDate` datetime DEFAULT NULL,
  `bankEventSSN` varchar(20) DEFAULT NULL,
  `bankEventFirstName` varchar(60) DEFAULT NULL,
  `bankEventLastName` varchar(60) DEFAULT NULL,
  `hiddenAuth` tinyint(2) DEFAULT NULL,
  `deleteStamp` datetime DEFAULT NULL,
  `deletedBy` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `comCode` (`comCode`),
  KEY `authorizedSSN` (`authorizedSSN`),
  KEY `validity` (`validity`),
  KEY `createdTime` (`createdTime`),
  KEY `expires` (`expires`),
  KEY `authorizedName` (`authorizedName`),
  KEY `authComCode` (`authorizedComCode`),
  KEY `handledSamp` (`handledStamp`),
  KEY `ownedStamp` (`ownedStamp`),
  KEY `country` (`country`),
  KEY `os_deny` (`os_deny`),
  KEY `version` (`version`),
  KEY `bankEventID` (`bankEventID`),
  KEY `internalGroup` (`internalGroup`),
  KEY `hiddenAuth` (`hiddenAuth`),
  KEY `ownedBy` (`ownedBy`)
) ENGINE=InnoDB AUTO_INCREMENT=123123125 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Authorization`
--

LOCK TABLES `Authorization` WRITE;
/*!40000 ALTER TABLE `Authorization` DISABLE KEYS */;
/*!40000 ALTER TABLE `Authorization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `COMPANYrah`
--

DROP TABLE IF EXISTS `COMPANYrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `COMPANYrah` (
  `COM_CODE` varchar(20) DEFAULT NULL,
  `SHORTNAME` varchar(50) DEFAULT NULL,
  `NAME1` varchar(255) DEFAULT NULL,
  `NAME2` varchar(255) DEFAULT NULL,
  `NAME3` varchar(255) DEFAULT NULL,
  `SO_SEC_NR` varchar(11) DEFAULT NULL,
  `LANGCODE` char(1) DEFAULT NULL,
  `CNTRY_CODE` char(3) DEFAULT NULL,
  `COM_CLASS` char(2) DEFAULT NULL,
  `REMARK` longtext DEFAULT NULL,
  `CREA_DATE` datetime DEFAULT NULL,
  `REF` char(3) DEFAULT NULL,
  `NATIONALITY` varchar(3) DEFAULT NULL,
  `FIRST_NAME` varchar(40) DEFAULT NULL,
  `LAST_NAME` varchar(40) DEFAULT NULL,
  `IDENT_METH_ID` int(10) DEFAULT NULL,
  KEY `COM_CODE` (`COM_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `COMPANYrah`
--

LOCK TABLES `COMPANYrah` WRITE;
/*!40000 ALTER TABLE `COMPANYrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `COMPANYrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disableMobileDevice`
--

DROP TABLE IF EXISTS `disableMobileDevice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disableMobileDevice` (
  `deviceUuid` varchar(50) DEFAULT NULL,
  `comCode` varchar(20) DEFAULT NULL,
  `disabled` varchar(5) DEFAULT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disableMobileDevice`
--

LOCK TABLES `disableMobileDevice` WRITE;
/*!40000 ALTER TABLE `disableMobileDevice` DISABLE KEYS */;
/*!40000 ALTER TABLE `disableMobileDevice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lastReplicationDate`
--

DROP TABLE IF EXISTS `lastReplicationDate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lastReplicationDate` (
  `ID` int(11) DEFAULT NULL,
  `lastUpdateDate` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lastReplicationDate`
--

LOCK TABLES `lastReplicationDate` WRITE;
/*!40000 ALTER TABLE `lastReplicationDate` DISABLE KEYS */;
/*!40000 ALTER TABLE `lastReplicationDate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoginMobileLog`
--

DROP TABLE IF EXISTS `LoginMobileLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoginMobileLog` (
  `ID` int(20) NOT NULL AUTO_INCREMENT,
  `accountName` varchar(30) DEFAULT NULL,
  `deviceModel` varchar(255) DEFAULT NULL,
  `deviceUuid` varchar(64) DEFAULT NULL,
  `deviceVersion` varchar(64) DEFAULT NULL,
  `devicePlatform` varchar(64) DEFAULT NULL,
  `COMCODE` int(12) DEFAULT NULL,
  `IP` varchar(64) DEFAULT NULL,
  `SUCCES` int(1) DEFAULT NULL,
  `TIME` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `IPForwarded` varchar(255) DEFAULT NULL,
  `deviceBrowser` varchar(255) DEFAULT NULL,
  `denyLoginReason` varchar(255) DEFAULT NULL,
  `appVersion` varchar(20) DEFAULT NULL,
  `RandSet` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `TIME` (`TIME`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoginMobileLog`
--

LOCK TABLES `LoginMobileLog` WRITE;
/*!40000 ALTER TABLE `LoginMobileLog` DISABLE KEYS */;
/*!40000 ALTER TABLE `LoginMobileLog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mobileSession`
--

DROP TABLE IF EXISTS `mobileSession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mobileSession` (
  `id` int(7) unsigned NOT NULL AUTO_INCREMENT,
  `comCode` varchar(20) DEFAULT NULL,
  `sessionKey` varchar(20) DEFAULT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mobileSession`
--

LOCK TABLES `mobileSession` WRITE;
/*!40000 ALTER TABLE `mobileSession` DISABLE KEYS */;
/*!40000 ALTER TABLE `mobileSession` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OS_ALERT_STATUS_MOBILE`
--

DROP TABLE IF EXISTS `OS_ALERT_STATUS_MOBILE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OS_ALERT_STATUS_MOBILE` (
  `STATUS_CODE` int(2) DEFAULT NULL,
  `TARGET` varchar(20) DEFAULT NULL,
  `FI_message` varchar(5000) DEFAULT NULL,
  `SV_message` varchar(5000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OS_ALERT_STATUS_MOBILE`
--

LOCK TABLES `OS_ALERT_STATUS_MOBILE` WRITE;
/*!40000 ALTER TABLE `OS_ALERT_STATUS_MOBILE` DISABLE KEYS */;
/*!40000 ALTER TABLE `OS_ALERT_STATUS_MOBILE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PORTFOLrah`
--

DROP TABLE IF EXISTS `PORTFOLrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PORTFOLrah` (
  `PORID` varchar(20) DEFAULT NULL,
  `COM_CODE` varchar(20) DEFAULT NULL,
  `NAME1` varchar(255) DEFAULT NULL,
  `NAME2` varchar(255) DEFAULT NULL,
  `NAME3` varchar(255) DEFAULT NULL,
  `POR_TYPE` char(2) DEFAULT NULL,
  `POR_STATUS` char(2) DEFAULT NULL,
  `BDATE` datetime DEFAULT NULL,
  `EDATE` datetime DEFAULT NULL,
  `VALUATION` int(10) DEFAULT NULL,
  `CHARGE` char(2) DEFAULT NULL,
  `PASSWORD` varchar(12) DEFAULT NULL,
  `TIMELIMIT` int(10) DEFAULT NULL,
  `NOTE` varchar(4000) DEFAULT NULL,
  `COMBINED` varchar(20) DEFAULT NULL,
  `TRUSTACC` varchar(30) DEFAULT NULL,
  `BKACCOUNT` varchar(30) DEFAULT NULL,
  `CON_CODE` varchar(12) DEFAULT NULL,
  `OWN_TYPE` char(1) DEFAULT NULL,
  `TRUSTACC2` varchar(30) DEFAULT NULL,
  `TRUSTACC3` varchar(30) DEFAULT NULL,
  `LIMITEDUSE` varchar(1) DEFAULT NULL,
  `VALUEDATE` int(10) DEFAULT NULL,
  `MINFEE` decimal(15,2) DEFAULT NULL,
  `BASICFEE` decimal(15,2) DEFAULT NULL,
  `PCNT_CVAL` decimal(8,4) DEFAULT NULL,
  `TR_PRICE` decimal(12,2) DEFAULT NULL,
  `DRV_PRICE` decimal(12,2) DEFAULT NULL,
  `SEC_PRICE` decimal(12,2) DEFAULT NULL,
  `PHYS_PRICE` decimal(12,2) DEFAULT NULL,
  `FORE_PRICE` decimal(12,2) DEFAULT NULL,
  `FEEGROUP` char(1) DEFAULT NULL,
  `REG1_PRICE` decimal(12,2) DEFAULT NULL,
  `REG2_PRICE` decimal(12,2) DEFAULT NULL,
  `LIMIT_IND` varchar(15) DEFAULT NULL,
  `CMPR_IND` varchar(20) DEFAULT NULL,
  `PERIOD` datetime DEFAULT NULL,
  `NXTVOUCHER` int(10) DEFAULT NULL,
  `INV_GRP` int(10) DEFAULT NULL,
  `TRADEACCLIMITED` char(1) DEFAULT NULL,
  `PAWN_CODE` varchar(10) DEFAULT NULL,
  KEY `COM_CODE` (`COM_CODE`),
  KEY `BDATE` (`BDATE`),
  KEY `EDATE` (`EDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PORTFOLrah`
--

LOCK TABLES `PORTFOLrah` WRITE;
/*!40000 ALTER TABLE `PORTFOLrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `PORTFOLrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PORTLOGrah`
--

DROP TABLE IF EXISTS `PORTLOGrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PORTLOGrah` (
  `TRANS_NR` int(10) DEFAULT NULL,
  `PREV_NR` int(10) DEFAULT NULL,
  `ACT_NR` int(10) DEFAULT NULL,
  `TRANS_CODE` char(2) DEFAULT NULL,
  `COM_CODE` varchar(20) DEFAULT NULL,
  `CCOM_CODE` varchar(20) DEFAULT NULL,
  `PORID` varchar(20) DEFAULT NULL,
  `CPORID` varchar(20) DEFAULT NULL,
  `SEC_TYPE` char(2) DEFAULT NULL,
  `SECID` varchar(20) DEFAULT NULL,
  `CSECID` varchar(20) DEFAULT NULL,
  `ISSUE` int(10) DEFAULT NULL,
  `OISSUE` int(10) DEFAULT NULL,
  `BROKID` varchar(20) DEFAULT NULL,
  `TRUSTID` varchar(50) DEFAULT NULL,
  `TRUST_NMBR` int(10) DEFAULT NULL,
  `TRANS_DATE` datetime DEFAULT NULL,
  `PMT_DATE` datetime DEFAULT NULL,
  `ORDER_VAL` datetime DEFAULT NULL,
  `ORDER_TIME` varchar(8) DEFAULT NULL,
  `CURRENCY1` char(3) DEFAULT NULL,
  `AMOUNT` decimal(19,6) DEFAULT NULL,
  `PRICE` decimal(16,6) DEFAULT NULL,
  `EXPENSES` decimal(15,2) DEFAULT NULL,
  `VALUE` decimal(15,2) DEFAULT NULL,
  `SPURVALUE2` decimal(15,2) DEFAULT NULL,
  `FEE` decimal(15,2) DEFAULT NULL,
  `PROVISION` decimal(15,2) DEFAULT NULL,
  `TAX` decimal(15,2) DEFAULT NULL,
  `OWN_TAX` decimal(15,2) DEFAULT NULL,
  `EMISSION` decimal(15,2) DEFAULT NULL,
  `TOT_EXP` decimal(15,2) DEFAULT NULL,
  `ROUNDING` decimal(15,2) DEFAULT NULL,
  `CURRENCY2` char(3) DEFAULT NULL,
  `CUR_RATE` decimal(16,6) DEFAULT NULL,
  `SPROFIT` decimal(15,2) DEFAULT NULL,
  `BDATE` datetime DEFAULT NULL,
  `EDATE` datetime DEFAULT NULL,
  `VOUCHER` int(10) DEFAULT NULL,
  `PAWN_CODE` varchar(10) DEFAULT NULL,
  `PAWN_AM` decimal(19,6) DEFAULT NULL,
  `SPL_RATIO` decimal(15,9) DEFAULT NULL,
  `SPL_RATIO2` decimal(15,9) DEFAULT NULL,
  `SPL_DATE` datetime DEFAULT NULL,
  `DIV_AMNT` decimal(15,2) DEFAULT NULL,
  `DIV_DATE` datetime DEFAULT NULL,
  `PRELIMTAX` decimal(15,2) DEFAULT NULL,
  `POFF_DATE` datetime DEFAULT NULL,
  `POFF_PRICE` decimal(16,6) DEFAULT NULL,
  `POFF_VALUE` decimal(15,2) DEFAULT NULL,
  `ISS_PRINT` datetime DEFAULT NULL,
  `TEMP_NR` varchar(30) DEFAULT NULL,
  `TRLEVEL` char(1) DEFAULT NULL,
  `ACCOUNT` varchar(35) DEFAULT NULL,
  `CAN_NMBR` int(10) DEFAULT NULL,
  `PREV_CODE` char(2) DEFAULT NULL,
  `CURRENCY` char(3) DEFAULT NULL,
  `CUR_RATE2` decimal(16,6) DEFAULT NULL,
  `PRINTED` int(10) DEFAULT NULL,
  `NOTE` varchar(255) DEFAULT NULL,
  `STATUS` char(1) DEFAULT NULL,
  `CURR_CODE` int(10) DEFAULT NULL,
  `EFF_YIELD` decimal(16,6) DEFAULT NULL,
  `INT_PERIOD` int(10) DEFAULT NULL,
  `TAX_CODE` int(10) DEFAULT NULL,
  `SCAP_DIFF` decimal(15,2) DEFAULT NULL,
  `INTEREST` decimal(12,6) DEFAULT NULL,
  `TAX_PCNT` decimal(8,4) DEFAULT NULL,
  `STAMP_DUTY` decimal(15,2) DEFAULT NULL,
  `UPD_USER` varchar(30) DEFAULT NULL,
  `UPD_DATE` datetime DEFAULT NULL,
  `UPD_TIME` varchar(8) DEFAULT NULL,
  `ORIG_NMBR` int(10) DEFAULT NULL,
  `CLEAR_CODE` char(10) DEFAULT NULL,
  `CLEAR_DATE` datetime DEFAULT NULL,
  `CLEAR_STAT` char(1) DEFAULT NULL,
  `BE_ACCOUNT` varchar(20) DEFAULT NULL,
  `EXT_NR` varchar(250) DEFAULT NULL,
  `CAGIO` decimal(15,2) DEFAULT NULL,
  `SBK_RETURN` decimal(15,2) DEFAULT NULL,
  `EXT_NAME` varchar(10) DEFAULT NULL,
  `EXT_CODE` varchar(15) DEFAULT NULL,
  `ISIN` varchar(12) DEFAULT NULL,
  `SETTLSTAT` varchar(4) DEFAULT NULL,
  `DEALTYPE` char(2) DEFAULT NULL,
  `TR_STATUS` char(2) DEFAULT NULL,
  `ERRORCODE` varchar(5) DEFAULT NULL,
  `SWIFT_ADDR` varchar(15) DEFAULT NULL,
  `EXT_TYPE` varchar(10) DEFAULT NULL,
  `KATIREF` varchar(18) DEFAULT NULL,
  `FREECODE` char(5) DEFAULT NULL,
  `TOT_VALUE` decimal(15,2) DEFAULT NULL,
  `DATE1` datetime DEFAULT NULL,
  `DATE2` datetime DEFAULT NULL,
  `VALUE1` decimal(15,2) DEFAULT NULL,
  `VALUE2` decimal(15,2) DEFAULT NULL,
  `VALUE3` decimal(10,6) DEFAULT NULL,
  `VALUE4` decimal(10,6) DEFAULT NULL,
  `CODE1` int(10) DEFAULT NULL,
  `CODE2` int(10) DEFAULT NULL,
  `CODE3` char(2) DEFAULT NULL,
  `CODE4` varchar(12) DEFAULT NULL,
  `CODE5` varchar(30) DEFAULT NULL,
  `PMT_TRANS` char(1) DEFAULT NULL,
  `PMTERROR` varchar(16) DEFAULT NULL,
  `BENOFSECA` varchar(12) DEFAULT NULL,
  `BENOFSECD` varchar(35) DEFAULT NULL,
  `SHORTCODE` char(1) DEFAULT NULL,
  `STATCODE` varchar(10) DEFAULT NULL,
  `CPROFIT` decimal(15,2) DEFAULT NULL,
  `AVG_RATE` decimal(16,6) DEFAULT NULL,
  `FILTERSTAT` varchar(255) DEFAULT NULL,
  `CUR_RATE1` decimal(16,6) DEFAULT NULL,
  `CAMOUNT` decimal(19,6) DEFAULT NULL,
  `SAMOUNT` decimal(19,6) DEFAULT NULL,
  `CPRICE` decimal(16,6) DEFAULT NULL,
  `SPRICE` decimal(16,6) DEFAULT NULL,
  `CEXPENSES` decimal(15,2) DEFAULT NULL,
  `SEXPENSES` decimal(15,2) DEFAULT NULL,
  `CVALUE` decimal(15,2) DEFAULT NULL,
  `SVALUE` decimal(15,2) DEFAULT NULL,
  `CPURVALUE2` decimal(15,2) DEFAULT NULL,
  `CFEE` decimal(15,2) DEFAULT NULL,
  `SFEE` decimal(15,2) DEFAULT NULL,
  `CPROVISION` decimal(15,2) DEFAULT NULL,
  `SPROVISION` decimal(15,2) DEFAULT NULL,
  `CTAX` decimal(15,2) DEFAULT NULL,
  `STAX` decimal(15,2) DEFAULT NULL,
  `COWN_TAX` decimal(15,2) DEFAULT NULL,
  `SOWN_TAX` decimal(15,2) DEFAULT NULL,
  `CEMISSION` decimal(15,2) DEFAULT NULL,
  `SEMISSION` decimal(15,2) DEFAULT NULL,
  `CTOT_EXP` decimal(15,2) DEFAULT NULL,
  `STOT_EXP` decimal(15,2) DEFAULT NULL,
  `CROUNDING` decimal(15,2) DEFAULT NULL,
  `SROUNDING` decimal(15,2) DEFAULT NULL,
  `CDIV_AMNT` decimal(15,2) DEFAULT NULL,
  `SDIV_AMNT` decimal(15,2) DEFAULT NULL,
  `CPRELIMTAX` decimal(15,2) DEFAULT NULL,
  `SPRELIMTAX` decimal(15,2) DEFAULT NULL,
  `CSTAMPDUTY` decimal(15,2) DEFAULT NULL,
  `SSTAMPDUTY` decimal(15,2) DEFAULT NULL,
  `CTOT_VALUE` decimal(15,2) DEFAULT NULL,
  `STOT_VALUE` decimal(15,2) DEFAULT NULL,
  `SVALUE1` decimal(15,2) DEFAULT NULL,
  `CVALUE1` decimal(15,2) DEFAULT NULL,
  `SVALUE2` decimal(15,2) DEFAULT NULL,
  `CVALUE2` decimal(15,2) DEFAULT NULL,
  `OWN_DATE` datetime DEFAULT NULL,
  `CCAP_DIFF` decimal(15,2) DEFAULT NULL,
  `CBK_RETURN` decimal(15,2) DEFAULT NULL,
  `UNIT` varchar(20) DEFAULT NULL,
  `ACT_CODE` int(10) DEFAULT NULL,
  `PAWN_CURR` char(3) DEFAULT NULL,
  `DIV_BIT` int(10) DEFAULT NULL,
  `ACC_CODE` varchar(20) DEFAULT NULL,
  `BORROWED` int(10) DEFAULT NULL,
  `PAID` int(10) DEFAULT NULL,
  `SETTLAMNT` decimal(19,6) DEFAULT NULL,
  `T_ENTRYDATE` datetime DEFAULT NULL,
  `P_ENTRYDATE` datetime DEFAULT NULL,
  KEY `COM_CODE` (`COM_CODE`),
  KEY `TRANS_CODE` (`TRANS_CODE`),
  KEY `SEC_TYPE` (`SEC_TYPE`),
  KEY `SECID` (`SECID`),
  KEY `STATUS` (`STATUS`),
  KEY `TRANS_DATE` (`TRANS_DATE`),
  KEY `ACT_NR` (`ACT_NR`),
  KEY `TRANS_NR` (`TRANS_NR`),
  KEY `PREV_NR` (`PREV_NR`),
  KEY `PORID` (`PORID`),
  KEY `KATIREF` (`KATIREF`),
  KEY `EXT_NR` (`EXT_NR`),
  KEY `CSECID` (`CSECID`),
  KEY `CCOM_CODE` (`CCOM_CODE`),
  KEY `ISSUE` (`ISSUE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PORTLOGrah`
--

LOCK TABLES `PORTLOGrah` WRITE;
/*!40000 ALTER TABLE `PORTLOGrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `PORTLOGrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PORTRANSrah`
--

DROP TABLE IF EXISTS `PORTRANSrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PORTRANSrah` (
  `TRANS_NR` int(10) DEFAULT NULL,
  `COM_CODE` varchar(20) DEFAULT NULL,
  `PORID` varchar(20) DEFAULT NULL,
  `SECID` varchar(20) DEFAULT NULL,
  `TRANS_DATE` datetime DEFAULT NULL,
  `VAL_END` datetime DEFAULT NULL,
  `PMT_DATE` datetime DEFAULT NULL,
  `AVG_DATE` datetime DEFAULT NULL,
  `AMOUNT` decimal(19,6) DEFAULT NULL,
  `PUR_VALUE` decimal(15,2) DEFAULT NULL,
  `PUR_PRICE` decimal(16,6) DEFAULT NULL,
  `PAWN_CODE` varchar(10) DEFAULT NULL,
  `PUR_CVALUE` decimal(15,2) DEFAULT NULL,
  `PAWN_AM` decimal(19,6) DEFAULT NULL,
  `OWN_BEGIN` datetime DEFAULT NULL,
  `OWN_END` datetime DEFAULT NULL,
  `PUR_CPRICE` decimal(16,6) DEFAULT NULL,
  KEY `COM_CODE` (`COM_CODE`),
  KEY `SECID` (`SECID`),
  KEY `AVG_DATE` (`AVG_DATE`),
  KEY `PORID` (`PORID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PORTRANSrah`
--

LOCK TABLES `PORTRANSrah` WRITE;
/*!40000 ALTER TABLE `PORTRANSrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `PORTRANSrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RATELASTrah`
--

DROP TABLE IF EXISTS `RATELASTrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RATELASTrah` (
  `SECID` varchar(20) DEFAULT NULL,
  `RDATE` datetime DEFAULT NULL,
  `RCLOSE` decimal(16,6) DEFAULT NULL,
  KEY `SECID` (`SECID`),
  KEY `RDATE` (`RDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RATELASTrah`
--

LOCK TABLES `RATELASTrah` WRITE;
/*!40000 ALTER TABLE `RATELASTrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `RATELASTrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RATErah`
--

DROP TABLE IF EXISTS `RATErah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RATErah` (
  `SECID` varchar(20) DEFAULT NULL,
  `RDATE` datetime DEFAULT NULL,
  `RCLOSE` decimal(16,6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RATErah`
--

LOCK TABLES `RATErah` WRITE;
/*!40000 ALTER TABLE `RATErah` DISABLE KEYS */;
/*!40000 ALTER TABLE `RATErah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SECURITYrah`
--

DROP TABLE IF EXISTS `SECURITYrah`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SECURITYrah` (
  `SECID` varchar(20) DEFAULT NULL,
  `NAME1` varchar(255) DEFAULT NULL,
  `NAME2` varchar(255) DEFAULT NULL,
  `NAME3` varchar(255) DEFAULT NULL,
  `CURRENCY` char(3) DEFAULT NULL,
  `PE_CORR` decimal(8,4) DEFAULT NULL,
  `ISIN` varchar(12) DEFAULT NULL,
  KEY `SECID` (`SECID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SECURITYrah`
--

LOCK TABLES `SECURITYrah` WRITE;
/*!40000 ALTER TABLE `SECURITYrah` DISABLE KEYS */;
/*!40000 ALTER TABLE `SECURITYrah` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserAccount`
--

DROP TABLE IF EXISTS `UserAccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserAccount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userName` varchar(48) NOT NULL,
  `hash` varchar(48) NOT NULL,
  `random` char(22) DEFAULT NULL,
  `comCode` int(11) NOT NULL,
  `__contractID` int(11) DEFAULT NULL,
  `disabled` bit(1) NOT NULL DEFAULT b'1',
  `readOnly` bit(1) NOT NULL DEFAULT b'0',
  `notificationEnabled` bit(1) NOT NULL DEFAULT b'0',
  `contractUpdateOverride` bit(1) NOT NULL DEFAULT b'0',
  `lastPasswordChange` datetime DEFAULT NULL,
  `notificationEmail` varchar(64) DEFAULT NULL,
  `lastRedemptionExitPollResponse` datetime DEFAULT NULL,
  `portfolioCreateEnabled` tinyint(4) DEFAULT 0,
  `contractUpdateDate` datetime DEFAULT NULL,
  `bankAccountChangeDisabled` bit(1) DEFAULT NULL,
  `bankIdRedemptionValidation` varchar(10) DEFAULT NULL,
  `accountStatus` tinyint(2) DEFAULT NULL,
  `notificationEnabledMobile` bit(1) DEFAULT NULL,
  `traditionalLoginDisabled` tinyint(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userName` (`userName`),
  UNIQUE KEY `comCode` (`comCode`),
  UNIQUE KEY `contractID` (`__contractID`),
  KEY `userName_2` (`userName`(8)),
  KEY `accountStatus` (`accountStatus`),
  KEY `contractUpdateDate` (`contractUpdateDate`)
) ENGINE=InnoDB AUTO_INCREMENT=10000000 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserAccount`
--

LOCK TABLES `UserAccount` WRITE;
/*!40000 ALTER TABLE `UserAccount` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserAccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserAccountSharedAccess`
--

DROP TABLE IF EXISTS `UserAccountSharedAccess`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserAccountSharedAccess` (
  `grantAccess` int(11) NOT NULL,
  `comCode` int(11) NOT NULL,
  `expires` date DEFAULT NULL,
  `readOnly` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`grantAccess`,`comCode`),
  KEY `comCode` (`comCode`),
  KEY `grantAccess` (`grantAccess`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserAccountSharedAccess`
--

LOCK TABLES `UserAccountSharedAccess` WRITE;
/*!40000 ALTER TABLE `UserAccountSharedAccess` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserAccountSharedAccess` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserAccountSharedAccessLog`
--

DROP TABLE IF EXISTS `UserAccountSharedAccessLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserAccountSharedAccessLog` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `comCode` int(11) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `accessedComCode` int(11) NOT NULL,
  `readOnly` bigint(20) DEFAULT NULL,
  `mobileApp` tinyint(1) DEFAULT NULL,
  `time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=403 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserAccountSharedAccessLog`
--

LOCK TABLES `UserAccountSharedAccessLog` WRITE;
/*!40000 ALTER TABLE `UserAccountSharedAccessLog` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserAccountSharedAccessLog` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
