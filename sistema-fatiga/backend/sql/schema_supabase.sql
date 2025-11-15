-- =====================================
-- CREACIÓN DE TABLAS
-- =====================================

CREATE TABLE IF NOT EXISTS operadores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    turno_asignado VARCHAR(50),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dispositivos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    modelo VARCHAR(100),
    id_operador_asignado UUID REFERENCES operadores(id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mediciones_crudas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    id_dispositivo UUID REFERENCES dispositivos(id) ON DELETE CASCADE,
    datos_brutos JSONB NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metricas_procesadas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    id_operador UUID REFERENCES operadores(id) ON DELETE CASCADE,
    indice_fatiga DECIMAL(5,2) NOT NULL,
    clasificacion_riesgo VARCHAR(20) NOT NULL,
    hrv DECIMAL(10,2),
    spo2 DECIMAL(5,2),
    frecuencia_cardiaca INTEGER,
    temperatura_piel DECIMAL(5,2),
    nivel_estres DECIMAL(5,2),
    angulo_inclinacion DECIMAL(5,2),
    nivel_contra_muscular DECIMAL(5,2),
    tipo_maquinaria VARCHAR(100),
    turno_trabajo VARCHAR(20),
    horas_turno INTEGER,
    temperatura_ambiente DECIMAL(5,2),
    humedad_ambiente DECIMAL(5,2),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alertas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    id_operador UUID REFERENCES operadores(id) ON DELETE CASCADE,
    nivel_alerta VARCHAR(20) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'activa',
    timestamp_resolucion TIMESTAMP WITH TIME ZONE,
    id_usuario_resolucion UUID,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS informes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tipo_informe VARCHAR(50) NOT NULL,
    archivo_pdf_base64 TEXT NOT NULL,
    parametros_filtro JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS usuarios_sistema (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================
-- ÍNDICES Y POLÍTICAS DE SEGURIDAD
-- =====================================

CREATE INDEX IF NOT EXISTS idx_mediciones_crudas_timestamp ON mediciones_crudas(timestamp);
CREATE INDEX IF NOT EXISTS idx_metricas_procesadas_operador ON metricas_procesadas(id_operador);
CREATE INDEX IF NOT EXISTS idx_alertas_operador ON alertas(id_operador);
CREATE INDEX IF NOT EXISTS idx_alertas_estado ON alertas(estado);

ALTER TABLE operadores ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispositivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE mediciones_crudas ENABLE ROW LEVEL SECURITY;
ALTER TABLE metricas_procesadas ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas ENABLE ROW LEVEL SECURITY;
ALTER TABLE informes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Lectura pública operadores"
ON operadores
FOR SELECT
USING (true);

CREATE POLICY "Ver operadores"
ON operadores
FOR SELECT
USING (auth.role() = 'authenticated');

CREATE POLICY "Insertar operadores"
ON operadores
FOR INSERT
USING (true)
WITH CHECK (true);

CREATE POLICY "Actualizar operadores"
ON operadores
FOR UPDATE
USING (true)
WITH CHECK (true);

CREATE POLICY "Eliminar operadores"
ON operadores
FOR DELETE
USING (true);
