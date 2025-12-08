import json
import src.etl.config as config
from src.etl.connect import get_storage_client

def load_watermarks() -> dict:
    """Descarga el archivo de watermarks desde GCS."""
    client = get_storage_client()
    bucket = client.bucket(config.RAW_BUCKET)
    blob = bucket.blob(config.STATE_FILE_PATH)
    
    if blob.exists():
        content = blob.download_as_text()
        return json.loads(content)
    return {}

def save_watermarks(watermarks: dict):
    """Guarda el archivo actualizado de watermarks en GCS."""
    client = get_storage_client()
    bucket = client.bucket(config.RAW_BUCKET)
    blob = bucket.blob(config.STATE_FILE_PATH)
    
    blob.upload_from_string(
        json.dumps(watermarks, indent=4), 
        content_type="application/json"
    )
    print(f"💾 Estado actualizado en: gs://{config.RAW_BUCKET}/{config.STATE_FILE_PATH}")
