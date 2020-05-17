-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 11, 2020 at 11:27 AM
-- Server version: 8.0.18
-- PHP Version: 7.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `student_support_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `studentsupport_departments`
--

DROP TABLE IF EXISTS `studentsupport_departments`;
CREATE TABLE IF NOT EXISTS `studentsupport_departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(100) NOT NULL,
  `accronym` varchar(10) NOT NULL,
  `is_mid_sem_live` tinyint(1) NOT NULL,
  `is_end_sem_live` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `studentsupport_departments`
--

INSERT INTO `studentsupport_departments` (`id`, `dept_name`, `accronym`, `is_mid_sem_live`, `is_end_sem_live`) VALUES
(1, 'Computer Engineering', 'CE', 1, 1),
(2, 'Information Technology', 'IT', 1, 1),
(3, 'Electronics & Communication', 'EC', 1, 1),
(4, 'Civil Engineering', 'CIVIL', 1, 1),
(5, 'Production Engineering', 'PROD', 1, 1),
(6, 'Mechanical Engineering', 'MECH', 1, 1),
(7, 'General Department', 'GNRL', 1, 1),
(8, 'Applied Mechanics', 'AM', 1, 1);

-- --------------------------------------------------------

-- Table structure for table `studentsupport_end_sem_feedback_questions`
--

DROP TABLE IF EXISTS `studentsupport_end_sem_feedback_questions`;
CREATE TABLE IF NOT EXISTS `studentsupport_end_sem_feedback_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_text` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `studentsupport_end_sem_feedback_questions`
--

INSERT INTO `studentsupport_end_sem_feedback_questions` (`id`, `question_text`) VALUES
(1, 'Has the teacher covered relevant topics beyond the syllabus?'),
(2, 'Effectiveness of Teacher in terms of:\r\n(a) Technical Content /Course Content\r\n(b) Communication Skills\r\n(c) Use of Teaching Aids'),
(3, 'Pace on which contents were covered'),
(4, 'Motivation and inspiration for students to learn'),
(5, 'Support for the development of Students skill \r\n(a) Practical demonstration\r\n(b) Hands-on training'),
(6, 'Clarity of expectations of students'),
(7, 'Feedback provided on students progress'),
(8, 'Has the Teacher covered the entire syllabus as prescribed by University / College / Board?'),
(9, 'Willingness to offer help and advice to students.');

-- --------------------------------------------------------

--
-- Table structure for table `studentsupport_mid_sem_feedback_questions`
--

DROP TABLE IF EXISTS `studentsupport_mid_sem_feedback_questions`;
CREATE TABLE IF NOT EXISTS `studentsupport_mid_sem_feedback_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_text` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `studentsupport_mid_sem_feedback_questions`
--

INSERT INTO `studentsupport_mid_sem_feedback_questions` (`id`, `question_text`) VALUES
(1, 'Has the teacher covered relevant topics beyond the syllabus?'),
(2, 'Effectiveness of Teacher in terms of:\r\n(a) Technical Content /Course Content\r\n(b) Communication Skills\r\n(c) Use of Teaching Aids'),
(3, 'Pace on which contents were covered'),
(4, 'Motivation and inspiration for students to learn'),
(5, 'Support for the development of Students skill \r\n(a) Practical demonstration\r\n(b) Hands-on training'),
(6, 'Clarity of expectations of students'),
(7, 'Feedback provided on students progress'),
(8, 'Has the Teacher covered the entire syllabus as prescribed by University / College / Board?'),
(9, 'Willingness to offer help and advice to students.');

-- --------------------------------------------------------
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
