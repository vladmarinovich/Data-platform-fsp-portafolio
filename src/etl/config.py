import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# CREDENCIALES Y CONFIGURACIÓN GCP / SUPABASE
# =============================================================================
PROJECT_ID = os.getenv("PROJECT_ID")
RAW_BUCKET = os.getenv("RAW_BUCKET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SOURCE_SYSTEM = "supabase"
STATE_FILE_PATH = "state/watermarks.json"

# =============================================================================
# DEFINICIÓN DE TABLAS Y ESTRATEGIAS
# =============================================================================

# Estrategia: INCREMENTAL (Append)
# Se usa para tablas transaccionales que crecen siempre.
# Requiere una columna de fecha (watermark) para filtrar lo nuevo.
INCREMENTAL_TABLES = {
    "donaciones": "last_modified_at",
    "gastos": "last_modified_at",
    "donantes": "last_modified_at",
    "casos": "last_modified_at"
}

# Estrategia: SNAPSHOT (Overwrite)
# Se usa para catálogos o tablas maestras pequeñas.
# Se descarga todo y se guarda en una ruta 'latest/' sobrescribiendo la anterior.
FULL_LOAD_TABLES = [
    "hogar_de_paso",
    "proveedores"
]
