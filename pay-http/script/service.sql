-- MySQL dump 10.13  Distrib 5.7.19, for Linux (x86_64)
--
-- Host: localhost    Database: 51paypay
-- ------------------------------------------------------
-- Server version	5.7.19-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acc_relation`
--

DROP TABLE IF EXISTS `acc_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `acc_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accountid` int(11) NOT NULL,
  `childid` int(11) NOT NULL,
  `extend` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account_appid`
--

DROP TABLE IF EXISTS `account_appid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_appid` (
  `accountid` int(11) NOT NULL,
  `appid` varchar(30) NOT NULL,
  `appkey` varchar(100) NOT NULL,
  `custid` varchar(30) NOT NULL,
  `pay_type` int(11) DEFAULT NULL,
  `extend` text,
  `valid` tinyint(4) DEFAULT '1',
  `mch_name` varchar(60) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `real_pay` int(11) DEFAULT NULL,
  `sceneInfo` text,
  `fee_rate` int(11) DEFAULT '0',
  `banklinknumber` varchar(30) DEFAULT '',
  `paymenttype` varchar(30) DEFAULT '',
  `service_rate` int(11) default '0',   -- 服务费
  PRIMARY KEY (`id`),
  UNIQUE KEY `appid` (`appid`,`pay_type`,`real_pay`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(24) DEFAULT NULL,
  `passwd_hash` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_accounts_phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `appid_channel`
--

DROP TABLE IF EXISTS `appid_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `appid_channel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appid` varchar(30) NOT NULL,
  `real_pay` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `appid_manage`
--

DROP TABLE IF EXISTS `appid_manage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `appid_manage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accountid` int(11) NOT NULL,
  `appid` varchar(30) NOT NULL,
  `appname` varchar(60) NOT NULL,
  `app_type` int(11) NOT NULL,
  `pay_type` varchar(30) DEFAULT NULL,
  `valid` tinyint(4) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_id` (`appid`),
  UNIQUE KEY `app_name` (`appname`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bills`
--

DROP TABLE IF EXISTS `bills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bills` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `access_number` varchar(32) DEFAULT NULL,
  `pay_type` varchar(8) DEFAULT NULL,
  `trade_type` varchar(1) DEFAULT NULL,
  `access_seq` varchar(32) DEFAULT NULL,
  `access_submit_date` datetime DEFAULT NULL,
  `trade_amount` varchar(32) DEFAULT NULL,
  `poundage` varchar(32) DEFAULT NULL,
  `currency_type` varchar(8) DEFAULT NULL,
  `channel_number` varchar(32) DEFAULT NULL,
  `card_code` varchar(32) DEFAULT NULL,
  `account` varchar(32) DEFAULT NULL,
  `protocol` varchar(32) DEFAULT NULL,
  `platform_seq` varchar(32) DEFAULT NULL,
  `platform_trade_date` datetime DEFAULT NULL,
  `trade_status` varchar(1) DEFAULT NULL,
  `bank_merchant_number` varchar(32) DEFAULT NULL,
  `channel_flag` varchar(32) DEFAULT NULL,
  `exchange_rate` varchar(8) DEFAULT NULL,
  `settling_amount` varchar(32) DEFAULT NULL,
  `settling_currency_type` varchar(8) DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `bills_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `custom_ids`
--

DROP TABLE IF EXISTS `custom_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_ids` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `custID` varchar(32) DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `custom_ids_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notify_record`
--

DROP TABLE IF EXISTS `notify_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notify_record` (
  `payid` bigint(20) NOT NULL,
  `pay_status` int(11) NOT NULL,
  `try_times` int(11) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pay_record`
--

DROP TABLE IF EXISTS `pay_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pay_record` (
  `id` bigint(20) NOT NULL,
  `orderid` varchar(60) DEFAULT NULL,
  `mchid` int(11) DEFAULT NULL,
  `appid` varchar(30) DEFAULT NULL,
  `originid` varchar(30) DEFAULT NULL,
  `pay_type` int(11) DEFAULT NULL,
  `pay_status` int(11) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `notify_url` varchar(100) DEFAULT NULL,
  `extend` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fee` decimal(10,5) DEFAULT '0.00000',
  `real_pay` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pay_record_ukey` (`appid`,`orderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t1`
--

DROP TABLE IF EXISTS `t1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `amount` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1099002 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_token`
--

DROP TABLE IF EXISTS `user_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_token` (
  `user_id` bigint(20) NOT NULL,
  `token` varchar(64) NOT NULL,
  `deleted` smallint(6) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-13  9:42:25

 CREATE TABLE `withdraw_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appid` varchar(30) NOT NULL,
  `order_code` varchar(30) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `fee` decimal(10,2) NOT NULL,
  `status` int(11) default null,
  `real_pay` int(11) NOT NULL,
  `channel` varchar(30) DEFAULT NULL,
  `extend` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `jinjian_record` (
  `id` bigint(20) NOT NULL,
  `accountid` int(11) DEFAULT NULL,
  `jinjian_data` text NOT NULL,
  `resp_data` text,
  `real_pay` int(11) NOT NULL,
  `status` int(11) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `mch_name` varchar(30) DEFAULT NULL,
  `custid` varchar(30) DEFAULT NULL,
  `banklinknumber` varchar(30) DEFAULT NULL,
  `paymenttype` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4


CREATE TABLE `jinjian_appid` (
  `accountid` int(11) NOT NULL,
  `appid` int(11) NOT NULL AUTO_INCREMENT,
  `appkey` varchar(64) NOT NULL,
  PRIMARY KEY (`appid`)
) ENGINE=InnoDB AUTO_INCREMENT=60003 DEFAULT CHARSET=utf8mb4;
