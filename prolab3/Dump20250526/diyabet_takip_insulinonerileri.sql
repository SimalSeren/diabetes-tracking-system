-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: diyabet_takip
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `insulinonerileri`
--

DROP TABLE IF EXISTS `insulinonerileri`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insulinonerileri` (
  `oneri_id` int NOT NULL AUTO_INCREMENT,
  `hasta_id` int NOT NULL,
  `olcum_id` int NOT NULL,
  `insulin_dozu` varchar(10) COLLATE utf8mb4_turkish_ci NOT NULL,
  `tarih` datetime NOT NULL,
  PRIMARY KEY (`oneri_id`),
  KEY `hasta_id` (`hasta_id`),
  KEY `olcum_id` (`olcum_id`),
  CONSTRAINT `insulinonerileri_ibfk_1` FOREIGN KEY (`hasta_id`) REFERENCES `kullanicilar` (`kullanici_id`),
  CONSTRAINT `insulinonerileri_ibfk_2` FOREIGN KEY (`olcum_id`) REFERENCES `kansekeriolcumleri` (`olcum_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insulinonerileri`
--

LOCK TABLES `insulinonerileri` WRITE;
/*!40000 ALTER TABLE `insulinonerileri` DISABLE KEYS */;
INSERT INTO `insulinonerileri` VALUES (1,2,1,'1 ml','2025-05-26 07:00:00'),(2,5,4,'1 ml','2025-05-26 07:00:00');
/*!40000 ALTER TABLE `insulinonerileri` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-26 23:33:24
