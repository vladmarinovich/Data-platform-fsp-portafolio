
import sys
import os

# Agregar root al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_storage_client
from src.etl.config import RAW_BUCKET

def nuke_bucket():
    """
    BORRA TODO EL CONTENIDO DEL BUCKET.
    PELIGROSO: SOLO USAR EN DATA DE PRUEBA.
    """
    print(f"☢️ INICIANDO BORRADO NUCLEAR DEL BUCKET: {RAW_BUCKET}")
    
    client = get_storage_client()
    bucket = client.bucket(RAW_BUCKET)
    
    blobs = list(bucket.list_blobs())
    
    if not blobs:
        print("   Bucket ya está vacío.")
        return

    print(f"   Encontrados {len(blobs)} archivos para eliminar...")
    
    from concurrent.futures import ThreadPoolExecutor

    def delete_blob_safe(blob):
        try:
            blob.delete()
        except:
            pass

    with ThreadPoolExecutor(max_workers=50) as executor:
        list(executor.map(delete_blob_safe, blobs))

    print("✅ BUCKET COMPLETAMENTE LIMPIO.")

if __name__ == "__main__":
    confirm = input(f"¿Estás seguro de borrar TODO en {RAW_BUCKET}? (escribe 'SI'): ")
    if confirm == "SI":
        nuke_bucket()
    else:
        print("Operación cancelada.")
