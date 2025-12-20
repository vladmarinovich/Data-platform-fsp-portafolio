"""
Script para verificar si los archivos de donaciones están llegando correctamente
a BigQuery desde el bucket raw.
"""

# Query para verificar la distribución de datos en raw_donaciones
query_check_raw = """
SELECT 
  COUNT(*) as total_registros,
  MIN(fecha_donacion) as fecha_minima,
  MAX(fecha_donacion) as fecha_maxima,
  COUNT(DISTINCT DATE(fecha_donacion)) as dias_distintos,
  COUNT(DISTINCT FORMAT_DATE('%Y-%m', DATE(fecha_donacion))) as meses_distintos
FROM `fsp-pipeline-project.fsp_raw.raw_donaciones`
"""

# Query para ver la distribución por partición (si existe)
query_partition_info = """
SELECT 
  _PARTITIONTIME as partition_date,
  COUNT(*) as registros
FROM `fsp-pipeline-project.fsp_raw.raw_donaciones`
WHERE _PARTITIONTIME IS NOT NULL
GROUP BY partition_date
ORDER BY partition_date DESC
LIMIT 20
"""

# Query para ver las últimas donaciones
query_latest_records = """
SELECT 
  id_donacion,
  fecha_donacion,
  monto,
  estado,
  last_modified_at
FROM `fsp-pipeline-project.fsp_raw.raw_donaciones`
ORDER BY last_modified_at DESC
LIMIT 10
"""

print("=" * 80)
print("QUERIES PARA DIAGNOSTICAR RAW_DONACIONES")
print("=" * 80)
print("\n1. VERIFICAR DISTRIBUCIÓN GENERAL:")
print(query_check_raw)
print("\n2. VERIFICAR PARTICIONES:")
print(query_partition_info)
print("\n3. VER ÚLTIMOS REGISTROS:")
print(query_latest_records)
print("\n" + "=" * 80)
print("Copia y pega estas queries en la consola de BigQuery para diagnosticar.")
print("=" * 80)
