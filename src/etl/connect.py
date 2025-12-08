from supabase import create_client, Client
from google.cloud import storage
import src.etl.config as config

def get_supabase_client() -> Client:
    """Retorna un cliente autenticado de Supabase."""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError("❌ Faltan credenciales de Supabase en .env")
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_storage_client() -> storage.Client:
    """Retorna un cliente autenticado de Google Cloud Storage."""
    return storage.Client(project=config.PROJECT_ID)
