CREATE DATABASE SmartFarmDB;

USE SmartFarmDB;

-- Users Table
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,  -- Ensuring username is unique
    password VARCHAR(255) NOT NULL,  -- Store password
    email VARCHAR(255) NOT NULL UNIQUE,  -- Optional: Add email as a unique identifier for login
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO Users (username, password, email) 
VALUES ('user123', '123', 'user123@example.com');

DROP TABLE IF EXISTS Devices;
-- Devices Table
CREATE TABLE Devices (
    device_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    user_id INT NOT NULL,
    device_Name VARCHAR(255)NOT NULL UNIQUE,
    device_status ENUM('offline', 'online') DEFAULT 'offline',
    last_sync_time TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
INSERT INTO Devices (user_id, device_Name) 
VALUES ('1', 'abcdefg');



-- Device Data Table
CREATE TABLE DeviceData (
    data_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    device_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_payload JSON,
    status VARCHAR(50) DEFAULT 'processed',
    FOREIGN KEY (device_id) REFERENCES Devices(device_id)
);

DROP PROCEDURE IF EXISTS Authenticate;
-- Procedure for authentication
DELIMITER $$

CREATE PROCEDURE Authenticate(IN input_username VARCHAR(255), IN input_password VARCHAR(255))
BEGIN
    SELECT * FROM Users
    WHERE Username = input_username AND Password = input_password;
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE Registration(
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_device_name VARCHAR(255)
)
BEGIN
    -- Declare the variable to store the new user_id
    DECLARE new_user_id INT;

    -- Step 1: Insert into Users table
    INSERT INTO Users (username, password, email) 
    VALUES (p_username, p_password, p_email);
    
    -- Step 2: Get the user_id of the newly inserted user
    SET new_user_id = LAST_INSERT_ID();
    
    -- Step 3: Insert into Devices table
    INSERT INTO Devices (user_id, device_Name) 
    VALUES (new_user_id, p_device_name);
    
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE CheckUserExistence(
    IN p_username VARCHAR(255),
    IN p_email VARCHAR(255),
    OUT p_user_count INT
)
BEGIN
    -- Query to count users with matching username or email
    SELECT COUNT(*) 
    INTO p_user_count
    FROM Users 
    WHERE username = p_username OR email = p_email;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE insertSensorData(
    IN p_device_name VARCHAR(255),
    IN p_data_payload JSON
)
BEGIN
    DECLARE device_id INT;

    -- Step 1: Get the device_id from the Devices table based on the device_name
    SELECT device_id INTO device_id
    FROM Devices
    WHERE device_Name = p_device_name
    LIMIT 1; -- Ensure only one device is matched

    -- Step 2: Check if the device exists
    IF device_id IS NOT NULL THEN
        -- Step 3: Insert data into DeviceData table
        INSERT INTO DeviceData (device_id, data_payload)
        VALUES (device_id, p_data_payload);
    ELSE
        -- Step 4: If device doesn't exist, raise an error (or handle accordingly)
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Device not found';
    END IF;

END $$

DELIMITER $$

CREATE PROCEDURE retrieveDeviceDataByUserName(
    IN p_username VARCHAR(255)
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_device_id INT;

    -- Step 1: Get the user_id based on the username
    SELECT user_id INTO v_user_id
    FROM Users
    WHERE username = p_username
    LIMIT 1;  -- Ensure only one result is returned

    -- Step 2: Check if the user exists
    IF v_user_id IS NOT NULL THEN
        -- Step 3: Get the device_id based on the user_id
        SELECT device_id INTO v_device_id
        FROM Devices
        WHERE user_id = v_user_id
        LIMIT 1;  -- Ensure only one device is returned

        -- Step 4: Check if the device exists
        IF v_device_id IS NOT NULL THEN
            -- Step 5: Retrieve the data_payload from DeviceData based on the device_id
            SELECT data_payload
            FROM DeviceData
            WHERE device_id = v_device_id;
        ELSE
            -- Step 6: If no device is found, raise an error
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No device found for this user';
        END IF;
    ELSE
        -- Step 7: If the user does not exist, raise an error
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

END $$

DELIMITER ;



