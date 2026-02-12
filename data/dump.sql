-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: formulation_tool
-- ------------------------------------------------------
-- Server version	8.0.33

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
-- Table structure for table `frm_attr_configurations`
--

DROP TABLE IF EXISTS `frm_attr_configurations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_attr_configurations` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `is_enabled` tinyint DEFAULT NULL,
  `config` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_attribute_def`
--

DROP TABLE IF EXISTS `frm_attribute_def`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_attribute_def` (
  `id` varchar(50) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `rollup_type` varchar(10) DEFAULT NULL,
  `src_sys_type` varchar(10) DEFAULT NULL,
  `src_sys_id` varchar(45) DEFAULT NULL,
  `ui_width` int DEFAULT NULL,
  `ui_hide_default` int DEFAULT NULL,
  `ui_editable` int DEFAULT NULL,
  `is_enabled` int DEFAULT NULL,
  `fk_attr_def_group` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_comp_local_formulas`
--

DROP TABLE IF EXISTS `frm_comp_local_formulas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_comp_local_formulas` (
  `project_id` varchar(50) DEFAULT NULL,
  `formula_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_comp_project`
--

DROP TABLE IF EXISTS `frm_comp_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_comp_project` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `author` varchar(50) DEFAULT NULL,
  `createddate` timestamp(3) NULL DEFAULT NULL,
  `lastmodifieddate` timestamp(3) NULL DEFAULT NULL,
  `baseformulaid` varchar(50) DEFAULT NULL,
  `isbaseformulalocal` tinyint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_comp_server_formulas`
--

DROP TABLE IF EXISTS `frm_comp_server_formulas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_comp_server_formulas` (
  `project_id` varchar(50) DEFAULT NULL,
  `formula_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_excel_configurations`
--

DROP TABLE IF EXISTS `frm_excel_configurations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_excel_configurations` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `is_enabled` tinyint DEFAULT NULL,
  `config` longtext,
  `created_by` varchar(50) DEFAULT NULL,
  `created_date` timestamp(3) NULL DEFAULT NULL,
  `last_modified_by` varchar(50) DEFAULT NULL,
  `last_modified_date` timestamp(3) NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_feature_access`
--

DROP TABLE IF EXISTS `frm_feature_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_feature_access` (
  `id` varchar(50) NOT NULL,
  `access_value` varchar(100) DEFAULT NULL,
  `access_label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `frm_feature_access`
--

LOCK TABLES `frm_feature_access` WRITE;
/*!40000 ALTER TABLE `frm_feature_access` DISABLE KEYS */;
INSERT INTO `frm_feature_access` VALUES ('acc_1393d54e087d44698825afb3a092ba6a','userManagement','User Management'),('acc_28af0c4f7e1f485caead3d61c50596dd','configuration','Configuration'),('acc_50d692981d0140bdba95d0ddb513d3da','labelGeneration','Label Generation'),('acc_7f3d13c74d304f74b2b74fbed05f626b','searchFormula','Search Formula'),('acc_a6c17fcc0e954245a7c9e0e45480b2ee','userRoleManagement','User Role Management'),('acc_c1fe2daef2cb476b91cc5e272edcf8ce','createFormula','Create Formula'),('acc_dc92baa9bb344c9a8400e843adbc2ca4','complianceScreening','Compliance Screening'),('acc_e870ebaed4874e31928f1d8d50f2b943','formulaCompareView','Formula Compare View');
/*!40000 ALTER TABLE `frm_feature_access` ENABLE KEYS */;
UNLOCK TABLES;
--
-- Table structure for table `frm_fitem_alt_uom`
--

DROP TABLE IF EXISTS `frm_fitem_alt_uom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_fitem_alt_uom` (
  `id` varchar(50) NOT NULL,
  `fk_formula_item` varchar(50) DEFAULT NULL,
  `fk_alternate_uom` varchar(50) DEFAULT NULL,
  `factor` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_fitem_attr_val`
--

DROP TABLE IF EXISTS `frm_fitem_attr_val`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_fitem_attr_val` (
  `id` varchar(50) NOT NULL,
  `value_measure` int DEFAULT NULL,
  `value_string` varchar(250) DEFAULT NULL,
  `value_bool` int DEFAULT NULL,
  `fk_formula_item` varchar(50) DEFAULT NULL,
  `fk_attribute_def` varchar(50) DEFAULT NULL,
  `fk_uom` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_formula`
--

DROP TABLE IF EXISTS `frm_formula`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_formula` (
  `id` varchar(50) NOT NULL,
  `name` varchar(250) DEFAULT NULL,
  `created_date` timestamp(3) NULL DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `fk_formula_item_output` varchar(50) DEFAULT NULL,
  `ref_id` varchar(50) DEFAULT NULL,
  `last_modified_date` timestamp(3) NULL DEFAULT NULL,
  `server_id` varchar(50) DEFAULT NULL,
  `is_editable` tinyint(1) DEFAULT NULL,
  `revision_code` varchar(50) DEFAULT NULL,
  `revision_id` varchar(50) DEFAULT NULL,
  `item_id` varchar(50) DEFAULT NULL,
  `org_id` varchar(50) DEFAULT NULL,
  `bom_id` varchar(50) DEFAULT NULL,
  `bom_type` varchar(50) DEFAULT NULL,
  `last_modified_by` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_formula_attributes`
--

DROP TABLE IF EXISTS `frm_formula_attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_formula_attributes` (
  `fk_formula` varchar(50) DEFAULT NULL,
  `attribute` varchar(100) DEFAULT NULL,
  `value` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_formula_item`
--

DROP TABLE IF EXISTS `frm_formula_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_formula_item` (
  `id` varchar(50) NOT NULL,
  `name` varchar(250) DEFAULT NULL,
  `fk_formula` varchar(50) DEFAULT NULL,
  `quantity` double DEFAULT NULL,
  `fk_uom` varchar(50) DEFAULT NULL,
  `pct_scrap_factor` int DEFAULT NULL,
  `is_deleted` int DEFAULT NULL,
  `material_ref` varchar(50) DEFAULT NULL,
  `item_type` varchar(10) DEFAULT NULL,
  `pct_composition` int DEFAULT NULL,
  `ref_id` varchar(45) DEFAULT NULL,
  `fk_produced_by_formula` varchar(50) DEFAULT NULL,
  `sequence_number` int DEFAULT NULL,
  `food_contact` varchar(2) DEFAULT NULL,
  `class_type` varchar(250) DEFAULT NULL,
  `fk_selected_uom` varchar(50) DEFAULT NULL,
  `item_id` varchar(50) DEFAULT NULL,
  `org_id` varchar(50) DEFAULT NULL,
  `revision_id` varchar(50) DEFAULT NULL,
  `revision_code` varchar(50) DEFAULT NULL,
  `created_date` timestamp(3) NULL DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `last_modified_date` timestamp(3) NULL DEFAULT NULL,
  `last_modified_by` varchar(50) DEFAULT NULL,
  `substitute_parent` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_notes`
--

DROP TABLE IF EXISTS `frm_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_notes` (
  `id` varchar(50) NOT NULL,
  `lastmodifieddate` timestamp(3) NULL DEFAULT NULL,
  `entry` longtext,
  `formula_id` varchar(50) NOT NULL,
  `username` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_shared_users`
--

DROP TABLE IF EXISTS `frm_shared_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_shared_users` (
  `user_id` varchar(50) NOT NULL,
  `formulaid` varchar(50) NOT NULL,
  `access` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_uom`
--

DROP TABLE IF EXISTS `frm_uom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_uom` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `abbreviation` varchar(10) DEFAULT NULL,
  `base_uom` varchar(50) DEFAULT NULL,
  `conversion` double DEFAULT NULL,
  `category` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frm_user_roles`
--

DROP TABLE IF EXISTS `frm_user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_user_roles` (
  `id` varchar(50) NOT NULL,
  `role` varchar(100) NOT NULL,
  `access` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `frm_user_roles`
--

LOCK TABLES `frm_user_roles` WRITE;
/*!40000 ALTER TABLE `frm_user_roles` DISABLE KEYS */;
INSERT INTO `frm_user_roles` VALUES 
('fur_0d334f660f6b41c494f0c3b114511076','Admin','createFormula, searchFormula, formulaCompareView, labelGeneration, complianceScreening, userManagement, userRoleManagement, configuration');
/*!40000 ALTER TABLE `frm_user_roles` ENABLE KEYS */;
UNLOCK TABLES;
--
-- Table structure for table `frm_users`
--

DROP TABLE IF EXISTS `frm_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `frm_users` (
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `role` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `token` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `createdby` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `modifiedby` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `lastlogin` timestamp(3) NULL DEFAULT NULL,
  `activestatus` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `createdon` timestamp(3) NULL DEFAULT NULL,
  `modifiedon` timestamp(3) NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `frm_users`
--

LOCK TABLES `frm_users` WRITE;
/*!40000 ALTER TABLE `frm_users` DISABLE KEYS */;
INSERT INTO `frm_users` VALUES ('usr_bbe0d4936b3d41949389bafc1ea37ef0','Administrator','admin','Admin',NULL,NULL,NULL,NULL,'y','2023-11-28 09:36:55.352','2023-11-28 09:36:55.352');
/*!40000 ALTER TABLE `frm_users` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-22 10:52:49
