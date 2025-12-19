import pandas as pd

def validate_and_transform(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Aplica reglas estrictas de tipado y limpieza.
    - Fechas -> Datetime
    - IDs -> Int64
    - Textos -> String (sin 'nan')
    - Montos -> Float64
    - Exclusiones de campos sensibles
    """
    if df.empty:
        return df
        
    # EXCLUSIONES ESPECÍFICAS (Privacidad / Peso)
    if table_name == 'donantes':
        cols_to_drop = ['notas', 'archivos']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    # 1. Fechas: Convertir a datetime estricto
    date_keywords = ['fecha', 'created_at', 'updated_at', 'timestamp', 'last_modified_at', '_date', 'date_']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in date_keywords):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass 

    # 2. Montos: Convertir a Float64
    money_keywords = ['presupuesto', 'costo_estimado', 'monto', 'valor_total']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in money_keywords):
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')

    # 3. IDs: Forzar conversión a Int64
    for col in df.columns:
        if col == 'id' or col.endswith('_id'):
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # 4. Booleanos: Forzar conversión a tipo 'boolean' (Nullable)
    # Corrección para evitar: "Parquet column has type INT32 which does not match target BOOL"
    bool_keywords = ['consentimiento', 'activo', 'is_', 'has_']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in bool_keywords):
            # Convertimos a 'boolean' de Pandas que soporta Nulos (pd.NA)
            # Primero nos aseguramos que 1/0 sean True/False
            df[col] = df[col].replace({1: True, 0: False, '1': True, '0': False})
            df[col] = df[col].astype('boolean')

    # 5. Textos: Forzar columnas de texto a String limpio
    text_keywords = [
        'nota', 'descrip', 'observ', 'coment', 'detalle', 'nombre', 
        'mail', 'tel', 'cel', 'phone', 'dir', 'address', 'ciudad', 
        'pais', 'estado', 'status', 'tipo', 'category', 'raza', 'especie',
        'documento', 'origen', 'frecuencia', 'metodo', 'referencia'
    ]
    for col in df.columns:
        if any(keyword in col.lower() for keyword in text_keywords):
            df[col] = df[col].astype(str).replace({'nan': None, 'None': None, '<NA>': None})
            
    # 5. Red de Seguridad (Objetos a String)
    for col in df.select_dtypes(include=['object']).columns:
        if not pd.api.types.is_string_dtype(df[col]):
             df[col] = df[col].astype(str).replace({'nan': None, 'None': None})

    # 6. Integridad de Llaves Primarias (PKs) Explícita
    pk_columns = ["id", "id_caso", "id_donante", "id_gasto", "id_hogar_de_paso", "id_proveedor", "id_donacion"]
    for col in pk_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            
    return df
