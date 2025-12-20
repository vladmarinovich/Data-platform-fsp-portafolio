"""
Script para verificar qué archivos hay en diciembre 2025 del bucket
Usa la misma conexión que nuke_bucket.py
"""
import sys
import os

# Agregar root al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_storage_client
from src.etl.config import RAW_BUCKET
from collections import defaultdict

def check_december_files():
    """Verifica archivos en diciembre 2025"""
    print("🔍 VERIFICANDO ARCHIVOS EN DICIEMBRE 2025")
    print("=" * 80)
    
    client = get_storage_client()
    bucket = client.bucket(RAW_BUCKET)
    
    # Listar todos los blobs en donaciones/y=2025/m=12/
    prefix = "supabase/donaciones/y=2025/m=12/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    # Separar carpetas de archivos
    files = [b for b in blobs if not b.name.endswith('/')]
    folders = [b for b in blobs if b.name.endswith('/')]
    
    print(f"\n📊 RESUMEN:")
    print(f"  Total objetos: {len(blobs)}")
    print(f"  Carpetas: {len(folders)}")
    print(f"  Archivos .parquet: {len(files)}")
    
    if files:
        print(f"\n📄 ARCHIVOS ENCONTRADOS:")
        print("-" * 80)
        
        # Agrupar por día
        by_day = defaultdict(list)
        for file in files:
            # Extraer el día del path
            parts = file.name.split('/')
            for part in parts:
                if part.startswith('d='):
                    day = part.split('=')[1]
                    by_day[day].append(file)
                    break
        
        # Mostrar por día
        for day in sorted(by_day.keys()):
            day_files = by_day[day]
            total_size = sum(f.size for f in day_files)
            size_mb = total_size / (1024 * 1024)
            print(f"  📅 Día {day}: {len(day_files)} archivo(s) - {size_mb:.2f} MB")
            for f in day_files:
                print(f"      └─ {f.name.split('/')[-1]}")
    else:
        print(f"\n⚠️ NO SE ENCONTRARON ARCHIVOS .parquet")
        if folders:
            print(f"\n📁 Carpetas encontradas (vacías):")
            for folder in folders[:10]:
                print(f"  {folder.name}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        check_december_files()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
