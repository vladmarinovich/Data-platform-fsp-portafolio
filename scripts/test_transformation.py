import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Definir la función EXACTA que tenemos en el extractor
def validate_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # 1. Fechas: Convertir a datetime estricto (Keywords más seguros)
    date_keywords = ['fecha', 'created_at', 'updated_at', 'timestamp', 'last_modified_at', '_date', 'date_']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in date_keywords):
            try:
                # errors='coerce' pone NaT si falla
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass 

    # 2. IDs: Forzar conversión a Int64
    for col in df.columns:
        if col == 'id' or col.endswith('_id'):
            # errors='coerce' pone NaN si no es numero, luego astype('Int64') lo vuelve <NA>
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # 3. Textos: Forzar columnas de texto a String
    text_keywords = [
        'nota', 'descrip', 'observ', 'coment', 'detalle', 'nombre', 
        'mail', 'tel', 'cel', 'phone', 'dir', 'address', 'ciudad', 
        'pais', 'estado', 'status', 'tipo', 'category'
    ]
    for col in df.columns:
        if any(keyword in col.lower() for keyword in text_keywords):
            df[col] = df[col].astype(str)
            # Limpieza CRÍTICA: Convertir "nan", "None", "<NA>" de texto a None real (objeto)
            df[col] = df[col].replace({'nan': None, 'None': None, '<NA>': None})
            
    # 4. Red de Seguridad: Convertir objetos restantes a String para evitar conflictos
    for col in df.select_dtypes(include=['object']).columns:
        if not pd.api.types.is_string_dtype(df[col]):
             df[col] = df[col].astype(str).replace({'nan': None, 'None': None})
    
    return df

def run_test():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Lista de tablas a probar
    tables = ["donaciones", "gastos", "donantes", "casos", "hogar_de_paso", "proveedores"]
    
    print("🧪 INICIANDO PRUEBA DE TRANSFORMACIÓN (Sample 5 rows)\n")
    
    for table in tables:
        print(f"--- TABLA: {table.upper()} ---")
        try:
            response = client.table(table).select("*").limit(5).execute()
            data = response.data
            
            if not data:
                print("⚠️ Tabla vacía.")
                print("-" * 30)
                continue
                
            df_raw = pd.DataFrame(data)
            print(f"filas obtenidas: {len(df_raw)}")
            
            # Aplicar magia
            df_cleaned = validate_and_transform(df_raw.copy())
            
            # Mostrar NOMBRES y TIPOS reales
            print("\n📋 COLUMNAS REALES (Copiar estos nombres a BigQuery):")
            print(list(df_cleaned.columns))
            
            print("\n🔍 TIPOS DETECTADOS:")
            print(df_cleaned.dtypes)
            
            print("\n👀 MUESTRA DE DATOS (Primer registro como diccionario):")
            # Convertimos a dict para ver si sale 'nan' (texto) o None (nulo real)
            first_row = df_cleaned.iloc[0].to_dict()
            for k, v in first_row.items():
                val_type = type(v).__name__
                print(f"   {k}: {repr(v)}  (Tipo: {val_type})")
            
        except Exception as e:
            print(f"❌ Error probando tabla {table}: {e}")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_test()
