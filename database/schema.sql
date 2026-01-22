-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema shiftwise
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema shiftwise
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `shiftwise` DEFAULT CHARACTER SET utf8 ;
USE `shiftwise` ;

-- -----------------------------------------------------
-- Table `shiftwise`.`workers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shiftwise`.`workers` (
  `worker_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `max_shifts_per_week` TINYINT(3) UNSIGNED NOT NULL,
  `active` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (`worker_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shiftwise`.`shifts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shiftwise`.`shifts` (
  `shift_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `shift_name` VARCHAR(100) NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `required_workers` TINYINT(3) UNSIGNED NOT NULL,
  `undesirable` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (`shift_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shiftwise`.`schedules`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shiftwise`.`schedules` (
  `schedule_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `week_start_date` DATE NOT NULL,
  PRIMARY KEY (`schedule_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shiftwise`.`availability`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shiftwise`.`availability` (
  `availability_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `day_of_week` TINYINT(1) UNSIGNED NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `worker_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`availability_id`),
  INDEX `fk_availability_workers_idx` (`worker_id` ASC) VISIBLE,
  CONSTRAINT `fk_availability_workers`
    FOREIGN KEY (`worker_id`)
    REFERENCES `shiftwise`.`workers` (`worker_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `shiftwise`.`assignments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `shiftwise`.`assignments` (
  `assignment_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `assigned_date` DATE NOT NULL,
  `schedule_id` INT UNSIGNED NOT NULL,
  `shift_id` INT UNSIGNED NOT NULL,
  `worker_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`assignment_id`),
  INDEX `fk_assignments_schedules1_idx` (`schedule_id` ASC) VISIBLE,
  INDEX `fk_assignments_shifts1_idx` (`shift_id` ASC) VISIBLE,
  INDEX `fk_assignments_workers1_idx` (`worker_id` ASC) VISIBLE,
  CONSTRAINT `fk_assignments_schedules1`
    FOREIGN KEY (`schedule_id`)
    REFERENCES `shiftwise`.`schedules` (`schedule_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignments_shifts1`
    FOREIGN KEY (`shift_id`)
    REFERENCES `shiftwise`.`shifts` (`shift_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignments_workers1`
    FOREIGN KEY (`worker_id`)
    REFERENCES `shiftwise`.`workers` (`worker_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
