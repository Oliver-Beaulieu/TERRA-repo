CREATE DATABASE IF NOT EXISTS terra_db;

USE terra_db;

-- TERRA Database

-- 1. ROLES - Defines user roles in the app.
CREATE TABLE IF NOT EXISTS roles (
    role_id INT NOT NULL AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id)
);

-- 2. USERS - App users.
CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL AUTO_INCREMENT,
    role_id INT NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    password_hash VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (user_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);


-- 3. COUNTRY - Central entity
CREATE TABLE IF NOT EXISTS country (
    country_id INT NOT NULL AUTO_INCREMENT,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(2) NOT NULL UNIQUE,
    region VARCHAR(100),
    population INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (country_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- 4. COUNTRY_YEAR_DATA
-- Cleaned yearly data used by the app and ML models.
CREATE TABLE IF NOT EXISTS country_year_data (
    data_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    year INT NOT NULL,

    gdp_per_capita DECIMAL(12,2),
    unemployment_rate DECIMAL(5,2),
    population INT,
    urban_pct DECIMAL(6,3),

    asylum_applications INT,

    temp_mean DECIMAL(5,2),
    heatwave_days INT,
    precip_total DECIMAL(10,2),
    precip_days_heavy INT,
    dry_days INT,
    evapotrans_total DECIMAL(10,2),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,

    PRIMARY KEY (data_id),
    UNIQUE KEY uq_country_year (country_id, year),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- 5. CLIMATE_EVENT
CREATE TABLE IF NOT EXISTS climate_event (
    event_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    event_type VARCHAR(100),
    event_date DATE,
    severity VARCHAR(50),
    event_description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (event_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- 6. RISK_ASSESSMENT - Country risk scores. Used by Gabriel, Diana, and Mohammed.
CREATE TABLE IF NOT EXISTS risk_assessment (
    risk_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    year INT NOT NULL,
    risk_score DECIMAL(5,2),
    risk_level VARCHAR(50),
    label_method VARCHAR(150),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (risk_id),
    UNIQUE KEY uq_risk_country_year (country_id, year),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);


-- 7. POLICIES - Gabriel's policy analysis work.
CREATE TABLE IF NOT EXISTS policies (
    policy_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    name VARCHAR(150),
    policy_type VARCHAR(100),
    status VARCHAR(50),
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (policy_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);


-- 8. POLICY_FLAG - Supports Gabriel flagging countries for policy review.
CREATE TABLE IF NOT EXISTS policy_flag (
    flag_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    user_id INT NOT NULL,
    flag_status VARCHAR(50) NOT NULL,
    flag_note TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (flag_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 9. SAVED_VIEWS - Saved country comparison views for Gabriel.
CREATE TABLE IF NOT EXISTS saved_views (
    view_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    view_name VARCHAR(150) NOT NULL,
    year_from INT,
    year_to INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (view_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 10. SAVED_VIEW_COUNTRY - Table for saved views and countries.
CREATE TABLE IF NOT EXISTS saved_view_country (
    view_id INT NOT NULL,
    country_id INT NOT NULL,
    PRIMARY KEY (view_id, country_id),
    FOREIGN KEY (view_id) REFERENCES saved_views(view_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

-- 11. NGO - Non-Governmental Organizations for Diana.
CREATE TABLE IF NOT EXISTS ngo (
    ngo_id INT NOT NULL AUTO_INCREMENT,
    ngo_name VARCHAR(150) NOT NULL,
    focus_area VARCHAR(100),
    contact_email VARCHAR(150),
    website VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    PRIMARY KEY (ngo_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- 12. NGO_COUNTRY - One NGO can operate in multiple countries. One country can have multiple NGOs.
CREATE TABLE IF NOT EXISTS ngo_country (
    ngo_id INT NOT NULL,
    country_id INT NOT NULL,
    operating_status VARCHAR(50) DEFAULT 'Active',
    support_notes TEXT,
    PRIMARY KEY (ngo_id, country_id),
    FOREIGN KEY (ngo_id) REFERENCES ngo(ngo_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

-- 13. WATCHLIST - Countries Mohammed wants to follow.
CREATE TABLE IF NOT EXISTS watchlist (
    watchlist_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    country_id INT NOT NULL,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (watchlist_id),
    UNIQUE KEY uq_watchlist_user_country (user_id, country_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

-- 14. COUNTRY_SUMMARY_REPORT - Stores exported country summaries for Diana.
CREATE TABLE IF NOT EXISTS country_summary_report (
    report_id INT NOT NULL AUTO_INCREMENT,
    country_id INT NOT NULL,
    user_id INT NOT NULL,
    report_title VARCHAR(150),
    report_text TEXT,
    export_format VARCHAR(20),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);