
import sys
import os

# Agregar root al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_supabase_client

def update_gastos_rechazados():
    """
    Actualiza todos los gastos con estado 'rechazado' a 'pagado' en Supabase.
    """
    print("🔌 Conectando a Supabase...")
    client = get_supabase_client()
    
    print("🔍 Buscando gastos rechazados...")
    # Primero contamos cuántos hay (opcional, pero bueno para confirmar)
    res_count = client.table('gastos').select('*', count='exact').eq('estado', 'rechazado').execute()
    count = res_count.count
    
    if count == 0:
        print("✅ No se encontraron gastos rechazados. Nada que actualizar.")
        return

    print(f"⚠️ Se encontraron {count} gastos rechazados.")
    print("🔄 Actualizando a 'pagado'...")
    
    # Update masivo
    # Nota: Supabase puede tener límites de filas por request, pero el cliente suele manejarlo
    # o aplicarlo a todos los que coincidan.
    try:
        # Actualizamos donde estado = 'rechazado'
        res_update = client.table('gastos').update({'estado': 'pagado'}).eq('estado', 'rechazado').execute()
        
        updated_count = len(res_update.data)
        print(f"✅ Éxito: Se han actualizado {updated_count} registros a 'pagado'.")
        
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")

if __name__ == "__main__":
    confirm = input("¿Seguro que quieres cambiar TODOS los gastos rechazados a 'pagado'? (SI/NO): ")
    if confirm.upper() == "SI":
        update_gastos_rechazados()
    else:
        print("Operación cancelada.")
