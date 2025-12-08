from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
RAW_BUCKET = os.getenv("RAW_BUCKET")

def clean_bucket():
    print(f"🧹 Iniciando limpieza del bucket: {RAW_BUCKET}")
    
    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(RAW_BUCKET)
        
        # Listar y borrar blobs
        blobs = list(bucket.list_blobs(prefix="supabase/")) + list(bucket.list_blobs(prefix="state/"))
        
        if not blobs:
            print("   El bucket ya estaba limpio.")
            return

        print(f"   Encontrados {len(blobs)} archivos para borrar...")
        
        # Borrado en batch
        # Note: bucket.delete_blobs(blobs) is more efficient if available, but iterating is safer for small batches
        batch_size = 100
        for i in range(0, len(blobs), batch_size):
            batch = blobs[i:i+batch_size]
            try:
                with client.batch():
                    for blob in batch:
                        blob.delete()
            except Exception as e:
                print(f"   Error en batch, borrando uno por uno: {e}")
                for blob in batch:
                    blob.delete()
            
        print("✨ Limpieza completada exitosamente.")
    except Exception as e:
        print(f"❌ Error al limpiar bucket: {e}")

if __name__ == "__main__":
    clean_bucket()
