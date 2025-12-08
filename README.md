# 🐾 Salvando Patitas Data Platform (SPDP)

Bienvenidos al repositorio central de la Plataforma de Datos de "Salvando Patitas". Este proyecto unifica la ingesta, transformación y análisis de datos para optimizar la gestión de rescates animales.

## 🚀 Arquitectura General

El proyecto sigue una arquitectura modular moderna que integra **ETL en Python** y **Transformación en SQLX (Dataform)** dentro de un **Monorepo**.

```text
/
├── src/                 # Código Python (ETL & ML)
│   ├── etl/             # Extracción (Supabase -> GCS Bronze)
│   └── ml/              # Modelos de Machine Learning (Futuro)
├── dataform/            # Transformación (Dataform SQLX)
│   ├── definitions/     # Lógica de negocio (Bronze, Silver, Gold)
│   └── workflow_settings.yaml
├── scripts/             # Herramientas de Mantenimiento y Soporte
├── docs/                # Documentación detallada
└── infrastructure/      # IaC (Terraform/SQL inicial)
```

## 📚 Documentación

Para entender cómo operar y mantener esta plataforma, consulta las siguientes guías:

*   **[🏗️ Arquitectura de Datos](docs/ARCHITECTURE.md):** Explica las estrategias de extracción (Incremental vs Snapshot), tipos de datos y flujo de información.
*   **[🛠️ Mantenimiento y Soporte](docs/MAINTENANCE.md):** Manual de operaciones. Explica cómo usar los scripts de `scripts/` para resolver incidentes (limpieza, rewind, etc.).
*   **[🚑 Bitácora de Troubleshooting](docs/TROUBLESHOOTING.md):** Historial de errores resueltos y lecciones aprendidas.

## ⚡ Comandos Rápidos

### Ejecutar Pipeline ETL (Local)
```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar orquestador
python3 -m src.main
```

### Ejecutar Scripts de Soporte
```bash
# Ejemplo: Limpiar tabla 'casos' corrupta
python3 scripts/clean_casos.py
```

---
**Owner:** Equipo de Datos SPDP  
**Estado:** Producción 🟢
