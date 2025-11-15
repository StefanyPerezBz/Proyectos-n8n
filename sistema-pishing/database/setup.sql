-- =============================
-- BASE DE DATOS: PHISHING SYSTEM
-- =============================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla principal de análisis de URLs
CREATE TABLE IF NOT EXISTS url_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    analysis_result JSONB NOT NULL,
    risk_level VARCHAR(20) CHECK (risk_level IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    prediction VARCHAR(20) CHECK (prediction IN ('LEGITIMATE','SUSPICIOUS','PHISHING','MALWARE')),
    probability DECIMAL(3,2),
    confidence VARCHAR(10),
    features_extracted INTEGER,
    processing_time DECIMAL(8,4),
    threat_intelligence JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de reportes generados
CREATE TABLE IF NOT EXISTS analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) CHECK (report_type IN ('DAILY','WEEKLY','MONTHLY','CUSTOM')),
    date_range DATERANGE,
    statistics JSONB NOT NULL,
    pdf_report_url TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('ADMIN','ANALYST','VIEWER')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Configuración del sistema
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_by VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Triggers para mantener updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_url_update BEFORE UPDATE ON url_analysis FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER trg_user_update BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER trg_config_update BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Datos iniciales
INSERT INTO users (email, name, role)
VALUES
('admin@company.com', 'Administrador', 'ADMIN'),
('analyst@company.com', 'Analista', 'ANALYST'),
('viewer@company.com', 'Visualizador', 'VIEWER')
ON CONFLICT (email) DO NOTHING;

INSERT INTO system_config (config_key, config_value, description)
VALUES
('phishing_threshold', '{"value":0.85}'::JSONB, 'Umbral phishing'),
('suspicious_threshold', '{"value":0.60}'::JSONB, 'Umbral sospechoso'),
('rate_limit', '{"requests_per_minute":60}'::JSONB, 'Límite solicitudes'),
('features_config', '{"enabled_features":["url_length","entropy","keywords"]}'::JSONB, 'Características activas')
ON CONFLICT (config_key) DO NOTHING;
