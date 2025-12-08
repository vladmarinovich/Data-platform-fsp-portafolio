from google.cloud import storage
import os
import json
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
RAW_BUCKET = os.getenv("RAW_BUCKET")

def clean_specific_table_and_reset_watermark(table_name="gastos"):
    print(f"🧹 Iniciando limpieza quirúrgica para tabla: {table_name}")
    
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(RAW_BUCKET)
    
    # 1. Borrar archivos Parquet de la tabla
    prefix = f"supabase/{table_name}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    if blobs:
        print(f"   Encontrados {len(blobs)} archivos para borrar en {prefix}...")
        batch_size = 100
        for i in range(0, len(blobs), batch_size):
            batch = blobs[i:i+batch_size]
            with client.batch():
                for blob in batch:
                    blob.delete()
        print("   ✅ Archivos Parquet borrados.")
    else:
        print("   ⚠️ No se encontraron archivos para borrar.")

    # 2. Resetear Watermark solo para esa tabla
    state_blob = bucket.blob("state/watermarks.json")
    if state_blob.exists():
        content = state_blob.download_as_text()
        watermarks = json.loads(content)
        
        if table_name in watermarks:
            print(f"   🔄 Reseteando watermark de '{table_name}' (era: {watermarks[table_name]})")
            del watermarks[table_name]
            state_blob.upload_from_string(json.dumps(watermarks, indent=4), content_type="application/json")
            print("   ✅ Watermark actualizado en GCS.")
        else:
            print(f"   ℹ️ No se encontró watermark para '{table_name}'.")

if __name__ == "__main__":
    clean_specific_table_and_reset_watermark("gastos")
