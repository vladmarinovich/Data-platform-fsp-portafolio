import pandas as pd
from supabase import Client

def extract_data(client: Client, table_name: str, watermark_col: str = None, watermark_val: str = None) -> pd.DataFrame:
    """
    Extrae datos de una tabla de Supabase con paginación automática.
    Si se provee watermark, filtra por >= watermark_val.
    """
    print(f"🔄 Extrayendo tabla: {table_name}...")
    all_data = []
    page_size = 1000
    offset = 0
    
    query = client.table(table_name).select("*")
    
    if watermark_col and watermark_val:
        print(f"   Filtro: {watermark_col} >= '{watermark_val}'")
        query = query.gte(watermark_col, watermark_val).order(watermark_col, desc=False)
    
    while True:
        try:
            response = query.range(offset, offset + page_size - 1).execute()
            data = response.data
            
            if not data:
                break
                
            all_data.extend(data)
            
            if len(data) < page_size:
                break
                
            offset += page_size
            print(f"   ...obtenidas {len(all_data)} filas...")
            
        except Exception as e:
            print(f"❌ Error extrayendo batch (offset {offset}): {e}")
            raise e

    return pd.DataFrame(all_data)
