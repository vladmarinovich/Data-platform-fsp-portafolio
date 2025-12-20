"""
Script para resetear el watermark de donaciones a una fecha específica
Esto forzará el reprocesamiento de todos los registros desde esa fecha
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.state import load_watermarks, save_watermarks

# Fecha desde la cual queremos reprocesar (inicio de diciembre 2025)
RESET_DATE = "2025-12-01"

print("🔄 RESETEO DE WATERMARK PARA DONACIONES")
print("=" * 60)

# Cargar watermarks actuales
watermarks = load_watermarks()
print(f"\n📊 Watermark actual de donaciones: {watermarks.get('donaciones', 'No existe')}")

# Resetear solo donaciones
watermarks['donaciones'] = RESET_DATE
print(f"✅ Nuevo watermark de donaciones: {RESET_DATE}")

# Guardar
save_watermarks(watermarks)
print(f"\n💾 Watermark actualizado exitosamente!")
print(f"   Ahora ejecuta el pipeline para reprocesar desde {RESET_DATE}")
print("=" * 60)
