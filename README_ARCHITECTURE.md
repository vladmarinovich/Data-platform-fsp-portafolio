# 🏗️ Arquitectura de Datos: SPDP (Salvando Patitas Data Platform)

Este documento describe la estrategia de extracción y carga (ELT) diseñada para garantizar consistencia, escalabilidad y simplicidad en el Data Lake.

---

## 🔄 Estrategias de Extracción

Utilizamos una arquitectura híbrida dependiendo de la naturaleza de los datos:

### 1. Tablas Transaccionales (Estrategia Incremental)
*   **Tablas:** `casos`, `donaciones`, `gastos`, `donantes`.
*   **Comportamiento:**
    *   Los datos crecen constantemente.
    *   Usamos una columna "Watermark" (`last_modified_at`) para bajar solo lo nuevo o modificado.
    *   **Almacenamiento:** Particionado por fecha de ingestión (`y=YYYY/m=MM/d=DD`).
    *   **Objetivo:** Mantener un historial completo e inmutable de todos los cambios.

### 2. Tablas Maestras/Catálogos (Estrategia Snapshot)
*   **Tablas:** `proveedores`, `hogar_de_paso`.
*   **Comportamiento:**
    *   Datos estáticos o de cambio lento (pocos registros, actualizaciones esporádicas).
    *   No se requiere historial de cambios día a día en la capa Raw.
    *   **Almacenamiento:** Ruta estática `.../latest/tabla.parquet`.
    *   **Lógica:** **Sobreescritura (Overwrite)**. Cada ejecución reemplaza el archivo anterior.
    *   **Objetivo:** Evitar duplicados en BigQuery. La tabla externa siempre apunta al archivo único "latest".

---

## 🛠️ Guía de Tipos de Datos (The "Iron Rules")

Para evitar errores de "Type Mismatch" en BigQuery, el extractor aplica conversiones estrictas:

| Concepto | Tipo Parquet/BQ | Regla Python |
| :--- | :--- | :--- |
| **IDs** | `INT64` (Nullable) | `to_numeric(..., errors='coerce').astype('Int64')` |
| **Montos** | `FLOAT64` | `to_numeric(..., errors='coerce').astype('float64')` |
| **Fechas** | `TIMESTAMP` | `to_datetime(..., errors='coerce')` |
| **Texto** | `STRING` | `astype(str)` + limpieza de `"nan"` a `NULL` |
| **JSON** | `STRING` | Convertido a texto para evitar estructuras anidadas complejas. |

---

## 🚀 Flujo de Trabajo (Pipeline)

1.  **Extract:** Python descarga datos de la API de Supabase (usando `postgrest`).
2.  **Transform:** Pandas limpia tipos y convierte nulos.
3.  **Load:**
    *   Si es Incremental -> Sube a partición diaria nueva.
    *   Si es Snapshot -> Sube a carpeta `latest/` (sobrescribiendo).
4.  **BigQuery:** Tablas Externas leen directamente desde GCS.
    *   *Nota:* Las tablas Snapshot no deben tener particionamiento Hive en su definición DDL.

---

## 🚨 Troubleshooting Común

*   **Duplicados en Proveedores:** Revisa si la tabla externa está leyendo particiones viejas (`y=2025...`) junto con el snapshot (`latest/`). Solución: Borrar particiones viejas en GCS.
*   **Error "Type Double vs Int64":** Significa que hay archivos viejos con esquema sucio. Solución: Borrar bucket de la tabla y recargar.

---
**Owner:** Ingeniería de Datos SPDP  
**Última Actualización:** Diciembre 2025
