from google.cloud import storage
import os
import json
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
RAW_BUCKET = os.getenv("RAW_BUCKET")

def clean_proveedores_partitions():
    print(f"🧹 Iniciando limpieza de particiones antiguas para 'proveedores'...")
    
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(RAW_BUCKET)
    
    # Borrar todo lo que sea partición diaria (y=...)
    # Dejaremos intacta la carpeta 'latest' si existiera (aunque el extractor la recreará)
    prefix = "supabase/proveedores/y="
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    if blobs:
        print(f"   Encontrados {len(blobs)} archivos antiguos particionados...")
        batch_size = 100
        for i in range(0, len(blobs), batch_size):
            batch = blobs[i:i+batch_size]
            with client.batch():
                for blob in batch:
                    blob.delete()
        print("   ✅ Particiones antiguas eliminadas. El bucket está listo para la estrategia Snapshot.")
    else:
        print("   ℹ️ No se encontraron particiones antiguas. Limpio.")

if __name__ == "__main__":
    clean_proveedores_partitions()
