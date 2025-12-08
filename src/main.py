from datetime import datetime as dt
import sys
import os

# TRUCO: Agregar la carpeta raíz del proyecto al PATH de Python
# Esto permite que 'import src.etl...' funcione aunque ejecutes el archivo directamente.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.etl.config as config
from src.etl.connect import get_supabase_client
from src.etl.state import load_watermarks, save_watermarks
from src.etl.extract import extract_data
from src.etl.transform import validate_and_transform
from src.etl.load import upload_incremental_partitions, upload_snapshot

def run_incremental_pipeline(client, watermarks):
    """Ejecuta el pipeline para tablas incrementales (Append)."""
    print("\n🚀 --- MODO INCREMENTAL ---")
    
    for table, date_col in config.INCREMENTAL_TABLES.items():
        last_val = watermarks.get(table, "2020-01-01")
        
        # 1. EXTRACT
        df = extract_data(client, table, watermark_col=date_col, watermark_val=last_val)
        
        if df.empty:
            print(f"⚠️ Tabla {table} sin cambios nuevos.")
            continue
            
        # 2. TRANSFORM
        df = validate_and_transform(df, table)
        
        # Calcular nuevo watermark (MAX de la columna fecha)
        # Convertimos a datetime para sacar el max real, luego a str ISO
        try:
            max_date = pd.to_datetime(df[date_col]).max()
            new_watermark = max_date.date().isoformat()
        except:
            # Fallback seguro si falla la conversion
            new_watermark = dt.today().date().isoformat()

        # 3. LOAD (Partitioned)
        upload_incremental_partitions(df, table, date_col)
        
        # Actualizar estado
        if new_watermark > last_val:
            watermarks[table] = new_watermark
            print(f"   Nuevo watermark para {table}: {new_watermark}")

def run_snapshot_pipeline(client):
    """Ejecuta el pipeline para tablas maestras (Overwrite)."""
    print("\n📸 --- MODO SNAPSHOT ---")
    
    for table in config.FULL_LOAD_TABLES:
        # 1. EXTRACT (Full)
        df = extract_data(client, table)
        
        if df.empty:
            print(f"⚠️ Tabla {table} vacía.")
            continue
            
        # 2. TRANSFORM
        df = validate_and_transform(df, table)
        
        # 3. LOAD (Snapshot)
        upload_snapshot(df, table)

def main():
    print(f"🏁 Iniciando Pipeline SPDP - {dt.now()}")
    
    # 0. SETUP
    client = get_supabase_client()
    watermarks = load_watermarks()
    
    try:
        # 1. INCREMENTAL
        import pandas as pd # Needed for max_date calculation (lazy import fixed above but better safe)
        run_incremental_pipeline(client, watermarks)
        
        # 2. SNAPSHOT
        run_snapshot_pipeline(client)
        
        # 3. COMMIT STATE
        save_watermarks(watermarks)
        print("✅ Pipeline finalizado exitosamente.")
        
    except Exception as e:
        print(f"🔥 Error Crítico en el Pipeline: {e}")
        exit(1)

if __name__ == "__main__":
    main()
