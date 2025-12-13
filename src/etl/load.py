import os
import pandas as pd
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage
import src.etl.config as config
from src.etl.connect import get_storage_client

def upload_to_gcs_blob(bucket_name, blob_path, content_bytes, content_type="application/octet-stream"):
    """Función atómica para upload."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content_bytes, content_type=content_type)
    return blob_path

def upload_incremental_partitions(df: pd.DataFrame, table_name: str, date_col: str):
    """
    Sube un DataFrame particionado por fecha (y=YYYY/m=MM/d=DD) usando ThreadPool.
    """
    if df.empty:
        return

    # 1. Convertir a datetime forzando UTC y coerción de errores
    # Esto asegura que todo tenga zona horaria (UTC) y los errores sean NaT
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', utc=True)
    
    # 2. Detección y Manejo de Fechas Nulas (NaT)
    null_dates_count = df[date_col].isna().sum()
    if null_dates_count > 0:
        print(f"⚠️ ¡ADVERTENCIA! Se encontraron {null_dates_count} registros con fecha nula/inválida en '{table_name}'.")
        print(f"   🔧 Asignando fecha por defecto: 1970-01-01 UTC (para no perder datos).")
        # Usamos un Timestamp CON zona horaria para coincidir con el resto
        default_date = pd.Timestamp("1970-01-01").tz_localize("UTC")
        df[date_col] = df[date_col].fillna(default_date)
    
    # Crear columna temporal de fecha (solo YYYY-MM-DD)
    df['_partition_date'] = df[date_col].dt.date
    
    unique_dates = df['_partition_date'].unique()
    print(f"   Particionando en {len(unique_dates)} fechas distintas...")
    
    futures = []
    # MAX_WORKERS = 20 (Para no saturar I/O)
    with ThreadPoolExecutor(max_workers=20) as executor:
        for p_date in unique_dates:
            partition_df = df[df['_partition_date'] == p_date].copy()
            # Quitamos la columna auxiliar
            partition_df = partition_df.drop(columns=['_partition_date'])
            
            y = p_date.year
            m = f"{p_date.month:02d}"
            d = f"{p_date.day:02d}"
            
            filename = f"{table_name}_{p_date.isoformat()}.parquet"
            # Ruta estilo Hive
            path = f"{config.SOURCE_SYSTEM}/{table_name}/y={y}/m={m}/d={d}/{filename}"
            
            # Convertir a Parquet Bytes
            parquet_bytes = partition_df.to_parquet(index=False)
            
            # Subir asíncronamente
            futures.append(executor.submit(
                upload_to_gcs_blob, 
                config.RAW_BUCKET, 
                path, 
                parquet_bytes,
                "application/x-parquet"
            ))

    # Esperar y mostrar progreso
    print(f"🚀 Iniciando subida paralela de {len(futures)} archivos...")
    completed = 0
    total = len(futures)
    for f in as_completed(futures):
        try:
            path = f.result()
            completed += 1
            if completed % 10 == 0:
                print(f"   ✅ Progreso: {completed}/{total} archivos subidos...")
        except Exception as e:
            print(f"❌ Error subiendo archivo: {e}")

    print(f"✨ Subida completada: {completed} archivos procesados.")

def upload_snapshot(df: pd.DataFrame, table_name: str):
    """
    Sube un DataFrame completo en modo Snapshot (Overwrite).
    Ruta: latest/tabla.parquet
    """
    filename = f"{table_name}.parquet"
    path = f"{config.SOURCE_SYSTEM}/{table_name}/latest/{filename}"
    
    parquet_bytes = df.to_parquet(index=False)
    upload_to_gcs_blob(config.RAW_BUCKET, path, parquet_bytes, "application/x-parquet")
    
    print(f"   ✅ Snapshot actualizado: {path}")
    print(f"      (Filas: {len(df)})")
