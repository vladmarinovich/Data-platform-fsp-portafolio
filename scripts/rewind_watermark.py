import json
from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
RAW_BUCKET = os.getenv("RAW_BUCKET")
STATE_FILE_PATH = "state/watermarks.json"

def rewind_watermark():
    print("⏪ Rebobinando watermark...")
    
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(RAW_BUCKET)
    blob = bucket.blob(STATE_FILE_PATH)
    
    if not blob.exists():
        print("❌ No existe el archivo de watermarks.")
    # Definir qué tablas y a qué fecha resetear
    # Usa "2020-01-01" para forzar una recarga histórica completa.
    tables_to_rewind = {
        "donantes": "2020-01-01"
    }
    
    # Cargar estado actual
    state_blob = bucket.blob("state/watermarks.json")
    if state_blob.exists():
        watermarks = json.loads(state_blob.download_as_text())
    else:
        watermarks = {}

    print(f"Estado actual: {watermarks}")

    # Aplicar Rewind
    for table, new_date in tables_to_rewind.items():
        print(f"🔄 Rebobinando '{table}' a {new_date}...")
        watermarks[table] = new_date

    # Guardar
    state_blob.upload_from_string(json.dumps(watermarks, indent=4), content_type="application/json")
    print("✅ Watermarks actualizados. La próxima ejecución descargará todo el historial.")

if __name__ == "__main__":
    rewind_watermark()
