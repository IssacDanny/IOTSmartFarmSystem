CREATE DATABASE SmartFarmDB;
USE SmartFarmDB;

####################################ResetIncaseOfMistake#################################
DROP TABLE IF EXISTS DeviceData;
DROP TABLE IF EXISTS Devices;
DROP TABLE IF EXISTS Users;
DROP PROCEDURE IF EXISTS Registration;
DROP PROCEDURE IF EXISTS CheckUserExistence;
DROP PROCEDURE IF EXISTS FetchUser;
DROP PROCEDURE IF EXISTS insertSensorData;
DROP PROCEDURE IF EXISTS RetrieveNewSensorData;
DROP PROCEDURE IF EXISTS RetrieveHistoricalSensorData;
DROP PROCEDURE IF EXISTS UpdateAutomationRule;
DROP PROCEDURE IF EXISTS RetrieveAutomationRule;
DROP PROCEDURE IF EXISTS RetrieveLatestSensorData;

####################################ViewData############################################
SELECT * FROM Users;
SELECT * FROM Devices;
SELECT * FROM DeviceData;

###################################InsertDummyData######################################
INSERT INTO Users (username, password, email) VALUES 
('alice', 'pass123', 'alice@example.com'),
('bob', 'pass456', 'bob@example.com'),
('charlie', 'pass789', 'charlie@example.com'),
('dave', 'passabc', 'dave@example.com'),
('eve', 'passdef', 'eve@example.com'),
('frank', 'passghi', 'frank@example.com'),
('grace', 'passjkl', 'grace@example.com'),
('heidi', 'passmno', 'heidi@example.com'),
('ivan', 'passpqr', 'ivan@example.com'),
('judy', 'passstu', 'judy@example.com');

INSERT INTO Devices (user_id, device_Name, AutomationRule) VALUES 
(1, 'alice_device', JSON_OBJECT(
    'Header', JSON_OBJECT(
        'DescriptionType', 'RuleDescription',
        'OperationType', 'ADD',
        'User', 'alice'
    ),
    'Body', JSON_OBJECT(
        'Rule1', JSON_OBJECT(
            'Condition', JSON_OBJECT(
                'Type', 'SetThreshold',
                'Description', JSON_OBJECT(
                    'Operation', '>=',
                    'Threshold', 46,
                    'Kind', 'Humidity'
                )
            ),
            'Action', JSON_OBJECT(
                'Header', JSON_OBJECT(
                    'DescriptionType', 'ActivationDescription',
                    'User', 'alice'
                ),
                'Body', JSON_OBJECT(
                    'CommandType', 'ActivePump',
                    'Parameter', JSON_OBJECT(
                        'Pump_1', 1 
                    )
                )
            )
        )
    )
)),
(2, 'bob_device',JSON_OBJECT(
    'Header', JSON_OBJECT(
        'DescriptionType', 'RuleDescription',
        'OperationType', 'ADD',
        'User', 'bob'
    ),
    'Body', JSON_OBJECT(
        'Rule1', JSON_OBJECT(
            'Condition', JSON_OBJECT(
                'Type', 'SetThreshold',
                'Description', JSON_OBJECT(
                    'Operation', '<=',
                    'Threshold', 25,
                    'Kind', 'Temperature'
                )
            ),
            'Action', JSON_OBJECT(
                'Header', JSON_OBJECT(
                    'DescriptionType', 'ActivationDescription',
                    'User', 'bob'
                ),
                'Body', JSON_OBJECT(
                    'CommandType', 'ActiveFan',
                    'Parameter', JSON_OBJECT(
                        'Fan', 1
                    )
                )
            )
        )
    )
)),
(3, 'charlie_device', JSON_OBJECT()),
(4, 'dave_device', JSON_OBJECT()),
(5, 'eve_device', JSON_OBJECT()),
(6, 'frank_device', JSON_OBJECT()),
(7, 'grace_device', JSON_OBJECT()),
(8, 'heidi_device', JSON_OBJECT()),
(9, 'ivan_device', JSON_OBJECT()),
(10, 'judy_device', JSON_OBJECT());

-- Assume IDs 1 and 2 correspond to alice_device and bob_device
INSERT INTO DeviceData (device_id, data_payload) VALUES
(1, JSON_OBJECT('Temperature', 22, 'Humidity', 55, 'Moisture', 33, 'Lux', 1000, 'GDD', 150, 'Status', 1, 'Pump_1', 0, 'Fan', 0)),
(1, JSON_OBJECT('Temperature', 27, 'Humidity', 60, 'Moisture', 35, 'Lux', 1200, 'GDD', 180, 'Status', 1, 'Pump_1', 0, 'Fan', 0)),
(2, JSON_OBJECT('Temperature', 29, 'Humidity', 85, 'Moisture', 40, 'Lux', 900, 'GDD', 200, 'Status', 1, 'Pump_1', 0, 'Fan', 0));

###################################RegionForTableCreationQuery###########################
-- Users Table
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Devices Table
CREATE TABLE Devices (
    device_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    user_id INT NOT NULL,
    device_Name VARCHAR(255)NOT NULL UNIQUE,
    AutomationRule Json NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);



-- Device Data Table
CREATE TABLE DeviceData (
    data_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    device_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_payload JSON NOT NULL,
    FOREIGN KEY (device_id) REFERENCES Devices(device_id)
);

##################################Registration procedure################################
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
    INSERT INTO Devices (user_id, device_Name, AutomationRule) 
    VALUES (new_user_id, p_device_name, JSON_OBJECT());
    
END $$
DELIMITER ;

#################################CheckUserExistence######################################
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
#################################FetchUser procedure#####################################
DELIMITER $$ 
CREATE PROCEDURE FetchUser()
BEGIN
	SELECT 
        u.username,
        u.password,
        u.email,
        d.device_Name,
        d.AutomationRule
    FROM 
        Users u
    LEFT JOIN 
        Devices d ON u.user_id = d.user_id;
END;

################################InsertSensorData#########################################
DELIMITER $$
CREATE PROCEDURE insertSensorData(
	IN DeviceName VARCHAR(225),
    In payload Json
)
BEGIN
	DECLARE dev_id INT;

    -- Get device_id from Devices table
    SELECT device_id INTO dev_id
    FROM Devices
    WHERE device_Name = DeviceName;

    -- Insert the data into DeviceData
    INSERT INTO DeviceData (device_id, data_payload)
    VALUES (dev_id, payload);
END $$
DELIMITER ;

################################RetrieveNewSensorData#######################################

DELIMITER $$
CREATE PROCEDURE RetrieveNewSensorData(
	IN UserName VARCHAR(225),
    IN LastSeen TIMESTAMP
)
BEGIN
	SELECT 
        dd.timestamp,
        dd.data_payload
    FROM 
        Users u
    INNER JOIN 
        Devices d ON u.user_id = d.user_id
    INNER JOIN 
        DeviceData dd ON d.device_id = dd.device_id
    WHERE 
        u.username = UserName
        AND dd.timestamp > LastSeen
    ORDER BY 
        dd.timestamp ASC;
END$$
DELIMITER ;

################################RetrieveHistoricalSensorData##############################
DELIMITER $$
CREATE PROCEDURE RetrieveHistoricalSensorData(
	IN UserName VARCHAR(225),
    IN LastSeen TIMESTAMP
)
BEGIN
	SELECT 
        dd.timestamp,
        dd.data_payload
    FROM 
        Users u
    INNER JOIN 
        Devices d ON u.user_id = d.user_id
    INNER JOIN 
        DeviceData dd ON d.device_id = dd.device_id
    WHERE 
        u.username = UserName
        AND dd.timestamp <= LastSeen
    ORDER BY 
        dd.timestamp ASC;
END$$
DELIMITER ;

###############################UpdateAutomationRule########################################
DELIMITER $$
CREATE PROCEDURE UpdateAutomationRule(
	IN DeviceName VARCHAR(225),
    IN RuleDecription Json
)
BEGIN
	UPDATE Devices
    SET AutomationRule = RuleDecription
    WHERE device_Name = DeviceName;
END $$
DELIMITER ;

###############################RetrieveAutomationRule######################################
DELIMITER $$
CREATE PROCEDURE RetrieveAutomationRule(
	IN p_DeviceName VARCHAR(225)
)
BEGIN
	SELECT AutomationRule
    FROM Devices
    Where device_Name = p_DeviceName;
END $$
DELIMITER ;

#############################RetrieveLatestSensorData#####################################
DELIMITER $$

CREATE PROCEDURE RetrieveLatestSensorData(
    IN input_device_name VARCHAR(255)
)
BEGIN
    SELECT 
        dd.data_id,
        dd.timestamp,
        dd.data_payload
    FROM 
        Devices d
    INNER JOIN 
        DeviceData dd ON d.device_id = dd.device_id
    WHERE 
        d.device_Name = input_device_name
    ORDER BY 
        dd.timestamp DESC
    LIMIT 1;
END$$

DELIMITER ;



