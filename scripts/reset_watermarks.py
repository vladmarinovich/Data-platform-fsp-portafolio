
import sys
import os
import json

# Agregar root al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_storage_client
from src.etl.connect import get_storage_client
from src.etl.config import RAW_BUCKET, STATE_FILE_PATH

def reset_watermarks():
    """
    Resetea el archivo de watermarks a una fecha segura pasada.
    Esto obliga al pipeline a volver a procesar datos históricos.
    """
    print(f"🔄 Reseteando watermarks en bucket: {RAW_BUCKET}")
    
    # Estado inicial seguro (ej: inicio de 2024 o 2020)
    safe_state = {
        "donaciones": "2024-01-01",
        "gastos": "2024-01-01",
        "casos": "2024-01-01",
        "donantes": "2024-01-01"
    }

    client = get_storage_client()
    bucket = client.bucket(RAW_BUCKET)
    blob = bucket.blob(STATE_FILE_PATH)

    blob.upload_from_string(
        data=json.dumps(safe_state, indent=2),
        content_type='application/json'
    )
    
    print("✅ Watermarks reseteados a 2024-01-01.")
    print("👉 Ahora ejecuta 'make run' para re-procesar los datos.")

if __name__ == "__main__":
    reset_watermarks()
