from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

def test_gcp_connection():
    print("🔄 Probando conexión a Google Cloud Storage...")
    
    # Verificar credenciales
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds:
        print(f"🔑 Usando credenciales desde: {creds}")
    else:
        print("⚠️ No se encontró GOOGLE_APPLICATION_CREDENTIALS. Usando Application Default Credentials (ADC)...")

    try:
        client = storage.Client()
        buckets = list(client.list_buckets())
        
        print("\n✅ Conexión exitosa. Buckets encontrados:")
        if not buckets:
            print("   (No hay buckets en este proyecto)")
        else:
            for b in buckets:
                print(f"   - {b.name}")
                
    except Exception as e:
        print(f"\n❌ Error conectando a GCP: {e}")
        print("   Asegúrate de haber ejecutado: gcloud auth application-default login")

if __name__ == "__main__":
    test_gcp_connection()
