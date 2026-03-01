/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.5-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: praitek
-- ------------------------------------------------------
-- Server version	11.8.5-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `account` VALUES
(1,'admin','password',0);
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `action`
--

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `action` VALUES
(1,'http','{\'method\': \'POST\', \'url\': \'http://localhost:5099/analytics-events/person\', \'header\': {}, \'param\': {}, \'body\': \'{\"camera_name\":\"{{camera_name}}\",\"time\":\"{{event_timestamp}}\",\"tag\":\"\",\"image_id\":{{image_id}},\"host_port\":{{host_http_port}} }\'}','milestone');
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `engine`
--

LOCK TABLES `engine` WRITE;
/*!40000 ALTER TABLE `engine` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `engine` VALUES
(2,'Face Recognition'),
(1,'Object Detection');
/*!40000 ALTER TABLE `engine` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `eventrule`
--

LOCK TABLES `eventrule` WRITE;
/*!40000 ALTER TABLE `eventrule` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `eventrule` VALUES
(1,'person','person',0);
/*!40000 ALTER TABLE `eventrule` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `face`
--

LOCK TABLES `face` WRITE;
/*!40000 ALTER TABLE `face` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `face` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `face_group_map`
--

LOCK TABLES `face_group_map` WRITE;
/*!40000 ALTER TABLE `face_group_map` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `face_group_map` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `face_image_map`
--

LOCK TABLES `face_image_map` WRITE;
/*!40000 ALTER TABLE `face_image_map` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `face_image_map` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `facegroup`
--

LOCK TABLES `facegroup` WRITE;
/*!40000 ALTER TABLE `facegroup` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `facegroup` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `faceimage`
--

LOCK TABLES `faceimage` WRITE;
/*!40000 ALTER TABLE `faceimage` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `faceimage` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `objectclass`
--

LOCK TABLES `objectclass` WRITE;
/*!40000 ALTER TABLE `objectclass` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `objectclass` VALUES
(4,'airplane'),
(47,'apple'),
(24,'backpack'),
(46,'banana'),
(34,'baseball bat'),
(35,'baseball glove'),
(21,'bear'),
(59,'bed'),
(13,'bench'),
(1,'bicycle'),
(14,'bird'),
(8,'boat'),
(73,'book'),
(39,'bottle'),
(45,'bowl'),
(50,'broccoli'),
(5,'bus'),
(55,'cake'),
(2,'car'),
(51,'carrot'),
(15,'cat'),
(67,'cell phone'),
(56,'chair'),
(74,'clock'),
(57,'couch'),
(19,'cow'),
(41,'cup'),
(60,'dining table'),
(16,'dog'),
(54,'donut'),
(20,'elephant'),
(10,'fire hydrant'),
(42,'fork'),
(29,'frisbee'),
(23,'giraffe'),
(78,'hair drier'),
(26,'handbag'),
(17,'horse'),
(52,'hot dog'),
(66,'keyboard'),
(33,'kite'),
(43,'knife'),
(63,'laptop'),
(68,'microwave'),
(3,'motorcycle'),
(64,'mouse'),
(49,'orange'),
(69,'oven'),
(12,'parking meter'),
(0,'person'),
(53,'pizza'),
(58,'potted plant'),
(72,'refrigerator'),
(65,'remote'),
(48,'sandwich'),
(76,'scissors'),
(18,'sheep'),
(71,'sink'),
(36,'skateboard'),
(30,'skis'),
(31,'snowboard'),
(44,'spoon'),
(32,'sports ball'),
(11,'stop sign'),
(28,'suitcase'),
(37,'surfboard'),
(77,'teddy bear'),
(38,'tennis racket'),
(27,'tie'),
(70,'toaster'),
(61,'toilet'),
(79,'toothbrush'),
(9,'traffic light'),
(6,'train'),
(7,'truck'),
(62,'tv'),
(25,'umbrella'),
(75,'vase'),
(40,'wine glass'),
(22,'zebra');
/*!40000 ALTER TABLE `objectclass` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `rule_action_map`
--

LOCK TABLES `rule_action_map` WRITE;
/*!40000 ALTER TABLE `rule_action_map` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `rule_action_map` VALUES
(1,1);
/*!40000 ALTER TABLE `rule_action_map` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `se_rule_map`
--

LOCK TABLES `se_rule_map` WRITE;
/*!40000 ALTER TABLE `se_rule_map` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `se_rule_map` VALUES
(1,1);
/*!40000 ALTER TABLE `se_rule_map` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `stream`
--

LOCK TABLES `stream` WRITE;
/*!40000 ALTER TABLE `stream` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `stream` VALUES
(1,'local','usb','0',1,0);
/*!40000 ALTER TABLE `stream` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping data for table `stream_engine_map`
--

LOCK TABLES `stream_engine_map` WRITE;
/*!40000 ALTER TABLE `stream_engine_map` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `stream_engine_map` VALUES
(1,1,1);
/*!40000 ALTER TABLE `stream_engine_map` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-01-28 16:20:51
