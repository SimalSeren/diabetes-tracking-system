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
-- Table structure for table `kansekeriolcumleri`
--

DROP TABLE IF EXISTS `kansekeriolcumleri`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kansekeriolcumleri` (
  `olcum_id` int NOT NULL AUTO_INCREMENT,
  `hasta_id` int NOT NULL,
  `olcum_degeri` int NOT NULL,
  `olcum_tipi` enum('Sabah','Öğle','İkindi','Akşam','Gece') COLLATE utf8mb4_turkish_ci NOT NULL,
  `olcum_tarihi` datetime NOT NULL,
  PRIMARY KEY (`olcum_id`),
  KEY `hasta_id` (`hasta_id`),
  CONSTRAINT `kansekeriolcumleri_ibfk_1` FOREIGN KEY (`hasta_id`) REFERENCES `kullanicilar` (`kullanici_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kansekeriolcumleri`
--

LOCK TABLES `kansekeriolcumleri` WRITE;
/*!40000 ALTER TABLE `kansekeriolcumleri` DISABLE KEYS */;
INSERT INTO `kansekeriolcumleri` VALUES (1,2,120,'Sabah','2025-05-26 07:00:00'),(2,2,130,'Öğle','2025-05-26 12:00:00'),(3,2,110,'Akşam','2025-05-26 18:00:00'),(4,5,115,'Sabah','2025-05-26 07:00:00'),(5,6,140,'Öğle','2025-05-26 12:00:00'),(6,7,125,'Sabah','2025-05-26 08:00:00'),(7,8,135,'Öğle','2025-05-26 13:00:00'),(8,9,150,'Akşam','2025-05-26 18:00:00'),(9,10,160,'Gece','2025-05-26 22:00:00'),(10,2,123,'Gece','2025-05-26 23:02:41'),(11,2,20,'Gece','2025-05-26 23:02:53');
/*!40000 ALTER TABLE `kansekeriolcumleri` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-26 23:33:22
