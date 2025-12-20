"""
Script para actualizar created_at y last_modified_at con la fecha_donacion
cuando estos campos son NULL en la tabla donaciones
Usa la API de Supabase para hacer el update
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_supabase_client

client = get_supabase_client()

print("🔧 ACTUALIZANDO REGISTROS CON TIMESTAMPS NULL")
print("=" * 80)

# Paso 1: Obtener registros con NULL
print("\n📊 Buscando registros con created_at o last_modified_at NULL...")
response = client.table('donaciones').select('id_donacion, fecha_donacion, created_at, last_modified_at').or_(
    'created_at.is.null,last_modified_at.is.null'
).execute()

registros_null = response.data
print(f"   Encontrados: {len(registros_null)} registros con timestamps NULL")

if not registros_null:
    print("\n✅ No hay registros para actualizar!")
    exit(0)

# Paso 2: Actualizar cada registro
print(f"\n🔄 Actualizando {len(registros_null)} registros...")
updated_count = 0
errors = 0

for registro in registros_null:
    id_donacion = registro['id_donacion']
    fecha_donacion = registro['fecha_donacion']
    created_at = registro['created_at'] or fecha_donacion
    last_modified_at = registro['last_modified_at'] or fecha_donacion
    
    try:
        client.table('donaciones').update({
            'created_at': created_at,
            'last_modified_at': last_modified_at
        }).eq('id_donacion', id_donacion).execute()
        
        updated_count += 1
        if updated_count % 100 == 0:
            print(f"   ✅ Progreso: {updated_count}/{len(registros_null)} registros actualizados...")
    except Exception as e:
        errors += 1
        print(f"   ❌ Error actualizando registro {id_donacion}: {e}")

print(f"\n✅ Actualización completada!")
print(f"   Registros actualizados: {updated_count}")
print(f"   Errores: {errors}")
print("\n" + "=" * 80)
