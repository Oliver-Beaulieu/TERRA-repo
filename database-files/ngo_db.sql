DROP DATABASE IF EXISTS ngo_db;
CREATE DATABASE IF NOT EXISTS ngo_db;

USE ngo_db;


CREATE TABLE IF NOT EXISTS WorldNGOs (
    NGO_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Founding_Year INTEGER,
    Focus_Area VARCHAR(100),
    Website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Projects (
    Project_ID INT AUTO_INCREMENT PRIMARY KEY,
    Project_Name VARCHAR(255) NOT NULL,
    Focus_Area VARCHAR(100),
    Budget DECIMAL(15, 2),
    NGO_ID INT,
    Start_Date DATE,
    End_Date DATE,
    FOREIGN KEY (NGO_ID) REFERENCES WorldNGOs(NGO_ID)
);

CREATE TABLE IF NOT EXISTS Donors (
    Donor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Donor_Name VARCHAR(255) NOT NULL,
    Donor_Type ENUM('Individual', 'Organization') NOT NULL,
    Donation_Amount DECIMAL(15, 2),
    NGO_ID INT,
    FOREIGN KEY (NGO_ID) REFERENCES WorldNGOs(NGO_ID)
);

INSERT INTO WorldNGOs (Name, Country, Founding_Year, Focus_Area, Website)
VALUES
('World Wildlife Fund', 'United States', 1961, 'Environmental Conservation', 'https://www.worldwildlife.org'),
('Doctors Without Borders', 'France', 1971, 'Medical Relief', 'https://www.msf.org'),
('Oxfam International', 'United Kingdom', 1995, 'Poverty and Inequality', 'https://www.oxfam.org'),
('Amnesty International', 'United Kingdom', 1961, 'Human Rights', 'https://www.amnesty.org'),
('Save the Children', 'United States', 1919, 'Child Welfare', 'https://www.savethechildren.org'),
('Greenpeace', 'Netherlands', 1971, 'Environmental Protection', 'https://www.greenpeace.org'),
('International Red Cross', 'Switzerland', 1863, 'Humanitarian Aid', 'https://www.icrc.org'),
('CARE International', 'Switzerland', 1945, 'Global Poverty', 'https://www.care-international.org'),
('Habitat for Humanity', 'United States', 1976, 'Affordable Housing', 'https://www.habitat.org'),
('Plan International', 'United Kingdom', 1937, 'Child Rights', 'https://plan-international.org');

INSERT INTO Projects (Project_Name, Focus_Area, Budget, NGO_ID, Start_Date, End_Date)
VALUES
('Save the Amazon', 'Environmental Conservation', 5000000.00, 1, '2022-01-01', '2024-12-31'),
('Emergency Medical Aid in Syria', 'Medical Relief', 3000000.00, 2, '2023-03-01', '2023-12-31'),
('Education for All', 'Poverty and Inequality', 2000000.00, 3, '2021-06-01', '2025-05-31'),
('Human Rights Advocacy in Asia', 'Human Rights', 1500000.00, 4, '2022-09-01', '2023-08-31'),
('Child Nutrition Program', 'Child Welfare', 2500000.00, 5, '2022-01-01', '2024-01-01');

INSERT INTO Donors (Donor_Name, Donor_Type, Donation_Amount, NGO_ID)
VALUES
('Bill & Melinda Gates Foundation', 'Organization', 10000000.00, 1),
('Elon Musk', 'Individual', 5000000.00, 2),
('Google.org', 'Organization', 2000000.00, 3),
('Open Society Foundations', 'Organization', 3000000.00, 4),
('Anonymous Philanthropist', 'Individual', 1000000.00, 5);

CREATE TABLE model1_params (
    sequence_number INT,
    beta_vals TEXT
);

INSERT INTO model1_params (sequence_number, beta_vals) VALUES
(1, '[0.25, 0.45, 0.67]');

-- Belgium World Bank energy/GDP data (from GDP_Energy_WBdat.csv, Belgium subset)
-- CO2_Upop is a derived column: CO2_emit / Urban_pop (computed from the raw data)
-- This is the dataset used to fit model02 (GDP ~ Fossil_Fuels + CO2_Upop)
CREATE TABLE IF NOT EXISTS belgium_energy (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    year        INT NOT NULL,
    GDP         DOUBLE,          -- GDP per capita (EUR)
    Fossil_Fuels DOUBLE,         -- Fossil fuel energy as % of total energy
    CO2_emit    DOUBLE,          -- CO2 emissions (kt)
    Urban_pop   DOUBLE,          -- Urban population
    CO2_Upop    DOUBLE           -- CO2_emit / Urban_pop (derived feature)
);

INSERT INTO belgium_energy (year, GDP, Fossil_Fuels, CO2_emit, Urban_pop, CO2_Upop) VALUES
(1990, 20600.375279, 75.815870, 109312.6, 9606261.0, 0.01137931),
(1991, 21041.660652, 76.397007, 113960.1, 9650427.0, 0.01180881),
(1992, 23372.619171, 75.932201, 112329.3, 9697796.0, 0.01158297),
(1993, 22283.936021, 75.935015, 110108.3, 9743821.0, 0.01130032),
(1994, 24208.554793, 77.649375, 114901.4, 9781788.0, 0.01174646),
(1995, 28413.826439, 77.405698, 114568.7, 9810102.0, 0.01167865),
(1996, 27489.555177, 77.644484, 119448.4, 9836805.0, 0.01214301),
(1997, 24820.938050, 75.898319, 116634.7, 9868070.0, 0.01181940),
(1998, 25338.443293, 77.048527, 119412.8, 9896510.0, 0.01206615),
(1999, 25252.801907, 75.790143, 115514.5, 9926274.0, 0.01163725),
(2000, 23098.886508, 75.854086, 117274.6, 9956937.0, 0.01177818),
(2001, 23015.071263, 75.628293, 118339.8, 9997106.0, 0.01183741),
(2002, 25006.191397, 74.470181, 110850.2, 10047703.0, 0.01103239),
(2003, 30655.209268, 75.232846, 115502.1, 10095562.0, 0.01144088),
(2004, 35429.407793, 75.019459, 113350.8, 10144977.0, 0.01117310),
(2005, 36809.701340, 74.763949, 110960.2, 10206487.0, 0.01087154),
(2006, 38705.106796, 73.942511, 108081.5, 10279407.0, 0.01051437),
(2007, 44319.165449, 72.666550, 103905.8, 10360589.0, 0.01002895),
(2008, 48303.397956, 73.393632, 106715.4, 10448114.0, 0.01021384),
(2009, 44760.291244, 72.640023, 99904.4, 10537701.0, 0.00948066),
(2010, 44184.946354, 72.793617, 106872.8, 10639649.0, 0.01004477),
(2011, 47410.566928, 70.254496, 96488.2, 10784163.0, 0.00894721),
(2012, 44670.560685, 71.115714, 95275.6, 10856360.0, 0.00877602),
(2013, 46757.951856, 70.820306, 96550.6, 10912673.0, 0.00884757),
(2014, 47764.071512, 72.652505, 90362.4, 10966157.0, 0.00824012),
(2015, 41008.296719, 75.870784, 95096.0, 11034732.0, 0.00861788);


-- Model 2 parameters: GDP ~ Fossil_Fuels + CO2_Upop
-- Fitted on the full Belgium dataset (HW2 Part 3.1)
-- beta_vals = [intercept, b_Fossil_Fuels, b_CO2_Upop]
CREATE TABLE IF NOT EXISTS model2_params (
    sequence_number INT,
    beta_vals       TEXT
);

-- NOTE: These parameters are based on the scaled features
-- The user will be inputting the raw values, so:
-- will need to scale before applying model in function
INSERT INTO model2_params (sequence_number, beta_vals) VALUES
(1, '[33258.521, -3204.811, -6118.475]');

-- To rescale, need to save the means and std of features
CREATE TABLE IF NOT EXISTS model2_scaler (
    sequence_number INT,
    feature_means   TEXT,   -- e.g. "[74.32, 0.0106]"
    feature_stds    TEXT    -- e.g. "[1.85, 0.00092]"
);

INSERT INTO model2_scaler (sequence_number, feature_means, feature_stds) VALUES
(1, '[74.717, 0.0107]', '[2.058, 0.0012]');