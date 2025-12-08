# 🛠️ Guía de Mantenimiento y Soporte (Ops Manual)

Este documento describe las herramientas de operación ("Scripts de Emergencia") ubicadas en la carpeta `scripts/`. Estas herramientas **NO** son parte del pipeline automático diario, sino que se ejecutan manualmente para resolver incidentes específicos.

---

## 🧹 Scripts de Limpieza ("The Nuclear Option")

Utiliza estos scripts cuando haya corrupción de datos, cambios radicales de esquema (ej. cambiar un tipo de dato de `String` a `Int64`), o necesites reiniciar una tabla desde cero.

**⚠️ ADVERTENCIA:** Estos scripts borran datos históricos del Data Lake (Bucket GCS). Úsalos con precaución.

| Script | Descripción | Cuándo usarlo |
| :--- | :--- | :--- |
| `clean_casos.py` | Borra todo el historial de la tabla `casos` y resetea su watermark. | Error "Type Mismatch (Double vs Int64)" en BigQuery para Casos. |
| `clean_donaciones.py` | Igual al anterior, pero para `donaciones`. | Error "Type Mismatch" en Donaciones. |
| `clean_gastos.py` | Igual al anterior, pero para `gastos`. | Error "Type Mismatch" en Gastos. |
| `clean_proveedores.py` | Borra las particiones antiguas (`y=...`) de Proveedores. | Para migrar Proveedores de estrategia Incremental a Snapshot (eliminar duplicados). |
| `clean_bucket.py` | **PELIGRO TOTAL.** Borra TODO el contenido del bucket `raw` (todas las tablas). | Solo al inicio del proyecto o si quieres reiniciar el Data Lake completo. |

**Ejemplo de Uso:**
```bash
# Reiniciar la tabla de casos por completo
source .venv/bin/activate
python3 scripts/clean_casos.py
# Luego ejecutar el pipeline para recargar
python3 -m src.main
```

---

## ⏳ Scripts de Gestión de Tiempo (Watermarks)

El pipeline usa `state/watermarks.json` en GCS para saber qué ya procesó. Estos scripts manipulan ese estado.

| Script | Descripción | Cuándo usarlo |
| :--- | :--- | :--- |
| `rewind_watermark.py` | "La Máquina del Tiempo". Retrocede la fecha de última carga de una tabla. | Si descubres que la carga de ayer quedó incompleta o con datos erróneos y quieres reprocesar los últimos N días. |
| `fix_watermark.py` | (Si existiera) Corrige fechas futuras o inválidas. | Si un bug puso `2099-01-01` en el watermark y el pipeline dejó de descargar datos. |

**Ejemplo de Uso:**
```bash
# Retroceder el reloj de 'donaciones' al 1 de Noviembre
# (Primero edita el script para poner la fecha deseada)
python3 scripts/rewind_watermark.py
```

---

## 🧪 Scripts de Prueba (Laboratorio)

Herramientas para desarrollo y validación segura sin afectar producción.

| Script | Descripción | Cuándo usarlo |
| :--- | :--- | :--- |
| `test_transformation.py` | Descarga 5 filas de Supabase, aplica la transformación actual y muestra los tipos de datos en consola. **No sube nada a GCS.** | Antes de modificar `src/etl/transform.py`. Úsalo para verificar que una nueva regla de limpieza funciona como esperas. |

**Ejemplo de Uso:**
```bash
python3 scripts/test_transformation.py
# Revisa la salida en consola para ver si 'telefono' es String o Float
```

---

## 📋 Checklist de Resolución de Incidentes

1.  **Error de Tipos en BigQuery:**
    *   Ejecuta `clean_{tabla}.py`.
    *   Ejecuta `python3 -m src.main` (Backfill).
    *   Ejecuta `CREATE OR REPLACE EXTERNAL TABLE...` en BigQuery.

2.  **Duplicados en Tablas Maestras:**
    *   Ejecuta `clean_proveedores.py` (o similar).
    *   Asegúrate de que la tabla esté en `FULL_LOAD_TABLES` en `src/etl/config.py`.
    *   Ejecuta el pipeline.

3.  **Pipeline no descarga datos nuevos:**
    *   Revisa `watermarks.json` en GCS.
    *   Si la fecha es correcta, verifica Supabase.
    *   Si la fecha es futura/errónea, usa un script para corregir el JSON.

---
**Owner:** Operaciones de Datos SPDP  
**Última Actualización:** Diciembre 2025
