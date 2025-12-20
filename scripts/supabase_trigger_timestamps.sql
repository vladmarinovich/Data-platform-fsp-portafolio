-- ============================================================================
-- TRIGGER PARA AUTO-COMPLETAR TIMESTAMPS EN TABLA DONACIONES
-- ============================================================================
-- Este trigger automáticamente establece created_at y last_modified_at
-- cuando se insertan o actualizan registros en la tabla donaciones
-- ============================================================================

-- Paso 1: Crear la función del trigger
CREATE OR REPLACE FUNCTION auto_set_timestamps_donaciones()
RETURNS TRIGGER AS $$
BEGIN
    -- Si created_at es NULL, usar fecha_donacion
    IF NEW.created_at IS NULL THEN
        NEW.created_at := NEW.fecha_donacion;
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

-- Paso 2: Eliminar trigger anterior si existe
DROP TRIGGER IF EXISTS trigger_auto_timestamps_donaciones ON donaciones;

-- Paso 3: Crear el trigger
CREATE TRIGGER trigger_auto_timestamps_donaciones
    BEFORE INSERT OR UPDATE ON donaciones
    FOR EACH ROW
    EXECUTE FUNCTION auto_set_timestamps_donaciones();

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
-- Ejecuta esto para verificar que el trigger se creó correctamente:
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'donaciones';

-- ============================================================================
-- PRUEBA DEL TRIGGER (OPCIONAL)
-- ============================================================================
-- Puedes probar el trigger insertando un registro de prueba.
-- NOTA: fecha_donacion debe ser bigint (microsegundos desde epoch)
-- 
-- INSERT INTO donaciones (id_donante, id_caso, fecha_donacion, monto, medio_pago, estado)
-- VALUES (
--     1, 
--     1, 
--     EXTRACT(EPOCH FROM NOW())::bigint * 1000000,  -- Timestamp actual en microsegundos
--     50000, 
--     'nequi', 
--     'aprobada'
-- );
-- 
-- -- Verificar que created_at y last_modified_at se establecieron automáticamente
-- SELECT id_donacion, fecha_donacion, created_at, last_modified_at
-- FROM donaciones
-- ORDER BY id_donacion DESC
-- LIMIT 1;
