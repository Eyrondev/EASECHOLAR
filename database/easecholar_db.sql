-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 02, 2025 at 03:13 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `easecholar_db`
--
-- CREATE DATABASE IF NOT EXISTS `easecholar_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `easecholar_db`;

-- --------------------------------------------------------

--
-- Table structure for table `applications`
--

CREATE TABLE `applications` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `scholarship_id` int(11) NOT NULL,
  `status` enum('PENDING','APPROVED','REJECTED','UNDER_REVIEW') DEFAULT NULL,
  `cover_letter` text DEFAULT NULL,
  `additional_info` text DEFAULT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `reviewer_notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `applications`
--

INSERT INTO `applications` (`id`, `student_id`, `scholarship_id`, `status`, `cover_letter`, `additional_info`, `submitted_at`, `reviewed_at`, `reviewer_notes`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 'APPROVED', 'adawdadwdfhvafsuytdfasiyfdasiyfgdafiysayifdyiags9gyuawgu99ugdasu9gdguaisgiuydaygiadyfayfiufyfyaudfyuayfgda', '', '2025-10-03 13:28:30', '2025-11-02 17:18:37', 'goods', '2025-10-03 13:28:30', NULL),
(2, 2, 1, 'APPROVED', 'i need this?aughdfcauykwdciuasgyduatwdfiaywfdiasudfgiyasfgasuyfggauisyfgauieyfaukgfasukvgfavuuhvafwhvafaffafw', '', '2025-11-02 21:30:06', '2025-11-02 21:31:04', 'awdaw', '2025-11-02 21:30:06', NULL),
(3, 2, 2, 'APPROVED', 'awdawdaksiydfa8owlyidfawilysfauadawdawdawdawdawdawawkegjhfguskhfggukashfgihasfasfar3wawdawdwadawdwadawd', '', '2025-11-02 21:44:41', '2025-11-02 21:45:15', 'aeawdaw', '2025-11-02 21:44:41', NULL),
(4, 3, 2, 'APPROVED', 'awdjajfduaiydfauiyduguifvgsfaduivgsfdadawdawdawdadawdawdawdadawduivhfsauhivgafseughvfasefawefewadawdawdawdawdaw', '', '2025-11-02 22:07:12', '2025-11-02 22:08:21', 'awdada', '2025-11-02 22:07:12', NULL),
(5, 3, 1, 'REJECTED', 'awdawdakhdfaiutdfaduktafdysajgdcajdchjgasdtufjajgdasitfudgasfutkasvgasdkuftasvgasufktvgadsyufgikasvasddasdassad', '', '2025-11-02 22:07:34', '2025-11-02 22:07:57', 'need cor', '2025-11-02 22:07:34', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `application_documents`
--

CREATE TABLE `application_documents` (
  `id` int(11) NOT NULL,
  `application_id` int(11) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `document_name` varchar(100) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_size` int(11) DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `application_documents`
--

INSERT INTO `application_documents` (`id`, `application_id`, `document_type`, `document_name`, `file_path`, `file_size`, `mime_type`, `uploaded_at`) VALUES
(1, 1, 'jpg', '8b98a3ea-522a-42bd-b6e5-f15a85189664.jpg', 'uploads\\student_documents\\1\\20251003_132830_4d2e76ba_8b98a3ea-522a-42bd-b6e5-f15a85189664.jpg', 37510, 'jpg', '2025-10-03 13:28:30'),
(2, 2, 'pdf', 'Individual Score Sheet.pdf', 'uploads\\student_documents\\5\\20251102_213006_dcddd1f2_Individual_Score_Sheet.pdf', 229228, 'pdf', '2025-11-02 21:30:06'),
(3, 3, 'pdf', 'RUBRIC FOR THESIS MANUSCRIPT.pdf', 'uploads\\student_documents\\5\\20251102_214441_793119ad_RUBRIC_FOR_THESIS_MANUSCRIPT.pdf', 200143, 'pdf', '2025-11-02 21:44:41'),
(4, 3, 'docx', 'solitation jlpc.docx', 'uploads\\student_documents\\5\\20251102_214441_7d55cd24_solitation_jlpc.docx', 81147, 'docx', '2025-11-02 21:44:41'),
(5, 4, 'pdf', 'Individual Score Sheet.pdf', 'uploads\\student_documents\\10\\20251102_220712_ec41467b_Individual_Score_Sheet.pdf', 229228, 'pdf', '2025-11-02 22:07:12'),
(6, 4, 'pdf', 'Mid-term Faculty Evaluation - Summary Report (1).pdf', 'uploads\\student_documents\\10\\20251102_220712_7a1ed855_Mid-term_Faculty_Evaluation_-_Summary_Report_1.pdf', 2532, 'pdf', '2025-11-02 22:07:12'),
(7, 5, 'pdf', 'Individual Score Sheet.pdf', 'uploads\\student_documents\\10\\20251102_220734_56fd3ff4_Individual_Score_Sheet.pdf', 229228, 'pdf', '2025-11-02 22:07:34');

-- --------------------------------------------------------

--
-- Table structure for table `providers`
--

CREATE TABLE `providers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `organization_name` varchar(100) NOT NULL,
  `organization_type` varchar(50) DEFAULT NULL,
  `website` varchar(200) DEFAULT NULL,
  `tax_id` varchar(20) DEFAULT NULL,
  `registration_number` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `contact_title` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `verification_documents` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `business_registration_document` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `providers`
--

INSERT INTO `providers` (`id`, `user_id`, `organization_name`, `organization_type`, `website`, `tax_id`, `registration_number`, `address`, `city`, `state`, `zip_code`, `contact_person`, `contact_title`, `description`, `logo`, `is_verified`, `verification_documents`, `created_at`, `updated_at`, `business_registration_document`) VALUES
(1, 2, 'ABC Foundation', 'Non-Profit', 'https://abcfoundation.org', NULL, NULL, 'dad', 'awdwa', 'ada', '13213', 'Juan Dela Cruz', 'awdwa', 'Supporting education through scholarships', NULL, 1, NULL, '2025-09-23 13:46:34', '2025-10-03 01:47:54', NULL),
(2, 9, 'eyrokorg', 'private_company', 'http://127.0.0.1:5000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'awdawawdaw', NULL, 1, NULL, '2025-11-02 17:12:58', '2025-11-02 17:12:58', 'business_reg_9_c45edea58f0fe33e.pdf');

-- --------------------------------------------------------

--
-- Table structure for table `saved_scholarships`
--

CREATE TABLE `saved_scholarships` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `scholarship_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `saved_scholarships`
--

INSERT INTO `saved_scholarships` (`id`, `student_id`, `scholarship_id`, `created_at`) VALUES
(6, 1, 1, '2025-10-03 19:25:56');

-- --------------------------------------------------------

--
-- Table structure for table `scholarships`
--

CREATE TABLE `scholarships` (
  `id` int(11) NOT NULL,
  `provider_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `scholarship_type` enum('FULL_SCHOLARSHIP','PARTIAL_SCHOLARSHIP','MONTHLY_ALLOWANCE','ONE_TIME_GRANT') NOT NULL,
  `amount` float NOT NULL,
  `currency` varchar(3) DEFAULT NULL,
  `eligibility_criteria` text DEFAULT NULL,
  `required_documents` text DEFAULT NULL,
  `application_deadline` datetime DEFAULT NULL,
  `scholarship_duration` varchar(50) DEFAULT NULL,
  `available_slots` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `scholarships`
--

INSERT INTO `scholarships` (`id`, `provider_id`, `title`, `description`, `scholarship_type`, `amount`, `currency`, `eligibility_criteria`, `required_documents`, `application_deadline`, `scholarship_duration`, `available_slots`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 1, 'TULONG EDUCATION', 'dwadad', 'PARTIAL_SCHOLARSHIP', 3000, NULL, 'awdawdaw', 'adawdaw', '2025-11-27 00:00:00', NULL, 12, 1, '2025-10-02 23:52:48', '2025-11-02 21:29:28'),
(2, 2, 'wadaw', 'awdawwa', 'PARTIAL_SCHOLARSHIP', 1000, NULL, '2.00', 'wadawd', '2025-11-21 00:00:00', NULL, 12, 1, '2025-11-02 21:43:34', '2025-11-02 21:43:34');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `student_number` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `current_school` varchar(100) DEFAULT NULL,
  `school_name` varchar(200) DEFAULT NULL,
  `course` varchar(200) DEFAULT NULL,
  `year_level` varchar(20) DEFAULT NULL,
  `current_grade_level` varchar(20) DEFAULT NULL,
  `gpa` float DEFAULT NULL,
  `expected_graduation_date` date DEFAULT NULL,
  `family_income` float DEFAULT NULL,
  `guardian_name` varchar(100) DEFAULT NULL,
  `guardian_phone` varchar(20) DEFAULT NULL,
  `guardian_email` varchar(120) DEFAULT NULL,
  `emergency_contact` varchar(100) DEFAULT NULL,
  `emergency_phone` varchar(20) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `cor_document` varchar(255) DEFAULT NULL COMMENT 'Certificate of Registration filename',
  `coe_document` varchar(255) DEFAULT NULL COMMENT 'Certificate of Enrollment filename',
  `transcript_document` varchar(255) DEFAULT NULL COMMENT 'Academic Transcript filename'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `user_id`, `student_id`, `student_number`, `date_of_birth`, `gender`, `address`, `city`, `state`, `zip_code`, `current_school`, `school_name`, `course`, `year_level`, `current_grade_level`, `gpa`, `expected_graduation_date`, `family_income`, `guardian_name`, `guardian_phone`, `guardian_email`, `emergency_contact`, `emergency_phone`, `bio`, `profile_picture`, `created_at`, `updated_at`, `cor_document`, `coe_document`, `transcript_document`) VALUES
(1, 1, NULL, NULL, NULL, 'Female', NULL, NULL, NULL, NULL, 'University of the Philippines', NULL, NULL, 'College Junior', 'College Junior', NULL, NULL, 4000, 'try', NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-23 13:46:33', '2025-09-23 13:46:33', NULL, NULL, NULL),
(2, 5, NULL, '2022-0212', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'NORZAGARAY COLLEGE', 'BSCS', '4th Year', NULL, 1.29, '2027-05-12', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-09-24 11:36:57', '2025-09-24 11:36:57', NULL, NULL, NULL),
(3, 10, NULL, '2022-0215', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'NORZAGARAY COLLEGE', 'BSCS', '4', NULL, 1.39, '2026-05-02', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-11-02 17:14:08', '2025-11-02 17:14:08', 'cor_10_45b50e0c7134e611.pdf', 'coe_10_4f7030745a8209da.pdf', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `student_documents`
--

CREATE TABLE `student_documents` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `document_name` varchar(100) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_size` int(11) DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `system_settings`
--

CREATE TABLE `system_settings` (
  `id` int(11) NOT NULL,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `system_settings`
--

INSERT INTO `system_settings` (`id`, `setting_key`, `setting_value`, `updated_at`) VALUES
(1, 'maintenance_mode', '0', '2025-10-03 10:21:13');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `user_type` enum('STUDENT','PROVIDER','ADMIN') NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `verification_token` varchar(100) DEFAULT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_expiry` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `user_type`, `first_name`, `last_name`, `phone_number`, `is_active`, `is_verified`, `verification_token`, `reset_token`, `reset_token_expiry`, `created_at`, `updated_at`, `last_login`) VALUES
(1, 'student@gmail.com', 'b1234ef905a57887663c10e064bfb1510ff8881f22d679bf881ee09d8e9072406cc6f8527054c7038d0d9fed21c37c95df5981a1eb406a01e993e6698581cc19af2fa180e4fafdc55ba8266a52a6540d5d572e5b03a2b970e3e4b42f299f2731', 'STUDENT', 'Maria', 'Santos', '09171234567', 1, 1, '4mHCbpP2jHRFB6SIEsp4jz1vZkd4IW9vUhtj9CJN5rI', NULL, NULL, '2025-09-23 13:46:33', '2025-10-02 19:52:30', '2025-11-02 17:15:54'),
(2, 'provider@gmail.com', 'b1234ef905a57887663c10e064bfb1510ff8881f22d679bf881ee09d8e9072406cc6f8527054c7038d0d9fed21c37c95df5981a1eb406a01e993e6698581cc19af2fa180e4fafdc55ba8266a52a6540d5d572e5b03a2b970e3e4b42f299f2731', 'PROVIDER', 'Juan', 'Dela Cruz', '09187654321', 1, 1, '-rEdTAiWN3ASkHKxCNCCfBVAmwoJ30nZsx2_Vu4FVng', NULL, NULL, '2025-09-23 13:46:34', '2025-10-03 01:47:54', '2025-11-02 22:07:43'),
(4, 'admin@gmail.com', 'b1234ef905a57887663c10e064bfb1510ff8881f22d679bf881ee09d8e9072406cc6f8527054c7038d0d9fed21c37c95df5981a1eb406a01e993e6698581cc19af2fa180e4fafdc55ba8266a52a6540d5d572e5b03a2b970e3e4b42f299f2731', 'ADMIN', 'System', 'Administrator', NULL, 1, 1, NULL, NULL, NULL, '2025-09-24 11:23:24', '2025-09-24 11:23:24', '2025-11-02 22:09:35'),
(5, 'troy@gmail.com', 'b1234ef905a57887663c10e064bfb1510ff8881f22d679bf881ee09d8e9072406cc6f8527054c7038d0d9fed21c37c95df5981a1eb406a01e993e6698581cc19af2fa180e4fafdc55ba8266a52a6540d5d572e5b03a2b970e3e4b42f299f2731', 'STUDENT', 'troy', 'jan', '09123456787', 1, 1, 'KRbvBL8FwndT-IgyZgGNPojBIJB4BHT8tw3yhQmWxrQ', NULL, NULL, '2025-09-24 11:36:57', '2025-11-02 21:28:28', '2025-11-02 21:46:56'),
(9, 'aaron@gmail.com', '72d667ecf63d5e62aa9a866d5cdcaee27a16d3aa90164b28760a0064377df214564b34445c453d9ab54cbcbfa54b258ec96f193b9d338842ee5a7b7f6cb34b67f927f31ae7e5c230eaf12aadb98f115d8896bf6270fda2cea7c44f988bf72f58', 'PROVIDER', 'try', 'try', '09932326567', 1, 1, 'WWRpS846A4E228oJwzKg3xGGYXPYn8cYU4AR_oZXzCU', NULL, NULL, '2025-11-02 17:12:58', '2025-11-02 21:42:37', '2025-11-02 22:10:49'),
(10, 'aaron1@gmail.com', 'b68692f7072dd9b4a4e67015d28b80e6e7eff658e16b877ccb8410edf8d328db8084ec0a1b97bc3f22e176f21b2368a7196555749df9ad4e5300c8d9a04aac757ffd363ba197620045ed7e5b08bfb7a6ec85dc819bbfd043648f0f0e66dbce2d', 'STUDENT', 'Aaron', 'Jimenez', '09932326567', 1, 1, '25KaqniTwRgB1tjxZTSqMEJLRTTnFwBUQ5JIj-rhHDI', NULL, NULL, '2025-11-02 17:14:08', '2025-11-02 22:06:05', '2025-11-02 22:08:58');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `applications`
--
ALTER TABLE `applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `scholarship_id` (`scholarship_id`);

--
-- Indexes for table `application_documents`
--
ALTER TABLE `application_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `application_id` (`application_id`);

--
-- Indexes for table `providers`
--
ALTER TABLE `providers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_providers_org_name` (`organization_name`);

--
-- Indexes for table `saved_scholarships`
--
ALTER TABLE `saved_scholarships`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_save` (`student_id`,`scholarship_id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `scholarship_id` (`scholarship_id`);

--
-- Indexes for table `scholarships`
--
ALTER TABLE `scholarships`
  ADD PRIMARY KEY (`id`),
  ADD KEY `provider_id` (`provider_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `student_documents`
--
ALTER TABLE `student_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indexes for table `system_settings`
--
ALTER TABLE `system_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `setting_key` (`setting_key`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `applications`
--
ALTER TABLE `applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `application_documents`
--
ALTER TABLE `application_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `providers`
--
ALTER TABLE `providers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `saved_scholarships`
--
ALTER TABLE `saved_scholarships`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `scholarships`
--
ALTER TABLE `scholarships`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `student_documents`
--
ALTER TABLE `student_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `system_settings`
--
ALTER TABLE `system_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `applications`
--
ALTER TABLE `applications`
  ADD CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  ADD CONSTRAINT `applications_ibfk_2` FOREIGN KEY (`scholarship_id`) REFERENCES `scholarships` (`id`);

--
-- Constraints for table `application_documents`
--
ALTER TABLE `application_documents`
  ADD CONSTRAINT `application_documents_ibfk_1` FOREIGN KEY (`application_id`) REFERENCES `applications` (`id`);

--
-- Constraints for table `providers`
--
ALTER TABLE `providers`
  ADD CONSTRAINT `providers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `saved_scholarships`
--
ALTER TABLE `saved_scholarships`
  ADD CONSTRAINT `saved_scholarships_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saved_scholarships_ibfk_2` FOREIGN KEY (`scholarship_id`) REFERENCES `scholarships` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `scholarships`
--
ALTER TABLE `scholarships`
  ADD CONSTRAINT `scholarships_ibfk_1` FOREIGN KEY (`provider_id`) REFERENCES `providers` (`id`);

--
-- Constraints for table `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `student_documents`
--
ALTER TABLE `student_documents`
  ADD CONSTRAINT `student_documents_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
