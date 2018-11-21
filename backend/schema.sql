-- MySQL dump 10.17  Distrib 10.3.11-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: cse331
-- ------------------------------------------------------
-- Server version	10.3.11-MariaDB-1:10.3.11+maria~bionic-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `BlacklistedWebsites`
--

DROP TABLE IF EXISTS `BlacklistedWebsites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `BlacklistedWebsites` (
  `URL` varchar(200) NOT NULL,
  `RedirectURL` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`URL`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Client`
--

DROP TABLE IF EXISTS `Client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Client` (
  `ID` int(10) unsigned NOT NULL,
  `CellPhone` varchar(15) DEFAULT NULL,
  `Address` varchar(100) DEFAULT NULL,
  `Email` varchar(60) DEFAULT NULL,
  `SSN` char(11) DEFAULT NULL,
  `FirstName` varchar(30) DEFAULT NULL,
  `LastName` varchar(30) DEFAULT NULL,
  `BirthDate` varchar(15) DEFAULT NULL,
  `NextPayload` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ComplexForms`
--

DROP TABLE IF EXISTS `ComplexForms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ComplexForms` (
  `CID` int(10) unsigned NOT NULL,
  `JSONFORM` varchar(400) NOT NULL,
  PRIMARY KEY (`CID`,`JSONFORM`),
  CONSTRAINT `ComplexForms_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `Client` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Cookies`
--

DROP TABLE IF EXISTS `Cookies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Cookies` (
  `CID` int(10) unsigned NOT NULL,
  `URL` varchar(200) NOT NULL,
  `Content` varchar(300) DEFAULT NULL,
  `Name` varchar(80) NOT NULL,
  PRIMARY KEY (`CID`,`URL`,`Name`),
  CONSTRAINT `Cookies_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `Client` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Credentials`
--

DROP TABLE IF EXISTS `Credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Credentials` (
  `Username` varchar(60) NOT NULL,
  `UserPassword` varchar(60) DEFAULT NULL,
  `URL` varchar(200) NOT NULL,
  `CID` int(10) unsigned NOT NULL,
  `MFA` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Username`,`URL`,`CID`),
  KEY `CID` (`CID`),
  CONSTRAINT `Credentials_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `Client` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CreditCard`
--

DROP TABLE IF EXISTS `CreditCard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CreditCard` (
  `CreditCardNumber` int(10) unsigned NOT NULL,
  `CVC` char(3) DEFAULT NULL,
  `ExpirationDate` date DEFAULT NULL,
  `CID` int(10) unsigned NOT NULL,
  `Type` enum('American Express','Discover Card','Mastercard','VISA') DEFAULT NULL,
  PRIMARY KEY (`CreditCardNumber`),
  KEY `CID` (`CID`),
  CONSTRAINT `CreditCard_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `Client` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FormIDMappings`
--

DROP TABLE IF EXISTS `FormIDMappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FormIDMappings` (
  `URL` varchar(200) NOT NULL,
  `RemOrLocID` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`URL`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SecurityQuestions`
--

DROP TABLE IF EXISTS `SecurityQuestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SecurityQuestions` (
  `CID` int(10) unsigned NOT NULL,
  `Question` varchar(80) NOT NULL,
  `Answer` varchar(80) DEFAULT NULL,
  `URL` varchar(200) NOT NULL,
  PRIMARY KEY (`CID`,`Question`,`URL`),
  CONSTRAINT `SecurityQuestions_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `Client` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-11-21 20:19:21
