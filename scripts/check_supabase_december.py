"""
Script para verificar cuántas donaciones hay por día en diciembre 2025 en Supabase
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_supabase_client
from datetime import datetime

client = get_supabase_client()

print("🔍 VERIFICANDO DONACIONES EN DICIEMBRE 2025 EN SUPABASE")
print("=" * 80)

# Consultar donaciones de diciembre 2025
# Supabase almacena fechas en microsegundos
response = client.table('donaciones').select('id_donacion, fecha_donacion').gte(
    'fecha_donacion', 
    int(datetime(2025, 12, 1).timestamp() * 1000000)
).lte(
    'fecha_donacion',
    int(datetime(2025, 12, 31, 23, 59, 59).timestamp() * 1000000)
).execute()

donaciones = response.data

print(f"\n✅ Total de donaciones en diciembre 2025: {len(donaciones)}")

if donaciones:
    # Agrupar por día
    from collections import defaultdict
    by_day = defaultdict(int)
    
    for don in donaciones:
        # Convertir de microsegundos a fecha
        fecha_us = don['fecha_donacion']
        fecha = datetime.fromtimestamp(fecha_us / 1000000)
        day = fecha.day
        by_day[day] += 1
    
    print(f"\n📊 DISTRIBUCIÓN POR DÍA:")
    print("-" * 80)
    for day in sorted(by_day.keys()):
        print(f"  Día {day:02d}: {by_day[day]} donaciones")
else:
    print("\n⚠️ No hay donaciones en diciembre 2025")

print("\n" + "=" * 80)
