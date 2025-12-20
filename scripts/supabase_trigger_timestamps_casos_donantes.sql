-- ============================================================================
-- TRIGGERS PARA AUTO-COMPLETAR TIMESTAMPS EN TODAS LAS TABLAS INCREMENTALES
-- ============================================================================
-- Este script crea triggers para: casos y donantes
-- ============================================================================

-- ============================================================================
-- TABLA: CASOS
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_set_timestamps_casos()
RETURNS TRIGGER AS $$
BEGIN
    -- Si created_at es NULL, usar fecha_ingreso
    IF NEW.created_at IS NULL THEN
        NEW.created_at := NEW.fecha_ingreso;
    END IF;
    
    -- Si last_modified_at es NULL, usar created_at
    IF NEW.last_modified_at IS NULL THEN
        NEW.last_modified_at := NEW.created_at;
    END IF;
    
    -- Si es un UPDATE, actualizar last_modified_at al timestamp actual
    IF TG_OP = 'UPDATE' THEN
        NEW.last_modified_at := EXTRACT(EPOCH FROM NOW()) * 1000000;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_timestamps_casos ON casos;

CREATE TRIGGER trigger_auto_timestamps_casos
    BEFORE INSERT OR UPDATE ON casos
    FOR EACH ROW
    EXECUTE FUNCTION auto_set_timestamps_casos();

-- Actualizar registros existentes
UPDATE casos
SET 
    created_at = COALESCE(created_at, fecha_ingreso),
    last_modified_at = COALESCE(last_modified_at, COALESCE(created_at, fecha_ingreso))
WHERE 
    created_at IS NULL 
    OR last_modified_at IS NULL;

-- ============================================================================
-- TABLA: DONANTES
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_set_timestamps_donantes()
RETURNS TRIGGER AS $$
BEGIN
    -- Si created_at es NULL, usar CURRENT_TIMESTAMP en microsegundos
    IF NEW.created_at IS NULL THEN
        NEW.created_at := EXTRACT(EPOCH FROM NOW()) * 1000000;
    END IF;
    
    -- Si last_modified_at es NULL, usar created_at
    IF NEW.last_modified_at IS NULL THEN
        NEW.last_modified_at := NEW.created_at;
    END IF;
    
    -- Si es un UPDATE, actualizar last_modified_at al timestamp actual
    IF TG_OP = 'UPDATE' THEN
        NEW.last_modified_at := EXTRACT(EPOCH FROM NOW()) * 1000000;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_timestamps_donantes ON donantes;

CREATE TRIGGER trigger_auto_timestamps_donantes
    BEFORE INSERT OR UPDATE ON donantes
    FOR EACH ROW
    EXECUTE FUNCTION auto_set_timestamps_donantes();

-- Actualizar registros existentes
UPDATE donantes
SET 
    created_at = COALESCE(created_at, EXTRACT(EPOCH FROM NOW()) * 1000000),
    last_modified_at = COALESCE(last_modified_at, created_at)
WHERE 
    created_at IS NULL 
    OR last_modified_at IS NULL;

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table IN ('casos', 'donantes')
ORDER BY event_object_table, trigger_name;
