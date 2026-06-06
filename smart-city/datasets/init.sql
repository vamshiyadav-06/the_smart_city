-- Smart City India - PostgreSQL Schema

CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    state VARCHAR(255) NOT NULL,
    population VARCHAR(100),
    famous_for TEXT,
    description TEXT,
    lat FLOAT,
    lon FLOAT
);

CREATE TABLE IF NOT EXISTS traffic_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    vehicle_count INT NOT NULL,
    avg_speed FLOAT NOT NULL,
    congestion_level VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parking_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    parking_name VARCHAR(255) NOT NULL,
    total_slots INT NOT NULL,
    occupied_slots INT NOT NULL,
    available_slots INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS road_damage_reports (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255),
    image_url TEXT,
    damage_type VARCHAR(255) NOT NULL,
    severity VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    confidence FLOAT,
    pothole_count INT DEFAULT 0,
    crack_count INT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_analysis_reports (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    analysis_text TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.85,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_traffic_city ON traffic_data(city);
CREATE INDEX IF NOT EXISTS idx_parking_city ON parking_data(city);
CREATE INDEX IF NOT EXISTS idx_damage_city ON road_damage_reports(city);
CREATE INDEX IF NOT EXISTS idx_ai_city ON ai_analysis_reports(city);
