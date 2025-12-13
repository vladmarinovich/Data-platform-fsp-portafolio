import argparse
import sys
import os
import json
from datetime import datetime

# Hack para importar módulos del src desde scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_storage_client
from src.etl.state import load_watermarks, save_watermarks
from src.etl import config

def list_status():
    """Muestra el estado actual de los watermarks."""
    print(f"\n📊 ESTADO ACTUAL DEL PIPELINE")
    print(f"Archivo: gs://{config.RAW_BUCKET}/{config.STATE_FILE_PATH}")
    print("-" * 40)
    
    watermarks = load_watermarks()
    if not watermarks:
        print("⚠️ No se encontró archivo de estado o está vacío.")
        return

    print(f"{'TABLA':<20} | {'LAST_MODIFIED_AT':<20}")
    print("-" * 40)
    for table, date in watermarks.items():
        print(f"{table:<20} | {date:<20}")
    print("-" * 40)

def reset_watermark(table, new_date):
    """Resetea el watermark de una tabla para causar un reprocesamiento."""
    print(f"\n⏪ REWIND DATA: {table}")
    
    # Validar fecha
    try:
        datetime.strptime(new_date, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Formato de fecha inválido. Usar YYYY-MM-DD")
        return

    watermarks = load_watermarks()
    old_date = watermarks.get(table, "N/A")
    
    watermarks[table] = new_date
    save_watermarks(watermarks)
    
    print(f"✅ Éxito: Watermark de '{table}' actualizado.")
    print(f"   Anterior: {old_date}")
    print(f"   Nuevo   : {new_date}")
    print("👉 En la próxima ejecución, el pipeline extraerá data desde esta fecha.")

def purge_table(table):
    """Opción Nuclear: Borra todos los archivos de una tabla en GCS."""
    print(f"\n☢️  NUT CLEAR OPTION: {table}")
    print(f"⚠️  ADVERTENCIA: Esto borrará TODOS los datos de 'gs://{config.RAW_BUCKET}/{table}/'")
    confirm = input("¿Estás seguro? Escribe 'borrar' para confirmar: ")
    
    if confirm != "borrar":
        print("Cancelado.")
        return

    client = get_storage_client()
    bucket = client.bucket(config.RAW_BUCKET)
    blobs = list(bucket.list_blobs(prefix=f"{table}/"))
    
    if not blobs:
        print(f"ℹ️  No se encontraron archivos en {table}/ para borrar.")
        return
        
    print(f"🗑️  Borrando {len(blobs)} archivos...")
    for blob in blobs:
        blob.delete()
        
    # También reseteamos el watermark porque la data ya no existe
    print("🔄 Reseteando watermark a 1970-01-01...")
    reset_watermark(table, "1970-01-01")
    
    print("Done. La tabla está limpia y lista para una recarga completa (Full Load).")

def main():
    parser = argparse.ArgumentParser(description="🛠️ SPDP Maintenance Toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando: status
    subparsers.add_parser("status", help="Ver watermarks actuales")

    # Comando: reset
    parser_reset = subparsers.add_parser("reset", help="Retroceder el tiempo (Rewind)")
    parser_reset.add_argument("--table", required=True, help="Nombre de la tabla")
    parser_reset.add_argument("--date", required=True, help="Nueva fecha (YYYY-MM-DD)")

    # Comando: purge
    parser_purge = subparsers.add_parser("purge", help="Borrar datos físicos (Nuclear)")
    parser_purge.add_argument("--table", required=True, help="Nombre de la tabla a purgar")

    args = parser.parse_args()

    if args.command == "status":
        list_status()
    elif args.command == "reset":
        reset_watermark(args.table, args.date)
    elif args.command == "purge":
        purge_table(args.table)

if __name__ == "__main__":
    main()
