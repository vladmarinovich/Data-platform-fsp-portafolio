# 🛠️ Guía de Operaciones y Mantenimiento

Este manual recopila los procedimientos estándar para operar, mantener y recuperar la plataforma de datos. Está diseñado para ser la referencia rápida ante incidentes.


---

![Contexto Operativo del Pipeline](img/Flujo%20Pipeline.jpeg)

---


## 🚦 Operación Diaria (Pipeline)

La plataforma se orquesta automáticamente. Sin embargo, para ejecuciones manuales o de relleno (backfill):

### Ejecutar Ingesta (Extract & Load)
Para traer nuevos datos desde Supabase hacia GCS/BigQuery Raw:
```bash
# Desde la raíz del proyecto
source .venv/bin/activate
python3 -m src.main
```

### Ejecutar Transformación (Dataform)
Para procesar Raw -> Silver -> Gold en Google Cloud:
1.  Ir a la consola de **Dataform**.
2.  Pipeline: `fsp_pipeline`.
3.  Clic en "Start Execution" > "All actions".
4.  *(Opcional)* Seleccionar tags específicos: `silver`, `gold`, `assertions`.

---

## 🚑 Resolución de Incidentes (Troubleshooting)

### 1. Fallo en Dataform Assertions 🚨
**Síntoma:** El pipeline termina con advertencias o error en pasos como `assert_silver_gastos`.
**Acción:**
1.  Identificar la aserción fallida en la consola de Dataform.
2.  Abrir el archivo `.sqlx` correspondiente en `definitions/assertions/`.
3.  Copiar el query SQL de validación.
4.  Ejecutarlo en BigQuery para ver las filas "culpables".
5.  **Remedio:**
    *   Si es data sucia real: Corregir en Supabase.
    *   Si es un falso positivo: Ajustar la regla en el `.sqlx` y pushear el cambio.

### 2. Reiniciar una Tabla Corrupta (Nuclear Option ☢️)
Si una tabla Raw se corrompe (ej. mezcla de tipos de datos int/string incompatibles):
1.  **Limpiar GCS:**
    ```bash
    python3 scripts/clean_casos.py  # Ejemplo para tabla casos
    ```
    *Esto borra todos los parquets y reinicia el watermark a fecha cero.*
2.  **Recargar:** Ejecutar `src.main` para bajar todo el histórico de nuevo.
3.  **Procesar:** Ejecutar Dataform con la opción "Run with Full Refresh" para recrear las tablas Silver/Gold.

### 3. Reprocesar Datos (Rewind ⏪)
Si necesitas volver a cargar los datos de los últimos 3 días (ej. porque se corrigió un bug en origen):
1.  Editar `scripts/rewind_watermark.py` con la fecha deseada.
2.  Ejecutar:
    ```bash
    python3 scripts/rewind_watermark.py
    ```
3.  Ejecutar el pipeline de ingesta normal.

---

## 🧪 Pruebas Locales (Development)

Para validar cambios en la transformación sin afectar producción:

1.  Crear un **Workspace** de desarrollo en Dataform (ej. `dev-vlad`).
2.  Hacer cambios en el código `.sqlx`.
3.  Ejecutar solo el nodo modificado con `Run selected node`.
4.  Verificar los resultados en BigQuery bajo el dataset `dataform_staging` (o el configurado para dev).

---

## 📅 Tareas de Mantenimiento Periódico

*   **Mensual:** Revisar costos de BigQuery y GCS. Ejecutar limpieza de logs antiguos si aplica.
*   **Trimestral:** Rotar llaves de API de Supabase y Service Accounts de GCP.
*   **Semestral:** Revisar reglas de Assertions para ver si siguen vigentes con el negocio.

---
**Responsable:** Vladislav Marinovich
