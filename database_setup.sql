-- ============================================================
-- ORGAN DONATION PROCUREMENT - Database Setup
-- Run this file in MySQL to create and populate the database
-- ============================================================

CREATE DATABASE IF NOT EXISTS dbms_project;
USE dbms_project;

-- ─── DROP TABLES (order matters due to FK constraints) ───────
DROP TABLE IF EXISTS `log`;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Organ_available;
DROP TABLE IF EXISTS Organization_head;
DROP TABLE IF EXISTS Doctor_phone_no;
DROP TABLE IF EXISTS Organization_phone_no;
DROP TABLE IF EXISTS Donor;
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Organization;
DROP TABLE IF EXISTS User_phone_no;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS login;

-- ─── CREATE TABLES ───────────────────────────────────────────

CREATE TABLE login (
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE User (
    User_ID          INT          NOT NULL,
    Name             VARCHAR(50)  NOT NULL,
    Date_of_Birth    DATE         NOT NULL,
    Medical_insurance INT,
    Medical_history  VARCHAR(100),
    Street           VARCHAR(50),
    City             VARCHAR(30),
    State            VARCHAR(30),
    PRIMARY KEY (User_ID)
);

CREATE TABLE User_phone_no (
    User_ID  INT          NOT NULL,
    phone_no VARCHAR(15),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID) ON DELETE CASCADE
);

CREATE TABLE Organization (
    Organization_ID   INT         NOT NULL,
    Organization_name VARCHAR(50) NOT NULL,
    Location          VARCHAR(30),
    Government_approved INT,          -- 0 or 1
    PRIMARY KEY (Organization_ID)
);

CREATE TABLE Doctor (
    Doctor_ID       INT         NOT NULL,
    Doctor_Name     VARCHAR(50) NOT NULL,
    Department_Name VARCHAR(50) NOT NULL,
    organization_ID INT         NOT NULL,
    FOREIGN KEY (organization_ID) REFERENCES Organization(Organization_ID) ON DELETE CASCADE,
    PRIMARY KEY (Doctor_ID)
);

CREATE TABLE Doctor_phone_no (
    Doctor_ID INT         NOT NULL,
    Phone_no  VARCHAR(15),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
);

CREATE TABLE Organization_phone_no (
    Organization_ID INT         NOT NULL,
    Phone_no        VARCHAR(15),
    FOREIGN KEY (Organization_ID) REFERENCES Organization(Organization_ID) ON DELETE CASCADE
);

CREATE TABLE Organization_head (
    Organization_ID INT         NOT NULL,
    Employee_ID     INT         NOT NULL,
    Name            VARCHAR(50) NOT NULL,
    Date_of_joining DATE        NOT NULL,
    Term_length     INT         NOT NULL,
    FOREIGN KEY (Organization_ID) REFERENCES Organization(Organization_ID) ON DELETE CASCADE,
    PRIMARY KEY (Organization_ID, Employee_ID)
);

CREATE TABLE Patient (
    Patient_ID             INT         NOT NULL,
    organ_req              VARCHAR(30) NOT NULL,
    reason_of_procurement  VARCHAR(50),
    Doctor_ID              INT         NOT NULL,
    User_ID                INT         NOT NULL,
    FOREIGN KEY (User_ID)   REFERENCES User(User_ID)     ON DELETE CASCADE,
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE,
    PRIMARY KEY (Patient_ID, organ_req)
);

CREATE TABLE Donor (
    Donor_ID           INT         NOT NULL,
    organ_donated      VARCHAR(30) NOT NULL,
    reason_of_donation VARCHAR(50),
    Organization_ID    INT         NOT NULL,
    User_ID            INT         NOT NULL,
    FOREIGN KEY (User_ID)          REFERENCES User(User_ID)                  ON DELETE CASCADE,
    FOREIGN KEY (Organization_ID)  REFERENCES Organization(Organization_ID)  ON DELETE CASCADE,
    PRIMARY KEY (Donor_ID, organ_donated)
);

CREATE TABLE Organ_available (
    Organ_ID   INT         NOT NULL AUTO_INCREMENT,
    Organ_name VARCHAR(30) NOT NULL,
    Donor_ID   INT         NOT NULL,
    FOREIGN KEY (Donor_ID) REFERENCES Donor(Donor_ID) ON DELETE CASCADE,
    PRIMARY KEY (Organ_ID)
);

CREATE TABLE Transaction (
    Patient_ID           INT  NOT NULL,
    Organ_ID             INT  NOT NULL,
    Donor_ID             INT  NOT NULL,
    Date_of_transaction  DATE NOT NULL,
    Status               INT  NOT NULL,   -- 0 or 1
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
    FOREIGN KEY (Donor_ID)   REFERENCES Donor(Donor_ID)     ON DELETE CASCADE,
    PRIMARY KEY (Patient_ID, Organ_ID)
);

CREATE TABLE `log` (
    querytime DATETIME,
    comment   VARCHAR(255)
);

-- ─── INSERT DATA ─────────────────────────────────────────────

INSERT INTO login VALUES ('admin', 'admin');

INSERT INTO User VALUES
(1,  'sneha',          '2003-05-28', 109, 'none',              'dr.ait',       'Banglore',    'Karnataka'),
(2,  'Jane Smith',     '1985-08-22', 0,   'None',              '456 Oak St',   'Townsville',  'Stateville'),
(3,  'Abhi',           '2000-01-01', 0,   'None',              'G5',           'Banglore',    'Karnataka'),
(4,  'Alice Williams', '1995-03-27', 1,   'High blood pressure','101 Cedar St','Hamletville', 'Stateville'),
(5,  'Kushal',         '2003-07-26', 0,   'None',              '101',          'Banglore',    'Karnataka'),
(6,  'Eva Davis',      '1992-09-03', 1,   'Asthma',            '303 Birch St', 'Suburbia',    'Stateland'),
(7,  'Frank Miller',   '1987-04-18', 0,   'None',              '404 Maple St', 'Cityburg',    'Stateland'),
(8,  'Grace Wilson',   '1975-11-09', 1,   'Diabetes',          '505 Pine St',  'Hometown',    'Stateville'),
(9,  'David Anderson', '1998-02-25', 0,   'None',              '606 Oak St',   'Villageville','Stateland'),
(10, 'Sophia Lee',     '1983-07-08', 1,   'No major issues',   '707 Cedar St', 'Countryside', 'Stateville');

INSERT INTO User_phone_no VALUES
(1,'123-456-7890'),(2,'987-654-3210'),(3,'555-123-4567'),
(4,'789-012-3456'),(5,'111-222-3333'),(6,'444-555-6666'),
(7,'999-888-7777'),(8,'123-789-4560'),(9,'555-876-5432'),(10,'987-654-1234');

INSERT INTO Organization VALUES
(1,'Hospital A',         'City A',1),(2,'Clinic B',         'City B',0),
(3,'Medical Center C',   'City C',1),(4,'Healthcare Group D','City D',1),
(5,'Medical Services E', 'City E',0),(6,'Hospital F',        'City F',1),
(7,'Clinic G',           'City G',0),(8,'Healthcare Center H','City H',1),
(9,'Hospital I',         'City I',1),(10,'Medical Group J',  'City J',0);

INSERT INTO Doctor VALUES
(1,'Dr. Smith',    'Cardiology',      1),(2,'Dr. Johnson',  'Orthopedics',     2),
(3,'Dr. Martinez', 'Neurology',       3),(4,'Dr. Turner',   'Pediatrics',      1),
(5,'Dr. Harris',   'Oncology',        2),(6,'Dr. Clark',    'Dermatology',     3),
(7,'Dr. White',    'Gastroenterology',1),(8,'Dr. Turner',   'Cardiac Surgery', 2),
(9,'Dr. Garcia',   'Plastic Surgery', 3),(10,'Dr. Lee',     'Urology',         1);

INSERT INTO Doctor_phone_no VALUES
(1,'123-456-7890'),(2,'987-654-3210'),(3,'555-123-4567'),
(4,'789-012-3456'),(5,'111-222-3333'),(6,'444-555-6666'),
(7,'999-888-7777'),(8,'123-789-4560'),(9,'555-876-5432'),(10,'987-654-1234');

INSERT INTO Organization_phone_no VALUES
(1,'123-456-7890'),(2,'987-654-3210'),(3,'555-123-4567'),
(4,'789-012-3456'),(5,'111-222-3333'),(6,'444-555-6666');

INSERT INTO Organization_head VALUES
(1,103,'Michael Brown',    '2023-11-28',2),(2,203,'Sophie Miller',     '2024-03-05',3),
(3,301,'David Lee',        '2024-02-20',2),(4,401,'Emma Turner',       '2023-12-10',1),
(3,302,'Oliver White',     '2024-01-15',3),(5,501,'Grace Harris',      '2024-03-10',2),
(4,402,'Daniel Clark',     '2023-11-15',1),(5,502,'Ava Garcia',        '2024-01-05',2),
(1,104,'Christopher Taylor','2023-12-20',3),(6,601,'Lily Turner',      '2024-02-25',1);

INSERT INTO Donor VALUES
(1,'Heart',       'Altruistic donation',           1,4),
(2,'Kidney',      'Volunteer for research',         2,6),
(3,'Liver',       'Personal choice',                3,7),
(4,'Lung',        'Helping restore vision',         1,8),
(5,'Pancreas',    'Gratitude for life',             2,6),
(6,'Intestine',   'Contributing to burn treatment', 3,9),
(7,'Cornea',      'Volunteer decision',             1,7),
(8,'Bone Marrow', 'Supporting leukemia patients',   2,8),
(9,'Skin',        'Improving vascular health',      3,10),
(10,'Blood Vessel','Family history of donation',    1,9);

INSERT INTO Patient VALUES
(1, 'heart',       'Slight heart attack',        3,2),
(2, 'Kidney',      'Chronic kidney disease',     2,2),
(3, 'Eye',         'sight',                      2,6),
(4, 'Lung',        'Idiopathic pulmonary',        4,4),
(5, 'heart',       'heart problem',              4,2),
(6, 'Intestine',   'Short bowel syndrome',       6,6),
(7, 'Cornea',      'Vision impairment',          7,7),
(8, 'Bone Marrow', 'Leukemia treatment',         8,8),
(9, 'Skin',        'Burn injuries',              9,9),
(10,'left eye',    'accident',                   3,8);

INSERT INTO Organ_available (Organ_name, Donor_ID) VALUES
('Heart',1),('Kidney',2),('Liver',3),('Lung',4),('Pancreas',5),
('Intestine',6),('Cornea',7),('Bone Marrow',8),('Skin',9);

INSERT INTO Transaction VALUES
(2,  11, 2,  '2024-02-15', 1),
(4,  13, 4,  '2024-03-15', 0),
(6,  15, 6,  '2024-04-15', 1),
(7,  16, 7,  '2024-05-01', 0),
(8,  17, 8,  '2024-05-15', 0),
(9,  18, 9,  '2024-06-01', 1);
