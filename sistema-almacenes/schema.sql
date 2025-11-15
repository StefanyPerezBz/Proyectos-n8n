-- ===========================================================
-- CREACIÓN DE TABLAS: LÍNEA y PRODUCTO
-- ===========================================================

-- ===========================
-- TABLA: LINEA
-- ===========================
CREATE TABLE IF NOT EXISTS public.LINEA (
    "idLinea" SERIAL PRIMARY KEY,
    "descripcion" TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABLA: PRODUCTO
-- ===========================
CREATE TABLE IF NOT EXISTS public.PRODUCTO (
    codigo SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    reorden INTEGER NOT NULL DEFAULT 0 CHECK (reorden >= 0),
    "idLinea" INTEGER REFERENCES public.LINEA("idLinea") ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- ÍNDICES DE RENDIMIENTO
-- ===========================
CREATE INDEX IF NOT EXISTS idx_producto_linea ON public.PRODUCTO("idLinea");
CREATE INDEX IF NOT EXISTS idx_producto_descripcion ON public.PRODUCTO(descripcion);
CREATE INDEX IF NOT EXISTS idx_producto_stock ON public.PRODUCTO(stock);

-- ===========================================================
-- TRIGGER AUTOMÁTICO PARA updated_at
-- ===========================================================
-- Esta función actualiza automáticamente el campo updated_at
-- cada vez que se modifica un registro.
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplica el trigger en ambas tablas
DROP TRIGGER IF EXISTS linea_set_updated_at ON public.LINEA;
CREATE TRIGGER linea_set_updated_at
BEFORE UPDATE ON public.LINEA
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS producto_set_updated_at ON public.PRODUCTO;
CREATE TRIGGER producto_set_updated_at
BEFORE UPDATE ON public.PRODUCTO
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- ===========================================================
-- 🔐 POLÍTICAS DE SEGURIDAD (para desarrollo)
-- ===========================================================
ALTER TABLE public.LINEA ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.PRODUCTO ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir acceso público a LINEA" ON public.LINEA
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Permitir acceso público a PRODUCTO" ON public.PRODUCTO
  FOR ALL USING (true) WITH CHECK (true);
