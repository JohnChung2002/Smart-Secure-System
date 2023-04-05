'''
in_out_logs
{
    "unlock_id": unlock_id,
    "timestamp": timestamp,
    "type": "Entry" | "Exit",
    "weight": weight,
    "height": height,
    "bmi": bmi,
}

unlock_logs
{
    "unlock_id": unlock_id,
    "timestamp": timestamp,
    "type": "Entry" | "Exit",
    "status": 0 | 1
}

configs
{
    "configs": value
}
{
    "alarm_status": 0 | 1,
    "weight_plus_minus": value,
    "person_count": value,
}

user_accounts
{
    "user_id": user_id,
    "username": username,
    "password": password,
    "role": "Admin" | "User",
    "key_card": key_card
}

user_details
{
    "user_id": user_id,
    "name": name,
    "age": age,
    "weight": weight,
    "height": height,
}
'''

CREATE DATABASE IF NOT EXISTS `smart_lock_system`;
USE `smart_lock_system`;
CREATE TABLE IF NOT EXISTS `user_details` (
  `user_id` INT(8) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `age` INT(3) NOT NULL,
  `weight` NUMERIC(5,2) NOT NULL,
  `height` NUMERIC(5,2) NOT NULL,
  `card_id` CHAR(8) NOT NULL,
  `type` ENUM("Human", "Pet") NOT NULL DEFAULT "User",
  PRIMARY KEY (`user_id`)
);
CREATE TABLE IF NOT EXISTS `user_accounts` (
  `user_id` INT(8) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` ENUM("Admin", "User") NOT NULL DEFAULT "User",
  `account_created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user_details`(`user_id`)
);
CREATE TABLE IF NOT EXISTS `unlock_logs` (
  `unlock_id` INT(8) NOT NULL AUTO_INCREMENT,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` ENUM("Entry", "Exit") NOT NULL,
  `status` ENUM("Success", "Failed", "Pending") NOT NULL DEFAULT "Pending",
  `user_id` INT(8),
  PRIMARY KEY (`unlock_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user_accounts`(`user_id`)
);
CREATE TABLE IF NOT EXISTS `in_out_logs` (
  `unlock_id` INT(8) NOT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` ENUM("Entry", "Exit") NOT NULL,
  `weight` NUMERIC(5,2) NOT NULL,
  `height` NUMERIC(5,2) NOT NULL,
  `bmi` NUMERIC(4,2) NOT NULL,
  PRIMARY KEY (`unlock_id`, `timestamp`),
  FOREIGN KEY (`unlock_id`) REFERENCES `unlock_logs`(`unlock_id`)
);
CREATE TABLE IF NOT EXISTS `remote_approval` (
  `unlock_id` INT(8) NOT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM("Approved", "Denied") NOT NULL,
  `user_id` INT(8) NOT NULL,
  PRIMARY KEY (`unlock_id`, `timestamp`),
  FOREIGN KEY (`unlock_id`) REFERENCES `unlock_logs`(`unlock_id`)
);
CREATE TABLE IF NOT EXISTS `configs` (
  `config` VARCHAR(255) NOT NULL,
  `value` VARCHAR(255) NOT NULL,
);
