"""
Script para ver el watermark actual de donaciones
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.state import load_watermarks

watermarks = load_watermarks()
print("📊 WATERMARKS ACTUALES:")
print("=" * 60)
for table, date in watermarks.items():
    print(f"  {table}: {date}")
print("=" * 60)
