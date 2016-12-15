-- MySQL dump 10.13  Distrib 5.6.24, for osx10.8 (x86_64)
--
-- Host: localhost    Database: demog_compadre
-- ------------------------------------------------------
-- Server version	5.6.24

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
-- Table structure for table `additional_sources`
--

DROP TABLE IF EXISTS `additional_sources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `additional_sources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publication_id` int(11) DEFAULT NULL,
  `source_type_id` int(11) DEFAULT NULL,
  `authors` text,
  `editors` text,
  `pub_title` text,
  `journal_book_conf` text,
  `year` smallint(6) DEFAULT NULL,
  `volume` text,
  `pages` text,
  `publisher` text,
  `city` text,
  `country` text,
  `institution` text,
  `DOI_ISBN` text,
  `name` text,
  `description` text,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `source_type_id` (`source_type_id`),
  CONSTRAINT `additional_sources_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`),
  CONSTRAINT `additional_sources_ibfk_2` FOREIGN KEY (`source_type_id`) REFERENCES `source_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `angio_gymno`
--

DROP TABLE IF EXISTS `angio_gymno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `angio_gymno` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `angio_gymno_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_angio_gymno_angio_gymno_name` (`angio_gymno_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `author_contacts`
--

DROP TABLE IF EXISTS `author_contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `author_contacts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publication_id` int(11) DEFAULT NULL,
  `date_contacted` date DEFAULT NULL,
  `contacting_user_id` int(11) DEFAULT NULL,
  `content_email_id` int(11) DEFAULT NULL,
  `author_reply` text,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contacting_user_id` (`contacting_user_id`),
  KEY `content_email_id` (`content_email_id`),
  KEY `publication_id` (`publication_id`),
  KEY `ix_author_contacts_date_contacted` (`date_contacted`),
  CONSTRAINT `author_contacts_ibfk_1` FOREIGN KEY (`contacting_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `author_contacts_ibfk_2` FOREIGN KEY (`content_email_id`) REFERENCES `content_email` (`id`),
  CONSTRAINT `author_contacts_ibfk_3` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `captivities`
--

DROP TABLE IF EXISTS `captivities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `captivities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cap_code` varchar(5) DEFAULT NULL,
  `cap_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_captivities_cap_code` (`cap_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `census_timings`
--

DROP TABLE IF EXISTS `census_timings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `census_timings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `census_name` varchar(200) DEFAULT NULL,
  `census_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_census_timings_census_name` (`census_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `content_email`
--

DROP TABLE IF EXISTS `content_email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `content_email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content_code` varchar(5) DEFAULT NULL,
  `content_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_content_email_content_code` (`content_code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `continents`
--

DROP TABLE IF EXISTS `continents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `continents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `continent_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_continents_continent_name` (`continent_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `databases`
--

DROP TABLE IF EXISTS `databases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `databases` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `database_name` varchar(64) DEFAULT NULL,
  `database_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_databases_database_name` (`database_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `daves_growth_types`
--

DROP TABLE IF EXISTS `daves_growth_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daves_growth_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(64) DEFAULT NULL,
  `type_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_daves_growth_types_type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dicot_monoc`
--

DROP TABLE IF EXISTS `dicot_monoc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dicot_monoc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dicot_monoc_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dicot_monoc_dicot_monoc_name` (`dicot_monoc_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ecoregions`
--

DROP TABLE IF EXISTS `ecoregions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ecoregions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ecoregion_code` varchar(5) DEFAULT NULL,
  `ecoregion_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_ecoregions_ecoregion_code` (`ecoregion_code`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `esa_statuses`
--

DROP TABLE IF EXISTS `esa_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `esa_statuses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_code` varchar(64) DEFAULT NULL,
  `status_name` varchar(64) DEFAULT NULL,
  `status_description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_esa_statuses_status_code` (`status_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fixed`
--

DROP TABLE IF EXISTS `fixed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fixed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `matrix_id` int(11) DEFAULT NULL,
  `vector_str` text,
  `vector_present` tinyint(1) DEFAULT NULL,
  `total_pop_no` int(11) DEFAULT NULL,
  `small_id` int(11) DEFAULT NULL,
  `private` tinyint(1) DEFAULT NULL,
  `census_timing_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `small_id` (`small_id`),
  KEY `ix_fixed_matrix_id` (`matrix_id`),
  CONSTRAINT `fixed_ibfk_1` FOREIGN KEY (`matrix_id`) REFERENCES `matrices` (`id`),
  CONSTRAINT `fixed_ibfk_2` FOREIGN KEY (`small_id`) REFERENCES `smalls` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `growth_forms_raunkiaer`
--

DROP TABLE IF EXISTS `growth_forms_raunkiaer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `growth_forms_raunkiaer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `form_name` text,
  PRIMARY KEY (`id`),
  KEY `ix_growth_forms_raunkiaer_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `growth_types`
--

DROP TABLE IF EXISTS `growth_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `growth_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_growth_types_type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `intervals`
--

DROP TABLE IF EXISTS `intervals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `intervals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `matrix_id` int(11) DEFAULT NULL,
  `interval_order` int(11) DEFAULT NULL,
  `interval_start` date DEFAULT NULL,
  `interval_end` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `matrix_id` (`matrix_id`),
  CONSTRAINT `intervals_ibfk_1` FOREIGN KEY (`matrix_id`) REFERENCES `matrices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invasive_status_elsewhere`
--

DROP TABLE IF EXISTS `invasive_status_elsewhere`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invasive_status_elsewhere` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_name` varchar(64) DEFAULT NULL,
  `status_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_invasive_status_elsewhere_status_name` (`status_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invasive_status_studies`
--

DROP TABLE IF EXISTS `invasive_status_studies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invasive_status_studies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_name` varchar(64) DEFAULT NULL,
  `status_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_invasive_status_studies_status_name` (`status_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `iucn_status`
--

DROP TABLE IF EXISTS `iucn_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iucn_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_code` varchar(64) DEFAULT NULL,
  `status_name` varchar(64) DEFAULT NULL,
  `status_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_iucn_status_status_code` (`status_code`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matrices`
--

DROP TABLE IF EXISTS `matrices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matrices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `population_id` int(11) DEFAULT NULL,
  `treatment_id` int(11) DEFAULT NULL,
  `matrix_split` tinyint(1) DEFAULT NULL,
  `matrix_composition_id` int(11) DEFAULT NULL,
  `survival_issue` float DEFAULT NULL,
  `n_intervals` smallint(6) DEFAULT NULL,
  `matrix_criteria_size` tinyint(1) DEFAULT NULL,
  `matrix_criteria_ontogeny` tinyint(1) DEFAULT NULL,
  `matrix_criteria_age` tinyint(1) DEFAULT NULL,
  `study_id` int(11) DEFAULT NULL,
  `matrix_start` varchar(64) DEFAULT NULL,
  `matrix_end` varchar(64) DEFAULT NULL,
  `matrix_start_season_id` int(11) DEFAULT NULL,
  `matrix_end_season_id` int(11) DEFAULT NULL,
  `matrix_fec` tinyint(1) DEFAULT NULL,
  `n_plots` smallint(6) DEFAULT NULL,
  `plot_size` float DEFAULT NULL,
  `n_individuals` int(11) DEFAULT NULL,
  `studied_sex_id` int(11) DEFAULT NULL,
  `captivity_id` int(11) DEFAULT NULL,
  `matrix_dimension` int(11) DEFAULT NULL,
  `observations` text,
  `periodicity` varchar(64) DEFAULT NULL,
  `matrix_a_string` text,
  `matrix_class_string` text,
  `uid` longtext,
  `checked` tinyint(1) DEFAULT NULL,
  `seasonal` tinyint(1) DEFAULT NULL,
  `status_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  `checked_count` int(11) DEFAULT NULL,
  `independent` tinyint(1) DEFAULT NULL,
  `matrix_c_string` text,
  `matrix_f_string` text,
  `matrix_u_string` text,
  `non_independence` text,
  `non_independence_author` text,
  PRIMARY KEY (`id`),
  KEY `captivity_id` (`captivity_id`),
  KEY `matrix_composition_id` (`matrix_composition_id`),
  KEY `matrix_end_season_id` (`matrix_end_season_id`),
  KEY `matrix_start_season_id` (`matrix_start_season_id`),
  KEY `population_id` (`population_id`),
  KEY `studied_sex_id` (`studied_sex_id`),
  KEY `study_id` (`study_id`),
  CONSTRAINT `matrices_ibfk_1` FOREIGN KEY (`captivity_id`) REFERENCES `captivities` (`id`),
  CONSTRAINT `matrices_ibfk_2` FOREIGN KEY (`matrix_composition_id`) REFERENCES `matrix_compositions` (`id`),
  CONSTRAINT `matrices_ibfk_3` FOREIGN KEY (`matrix_end_season_id`) REFERENCES `seasons` (`id`),
  CONSTRAINT `matrices_ibfk_4` FOREIGN KEY (`matrix_start_season_id`) REFERENCES `seasons` (`id`),
  CONSTRAINT `matrices_ibfk_6` FOREIGN KEY (`population_id`) REFERENCES `populations` (`id`),
  CONSTRAINT `matrices_ibfk_7` FOREIGN KEY (`studied_sex_id`) REFERENCES `studied_sex` (`id`),
  CONSTRAINT `matrices_ibfk_8` FOREIGN KEY (`study_id`) REFERENCES `studies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30722 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matrix_compositions`
--

DROP TABLE IF EXISTS `matrix_compositions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matrix_compositions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comp_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matrix_stages`
--

DROP TABLE IF EXISTS `matrix_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matrix_stages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stage_order` smallint(6) DEFAULT NULL,
  `stage_id` int(11) DEFAULT NULL,
  `matrix_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `matrix_id` (`matrix_id`),
  KEY `stage_id` (`stage_id`),
  CONSTRAINT `matrix_stages_ibfk_1` FOREIGN KEY (`matrix_id`) REFERENCES `matrices` (`id`),
  CONSTRAINT `matrix_stages_ibfk_2` FOREIGN KEY (`stage_id`) REFERENCES `stages` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matrix_values`
--

DROP TABLE IF EXISTS `matrix_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matrix_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `column_number` smallint(6) DEFAULT NULL,
  `row_number` smallint(6) DEFAULT NULL,
  `transition_type_id` int(11) DEFAULT NULL,
  `value` float DEFAULT NULL,
  `matrix_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `matrix_id` (`matrix_id`),
  KEY `transition_type_id` (`transition_type_id`),
  CONSTRAINT `matrix_values_ibfk_1` FOREIGN KEY (`matrix_id`) REFERENCES `matrices` (`id`),
  CONSTRAINT `matrix_values_ibfk_2` FOREIGN KEY (`transition_type_id`) REFERENCES `transition_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `missing_data`
--

DROP TABLE IF EXISTS `missing_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `missing_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `missing_code` varchar(5) DEFAULT NULL,
  `missing_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_missing_data_missing_code` (`missing_code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `populations`
--

DROP TABLE IF EXISTS `populations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `populations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `species_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  `study_id` int(11) DEFAULT NULL,
  `species_author` varchar(64) DEFAULT NULL,
  `name` text,
  `ecoregion_id` int(11) DEFAULT NULL,
  `country` text,
  `continent_id` int(11) DEFAULT NULL,
  `geometries` text,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  `invasive_status_study_id` int(11) DEFAULT NULL,
  `invasive_status_selsewhere_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `continent_id` (`continent_id`),
  KEY `ecoregion_id` (`ecoregion_id`),
  KEY `species_id` (`species_id`),
  KEY `study_id` (`study_id`),
  KEY `ix_populations_id` (`id`),
  CONSTRAINT `populations_ibfk_1` FOREIGN KEY (`continent_id`) REFERENCES `continents` (`id`),
  CONSTRAINT `populations_ibfk_2` FOREIGN KEY (`ecoregion_id`) REFERENCES `ecoregions` (`id`),
  CONSTRAINT `populations_ibfk_4` FOREIGN KEY (`species_id`) REFERENCES `species` (`id`),
  CONSTRAINT `populations_ibfk_5` FOREIGN KEY (`study_id`) REFERENCES `studies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3464 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publication_missing_data`
--

DROP TABLE IF EXISTS `publication_missing_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `publication_missing_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `missing_data_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `missing_data_id` (`missing_data_id`),
  KEY `publication_id` (`publication_id`),
  CONSTRAINT `publication_missing_data_ibfk_1` FOREIGN KEY (`missing_data_id`) REFERENCES `missing_data` (`id`),
  CONSTRAINT `publication_missing_data_ibfk_2` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publication_purposes`
--

DROP TABLE IF EXISTS `publication_purposes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `publication_purposes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purpose_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `purpose_id` (`purpose_id`),
  CONSTRAINT `publication_purposes_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`),
  CONSTRAINT `publication_purposes_ibfk_2` FOREIGN KEY (`purpose_id`) REFERENCES `purposes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publications`
--

DROP TABLE IF EXISTS `publications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `publications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_type_id` int(11) DEFAULT NULL,
  `authors` text,
  `editors` text,
  `pub_title` text,
  `journal_book_conf` text,
  `year` smallint(6) DEFAULT NULL,
  `volume` text,
  `pages` text,
  `publisher` text,
  `city` text,
  `country` text,
  `institution` text,
  `DOI_ISBN` text,
  `name` text,
  `corresponding_author` text,
  `email` text,
  `purposes_id` int(11) DEFAULT NULL,
  `date_digitised` date DEFAULT NULL,
  `embargo` date DEFAULT NULL,
  `missing_data_id` int(11) DEFAULT NULL,
  `user_created` int(11) DEFAULT NULL,
  `user_modified` int(11) DEFAULT NULL,
  `timestamp_created` datetime DEFAULT NULL,
  `timestamp_modified` datetime DEFAULT NULL,
  `additional_source_string` text,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  `colour` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `missing_data_id` (`missing_data_id`),
  KEY `purposes_id` (`purposes_id`),
  KEY `user_created` (`user_created`),
  KEY `user_modified` (`user_modified`),
  CONSTRAINT `publications_ibfk_1` FOREIGN KEY (`missing_data_id`) REFERENCES `missing_data` (`id`),
  CONSTRAINT `publications_ibfk_2` FOREIGN KEY (`purposes_id`) REFERENCES `purposes` (`id`),
  CONSTRAINT `publications_ibfk_4` FOREIGN KEY (`user_created`) REFERENCES `users` (`id`),
  CONSTRAINT `publications_ibfk_5` FOREIGN KEY (`user_modified`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1293 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purposes`
--

DROP TABLE IF EXISTS `purposes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purposes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purpose_name` varchar(64) DEFAULT NULL,
  `purpose_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_purposes_purpose_name` (`purpose_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reproductive_repetition`
--

DROP TABLE IF EXISTS `reproductive_repetition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reproductive_repetition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repetition_name` text,
  PRIMARY KEY (`id`),
  KEY `ix_reproductive_repetition_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  `permissions` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_roles_default` (`default`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seasons`
--

DROP TABLE IF EXISTS `seasons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seasons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `season_name` varchar(64) DEFAULT NULL,
  `season_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_seasons_season_name` (`season_name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds`
--

DROP TABLE IF EXISTS `seeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `matrix_id` int(11) DEFAULT NULL,
  `matrix_a` text,
  PRIMARY KEY (`id`),
  KEY `ix_seeds_matrix_id` (`matrix_id`),
  CONSTRAINT `seeds_ibfk_1` FOREIGN KEY (`matrix_id`) REFERENCES `matrices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smalls`
--

DROP TABLE IF EXISTS `smalls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smalls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `small_name` varchar(200) DEFAULT NULL,
  `small_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_smalls_small_name` (`small_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `source_types`
--

DROP TABLE IF EXISTS `source_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `source_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_name` varchar(64) DEFAULT NULL,
  `source_description` text,
  `database_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_source_types_source_name` (`source_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `species`
--

DROP TABLE IF EXISTS `species`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `species` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iucn_status_id` int(11) DEFAULT NULL,
  `esa_status_id` int(11) DEFAULT NULL,
  `invasive_status` tinyint(1) DEFAULT NULL,
  `timestamp_created` datetime DEFAULT NULL,
  `timestamp_modified` datetime DEFAULT NULL,
  `user_created_id` int(11) DEFAULT NULL,
  `user_modified_id` int(11) DEFAULT NULL,
  `species_accepted` varchar(64) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  `GBIF_key` int(11) DEFAULT NULL,
  `image_path` text,
  `image_path2` text,
  `species_common` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_species_timestamp_modified` (`timestamp_modified`)
) ENGINE=InnoDB AUTO_INCREMENT=1974 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stage_type_classes`
--

DROP TABLE IF EXISTS `stage_type_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stage_type_classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_class` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_stage_type_classes_type_class` (`type_class`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stage_types`
--

DROP TABLE IF EXISTS `stage_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stage_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` text,
  `type_class_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `type_class_id` (`type_class_id`),
  KEY `ix_stage_types_id` (`id`),
  CONSTRAINT `stage_types_ibfk_1` FOREIGN KEY (`type_class_id`) REFERENCES `stage_type_classes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stages`
--

DROP TABLE IF EXISTS `stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `species_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  `stage_type_id` int(11) DEFAULT NULL,
  `name` text,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `species_id` (`species_id`),
  KEY `stage_type_id` (`stage_type_id`),
  KEY `ix_stages_id` (`id`),
  CONSTRAINT `stages_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`),
  CONSTRAINT `stages_ibfk_2` FOREIGN KEY (`species_id`) REFERENCES `species` (`id`),
  CONSTRAINT `stages_ibfk_3` FOREIGN KEY (`stage_type_id`) REFERENCES `stage_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statuses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_name` varchar(64) DEFAULT NULL,
  `status_description` text,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `ix_statuses_status_name` (`status_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `studied_sex`
--

DROP TABLE IF EXISTS `studied_sex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `studied_sex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sex_code` varchar(5) DEFAULT NULL,
  `sex_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_studied_sex_sex_code` (`sex_code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `studies`
--

DROP TABLE IF EXISTS `studies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `studies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publication_id` int(11) DEFAULT NULL,
  `study_duration` int(11) DEFAULT NULL,
  `study_start` int(11) DEFAULT NULL,
  `study_end` int(11) DEFAULT NULL,
  `number_populations` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `ix_studies_study_duration` (`study_duration`),
  CONSTRAINT `studies_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1921 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taxonomies`
--

DROP TABLE IF EXISTS `taxonomies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taxonomies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `species_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  `species_author` varchar(64) DEFAULT NULL,
  `species_accepted` varchar(64) DEFAULT NULL,
  `authority` text,
  `tpl_version` varchar(64) DEFAULT NULL,
  `infraspecies_accepted` varchar(64) DEFAULT NULL,
  `species_epithet_accepted` varchar(64) DEFAULT NULL,
  `genus_accepted` varchar(64) DEFAULT NULL,
  `genus` varchar(64) DEFAULT NULL,
  `family` varchar(64) DEFAULT NULL,
  `tax_order` varchar(64) DEFAULT NULL,
  `tax_class` varchar(64) DEFAULT NULL,
  `phylum` varchar(64) DEFAULT NULL,
  `kingdom` varchar(64) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `species_id` (`species_id`),
  KEY `ix_taxonomies_species_author` (`species_author`),
  CONSTRAINT `taxonomies_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`),
  CONSTRAINT `taxonomies_ibfk_2` FOREIGN KEY (`species_id`) REFERENCES `species` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1979 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `traits`
--

DROP TABLE IF EXISTS `traits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `traits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `species_id` int(11) DEFAULT NULL,
  `max_height` float DEFAULT NULL,
  `growth_type_id` int(11) DEFAULT NULL,
  `growth_form_raunkiaer_id` int(11) DEFAULT NULL,
  `reproductive_repetition_id` int(11) DEFAULT NULL,
  `dicot_monoc_id` int(11) DEFAULT NULL,
  `angio_gymno_id` int(11) DEFAULT NULL,
  `daves_growth_type_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `version_of_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `angio_gymno_id` (`angio_gymno_id`),
  KEY `daves_growth_type_id` (`daves_growth_type_id`),
  KEY `dicot_monoc_id` (`dicot_monoc_id`),
  KEY `growth_form_raunkiaer_id` (`growth_form_raunkiaer_id`),
  KEY `growth_type_id` (`growth_type_id`),
  KEY `reproductive_repetition_id` (`reproductive_repetition_id`),
  KEY `species_id` (`species_id`),
  KEY `version_of_id` (`version_of_id`),
  CONSTRAINT `traits_ibfk_1` FOREIGN KEY (`angio_gymno_id`) REFERENCES `angio_gymno` (`id`),
  CONSTRAINT `traits_ibfk_2` FOREIGN KEY (`daves_growth_type_id`) REFERENCES `daves_growth_types` (`id`),
  CONSTRAINT `traits_ibfk_3` FOREIGN KEY (`dicot_monoc_id`) REFERENCES `dicot_monoc` (`id`),
  CONSTRAINT `traits_ibfk_4` FOREIGN KEY (`growth_form_raunkiaer_id`) REFERENCES `growth_forms_raunkiaer` (`id`),
  CONSTRAINT `traits_ibfk_5` FOREIGN KEY (`growth_type_id`) REFERENCES `growth_types` (`id`),
  CONSTRAINT `traits_ibfk_6` FOREIGN KEY (`reproductive_repetition_id`) REFERENCES `reproductive_repetition` (`id`),
  CONSTRAINT `traits_ibfk_7` FOREIGN KEY (`species_id`) REFERENCES `species` (`id`),
  CONSTRAINT `traits_ibfk_8` FOREIGN KEY (`version_of_id`) REFERENCES `traits` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transition_types`
--

DROP TABLE IF EXISTS `transition_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transition_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `trans_code` varchar(64) DEFAULT NULL,
  `trans_description` text,
  PRIMARY KEY (`id`),
  KEY `ix_transition_types_trans_code` (`trans_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treatment_types`
--

DROP TABLE IF EXISTS `treatment_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treatment_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` text,
  PRIMARY KEY (`id`),
  KEY `ix_treatment_types_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=279 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `treatments`
--

DROP TABLE IF EXISTS `treatments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treatments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publication_id` int(11) DEFAULT NULL,
  `treatment_type_id` int(11) DEFAULT NULL,
  `name` text,
  `description` text,
  PRIMARY KEY (`id`),
  KEY `publication_id` (`publication_id`),
  KEY `treatment_type_id` (`treatment_type_id`),
  KEY `ix_treatments_id` (`id`),
  CONSTRAINT `treatments_ibfk_1` FOREIGN KEY (`publication_id`) REFERENCES `publications` (`id`),
  CONSTRAINT `treatments_ibfk_2` FOREIGN KEY (`treatment_type_id`) REFERENCES `treatment_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `about_me` text,
  `last_seen` datetime DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  `api_hash` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-23 11:39:45
