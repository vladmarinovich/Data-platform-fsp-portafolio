"""
Script simple para contar donaciones por mes en 2025
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.connect import get_supabase_client
from datetime import datetime
from collections import defaultdict

client = get_supabase_client()

print("🔍 ANALIZANDO DONACIONES EN 2025")
print("=" * 80)

# Obtener TODAS las donaciones
print("\n📊 Obteniendo todas las donaciones...")
all_donaciones = []
offset = 0
limit = 1000

while True:
    response = client.table('donaciones').select(
        'id_donacion, fecha_donacion, created_at, last_modified_at'
    ).range(offset, offset + limit - 1).execute()
    
    if not response.data:
        break
    
    all_donaciones.extend(response.data)
    offset += limit
    print(f"   ...obtenidas {len(all_donaciones)} donaciones...")
    
    if len(response.data) < limit:
        break

print(f"\n✅ Total donaciones en la base: {len(all_donaciones)}")

# Analizar por año y mes
by_year_month = defaultdict(lambda: defaultdict(int))
null_count = 0

for don in all_donaciones:
    # Verificar NULLs
    if don['last_modified_at'] is None or don['created_at'] is None:
        null_count += 1
    
    # Convertir fecha_donacion
    try:
        fecha_us = don['fecha_donacion']
        if fecha_us:
            fecha = datetime.fromtimestamp(fecha_us / 1000000)
            year = fecha.year
            month = fecha.month
            by_year_month[year][month] += 1
    except:
        pass

print(f"\n⚠️ Registros con created_at o last_modified_at NULL: {null_count}")

print(f"\n📊 DISTRIBUCIÓN POR AÑO Y MES:")
print("-" * 80)
for year in sorted(by_year_month.keys()):
    print(f"\n  Año {year}:")
    for month in sorted(by_year_month[year].keys()):
        count = by_year_month[year][month]
        print(f"    Mes {month:02d}: {count} donaciones")

# Detalle de diciembre 2025
print(f"\n📅 DETALLE DICIEMBRE 2025:")
print("-" * 80)
by_day = defaultdict(int)

for don in all_donaciones:
    try:
        fecha_us = don['fecha_donacion']
        if fecha_us:
            fecha = datetime.fromtimestamp(fecha_us / 1000000)
            if fecha.year == 2025 and fecha.month == 12:
                by_day[fecha.day] += 1
    except:
        pass

if by_day:
    for day in sorted(by_day.keys()):
        print(f"  Día {day:02d}: {by_day[day]} donaciones")
else:
    print("  No hay donaciones en diciembre 2025")

print("\n" + "=" * 80)
