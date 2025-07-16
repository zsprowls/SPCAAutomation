
-- MySQL Schema for Pathways for Care Database

CREATE DATABASE IF NOT EXISTS pathways_care;
USE pathways_care;

-- Main pathways data table
CREATE TABLE IF NOT EXISTS pathways_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    AID VARCHAR(50) NOT NULL,
    Name VARCHAR(255),
    Species VARCHAR(100),
    Breed VARCHAR(255),
    Color VARCHAR(255),
    Sex VARCHAR(50),
    Age VARCHAR(100),
    Weight VARCHAR(100),
    `Intake Date` DATE,
    `Days in System` INT,
    `Location ` VARCHAR(255),
    `Foster Attempted` VARCHAR(10),
    `Transfer Attempted` VARCHAR(10),
    `Communications Team Attempted` VARCHAR(10),
    `Welfare Notes` TEXT,
    `Medical Notes` TEXT,
    `Behavior Notes` TEXT,
    `Adoption Notes` TEXT,
    `Transfer Notes` TEXT,
    `Foster Notes` TEXT,
    `Return Notes` TEXT,
    `Euthanasia Notes` TEXT,
    `Other Notes` TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_aid (AID),
    INDEX idx_name (Name),
    INDEX idx_species (Species),
    INDEX idx_intake_date (`Intake Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Animal inventory table
CREATE TABLE IF NOT EXISTS animal_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    AnimalNumber VARCHAR(50),
    Location VARCHAR(255),
    SubLocation VARCHAR(255),
    Status VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_animal_number (AnimalNumber),
    INDEX idx_location (Location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Metadata table
CREATE TABLE IF NOT EXISTS metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Image cache table
CREATE TABLE IF NOT EXISTS image_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id VARCHAR(50) NOT NULL,
    image_urls JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_animal_id (animal_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert initial metadata
INSERT IGNORE INTO metadata (`key`, value) VALUES 
('last_updated', NOW()),
('database_version', '2.0'),
('migration_date', NOW());
