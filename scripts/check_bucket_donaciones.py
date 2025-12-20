"""
Script para diagnosticar el contenido del bucket raw_donaciones
"""
from google.cloud import storage
import sys
import os

# Agregar el path del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.etl.config as config

def check_bucket_structure():
    """Verifica la estructura del bucket y muestra archivos reales"""
    client = storage.Client(project=config.PROJECT_ID)
    bucket = client.bucket('fsp-pipeline-raw')
    
    print('📂 DIAGNÓSTICO DEL BUCKET: raw_donaciones')
    print('=' * 80)
    
    # Listar todos los blobs en donaciones
    prefix = 'supabase/donaciones/'
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    print(f'\n✅ Total de objetos encontrados: {len(blobs)}')
    print('\n' + '=' * 80)
    
    # Separar carpetas de archivos
    folders = []
    files = []
    
    for blob in blobs:
        # En GCS, las "carpetas" son objetos que terminan en /
        if blob.name.endswith('/'):
            folders.append(blob)
        else:
            files.append(blob)
    
    print(f'\n📁 Carpetas (objetos que terminan en /): {len(folders)}')
    for folder in folders[:10]:  # Primeras 10
        print(f'   {folder.name}')
    
    print(f'\n📄 Archivos reales (.parquet): {len(files)}')
    for file in files[:20]:  # Primeros 20
        size_mb = file.size / (1024 * 1024)
        print(f'   {file.name} ({size_mb:.2f} MB)')
    
    # Análisis por año/mes
    print('\n' + '=' * 80)
    print('📊 DISTRIBUCIÓN POR FECHA:')
    print('=' * 80)
    
    from collections import defaultdict
    distribution = defaultdict(int)
    
    for file in files:
        parts = file.name.split('/')
        # Buscar y= y m= en el path
        year = None
        month = None
        for part in parts:
            if part.startswith('y='):
                year = part.split('=')[1]
            elif part.startswith('m='):
                month = part.split('=')[1]
        
        if year and month:
            key = f'{year}-{month}'
            distribution[key] += 1
    
    for period in sorted(distribution.keys()):
        print(f'   {period}: {distribution[period]} archivos')
    
    # Mostrar estructura de un archivo de ejemplo
    if files:
        print('\n' + '=' * 80)
        print('🔍 EJEMPLO DE RUTA COMPLETA:')
        print('=' * 80)
        print(f'   {files[0].name}')

if __name__ == '__main__':
    check_bucket_structure()
