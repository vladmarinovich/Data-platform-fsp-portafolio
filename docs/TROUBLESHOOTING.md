# 🐛 Bitácora de Errores y Soluciones (Troubleshooting Log)
**Proyecto:** Salvando Patitas Data Platform (SPDP)  
**Componente:** Pipeline de Extracción (Supabase -> GCS -> BigQuery)  
**Fecha:** Diciembre 2025

Esta bitácora documenta los desafíos técnicos encontrados durante la implementación del Data Lake, sus causas raíz y las soluciones aplicadas. Sirve como base de conocimiento para mantenimiento futuro y entrevistas técnicas.

---

## 📅 Timeline de Desafíos y Resoluciones

### 1. 🔌 El Bloqueo del Connection Pooler (PgBouncer)
**Síntoma:** El script original usando `sqlalchemy`/`psycopg2` fallaba al conectar a Supabase, o se caía intermitentemente.
**Causa:** Supabase en modo transaccional (puerto 6543) y IPv4 en redes restringidas causaban timeouts y handshake errors.
**Solución:**
*   Abandonar la conexión directa a base de datos (SQL).
*   Migrar al **Cliente Supabase Python (REST API)**. Esto desacopla la infraestructura de red, usa HTTPS estándar (puerto 443) y es mucho más resiliente.

### 2. 📝 El Fantasma de los "string nan"
**Síntoma:** En BigQuery, columnas que deberían ser vacías aparecían con el texto literal `"nan"` o `"None"`.
**Causa:** Una regla de limpieza en Pandas convertía *todo* objeto a string (`astype(str)`), transformando los valores nulos (`NaN`, `None`) en las cadenas de texto `"nan"`.
**Solución:**
*   Agregar un paso de limpieza pos-conversión:
    ```python
    df[col] = df[col].replace({'nan': None, 'None': None, '<NA>': None})
    ```
*   Esto restaura el objeto `None` nativo, que Parquet y BigQuery interpretan correctamente como `NULL`.

### 3. 🔥 El Incidente de los Números Perdidos (Monto vs Texto)
**Síntoma:** Columnas de texto importantes (ej. "descripción") aparecían todas como `NULL`.
**Causa:** Una lógica agresiva intentaba convertir cualquier columna con palabras como "valor" o "desc" a numérico (`to_numeric(errors='coerce')`). Al fallar la conversión de texto a número, Pandas borraba el contenido.
**Solución:**
*   Refinar las palabras clave de detección (`money_keywords`).
*   Ser explícitos: solo convertir a Float columnas como `monto`, `presupuesto`, `costo`.
*   Para todo lo demás: Respetar el tipo original.

### 4. 🧟‍♂️ Archivos Zombies: "Type Mismatch" (Double vs Int64)
**Síntoma:** Error en BigQuery al leer tablas externas (`raw_casos`, `raw_donaciones`, `raw_gastos`):
> `Parquet column 'id_hogar_de_paso' (o 'id_caso') has type DOUBLE which does not match the target cpp_type INT64.`
**Causa (Schema Drift):**
*   **Archivos Viejos:** Generados cuando Pandas infería IDs nulos como Float (`15.0`).
*   **Archivos Nuevos:** Generados con la nueva regla estricta `Int64` (`15`).
*   **Conflicto:** BigQuery no puede leer una carpeta mezclada.
**Solución:**
*   **Código:** Implementar la regla estricta `astype('Int64')` para todas las columnas terminadas en `_id` y PKs explícitas.
*   **Limpieza (The Nuclear Option):** Borrar físicamente el historial del bucket (`gsutil rm ...`) para eliminar los archivos con esquema viejo.
*   **Recarga (Backfill):** Reprocesar todo el historial con el nuevo código estricto. Se aplicó tabla por tabla (`casos`, `donaciones`, `gastos`).

### 5. 📛 Desalineación de Nombres (Schema Mismatch)
**Síntoma:** Columnas llenas de NULLs en BigQuery a pesar de tener datos en el Parquet.
**Causa:** La definición de la tabla externa en BigQuery esperaba nombres como `nombre_animal`, pero el Parquet venía de la fuente como `nombre_caso`. BigQuery, al no encontrar la columna exacta, rellenaba con NULL.
**Solución:**
*   **Filosofía ELT:** Aceptar que la capa Raw/Bronze debe ser un espejo de la fuente.
*   **Acción:** Ejecutar `CREATE OR REPLACE EXTERNAL TABLE` en BigQuery para que auto-detecte los nombres reales del Parquet.
*   **Validación:** Se creó el script `scripts/test_transformation.py` para imprimir los nombres exactos de columnas y garantizar alineación.

### 6. 🧹 Limpieza de Datos Sensibles e Innecesarios
**Necesidad:** La tabla `donantes` contenía campos pesados (`archivos`) y sensibles (`notas`).
**Solución:**
*   Implementar una regla de exclusión temprana en el extractor:
    ```python
    if table_name == 'donantes':
        df = df.drop(columns=['notas', 'archivos'], errors='ignore')
    ```
*   Esto reduce costos de almacenamiento y riesgos de privacidad.

---

## 🛠 Estado Final de la Arquitectura

1.  **Extractor:** Python Multithreaded (20 workers).
2.  **Validación de Tipos:** Estricta (Fechas, Int64 IDs, Float Montos, String Textos).
3.  **Manejo de Nulos:** Nativo (NULL real).
4.  **Estrategia de Carga:**
    *   **Incremental:** `last_modified_at` (Insert + Update).
    *   **Deduplicación:** Se delega a la capa Silver (SQL).
5.  **Formato:** Parquet con particionamiento Hive (`y=YYYY/m=MM/d=DD`).

---

### 7. 🚨 Alerta de Calidad de Datos (Pendiente)
**Incidente:** Dataform reporta fallo en la aserción `assert_silver_gastos`.
**Síntoma:** Error `Assertion failed, expected zero rows`.
**Causa Probable:**
*   Existen registros en `silver_gastos` que violan integridad referencial (FK hacia Proveedores o Casos).
*   Posibles duplicados o montos negativos.
**Estado:** Deuda técnica registrada. El pipeline continúa su ejecución (no bloqueante), pero se debe investigar y limpiar la data raw en Supabase.
**Acción Futura:**
1.  Ejecutar query de diagnóstico en BigQuery para identificar IDs culpables.
2.  Corregir datos en origen (Supabase) o ajustar regla de negocio.

