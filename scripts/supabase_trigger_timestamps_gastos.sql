-- ============================================================================
-- TRIGGER PARA AUTO-COMPLETAR TIMESTAMPS EN TABLA GASTOS
-- ============================================================================
-- Este trigger automáticamente establece created_at y last_modified_at
-- cuando se insertan o actualizan registros en la tabla gastos
-- ============================================================================

-- Paso 1: Crear la función del trigger
CREATE OR REPLACE FUNCTION auto_set_timestamps_gastos()
RETURNS TRIGGER AS $$
BEGIN
    -- Si created_at es NULL, usar fecha_pago
    IF NEW.created_at IS NULL THEN
        NEW.created_at := NEW.fecha_pago;
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
DROP TRIGGER IF EXISTS trigger_auto_timestamps_gastos ON gastos;

-- Paso 3: Crear el trigger
CREATE TRIGGER trigger_auto_timestamps_gastos
    BEFORE INSERT OR UPDATE ON gastos
    FOR EACH ROW
    EXECUTE FUNCTION auto_set_timestamps_gastos();

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
-- Ejecuta esto para verificar que el trigger se creó correctamente:
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'gastos';

-- ============================================================================
-- ACTUALIZAR REGISTROS EXISTENTES CON TIMESTAMPS NULL
-- ============================================================================
-- Este UPDATE establece created_at y last_modified_at para registros que los tienen NULL
UPDATE gastos
SET 
    created_at = COALESCE(created_at, fecha_pago),
    last_modified_at = COALESCE(last_modified_at, COALESCE(created_at, fecha_pago))
WHERE 
    created_at IS NULL 
    OR last_modified_at IS NULL;

-- Verificar cuántos registros se actualizaron
SELECT COUNT(*) as registros_actualizados
FROM gastos
WHERE created_at IS NOT NULL AND last_modified_at IS NOT NULL;

-- ============================================================================
-- PRUEBA DEL TRIGGER (OPCIONAL)
-- ============================================================================
-- Puedes probar el trigger insertando un registro de prueba.
-- 
-- INSERT INTO gastos (id_proveedor, id_caso, fecha_pago, monto, categoria, estado)
-- VALUES (
--     1,  -- id_proveedor (ajusta según tu base de datos)
--     1,  -- id_caso (ajusta según tu base de datos)
--     CURRENT_DATE,  -- Fecha actual
--     99999,  -- Monto de prueba
--     'veterinaria',
--     'pagado'
-- );
-- 
-- -- Verificar que created_at y last_modified_at se establecieron automáticamente
-- SELECT id_gasto, fecha_pago, created_at, last_modified_at, monto
-- FROM gastos
-- WHERE monto = 99999
-- ORDER BY id_gasto DESC
-- LIMIT 1;
-- 
-- -- LIMPIEZA: Eliminar el registro de prueba
-- DELETE FROM gastos WHERE monto = 99999;
