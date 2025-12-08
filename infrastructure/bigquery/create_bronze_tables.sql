-- ========================================================================================
-- Script de Creación de Capa Bronze (BigLake Tables)
-- Proyecto: Salvando Patitas Data Platform (SPDP)
-- Descripción: Mapea los archivos Parquet en GCS a tablas externas en BigQuery.
--              Configura el particionado Hive (y, m, d) para optimización de costos.
-- ========================================================================================

-- 1. Crear Dataset (Si no existe)
CREATE SCHEMA IF NOT EXISTS `fsp-pipeline-project.spdp_bronze`
OPTIONS(
  location="us-central1",
  description="Capa Bronze: Datos crudos (RAW) mapeados directamente desde GCS."
);

-- ========================================================================================
-- 2. Tablas Transaccionales (Incrementales)
-- ========================================================================================

-- Tabla: donaciones
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.donaciones`
WITH PARTITION COLUMNS (
    y STRING, -- Año de la partición
    m STRING, -- Mes de la partición
    d STRING  -- Día de la partición
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/donaciones/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/donaciones',
    require_hive_partition_filter = FALSE
);

-- Tabla: gastos
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.gastos`
WITH PARTITION COLUMNS (
    y STRING,
    m STRING,
    d STRING
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/gastos/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/gastos',
    require_hive_partition_filter = FALSE
);

-- ========================================================================================
-- 3. Tablas Maestras (Full Load Snapshots)
-- Nota: Estas tablas tienen múltiples copias de los mismos datos (una por día de ejecución).
--       En la capa Silver se deberá seleccionar solo el último snapshot (d más reciente).
-- ========================================================================================

-- Tabla: donantes
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.donantes`
WITH PARTITION COLUMNS (
    y STRING,
    m STRING,
    d STRING
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/donantes/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/donantes',
    require_hive_partition_filter = FALSE
);

-- Tabla: casos
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.casos`
WITH PARTITION COLUMNS (
    y STRING,
    m STRING,
    d STRING
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/casos/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/casos',
    require_hive_partition_filter = FALSE
);

-- Tabla: hogar_de_paso
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.hogar_de_paso`
WITH PARTITION COLUMNS (
    y STRING,
    m STRING,
    d STRING
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/hogar_de_paso/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/hogar_de_paso',
    require_hive_partition_filter = FALSE
);

-- Tabla: proveedores
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.spdp_bronze.proveedores`
WITH PARTITION COLUMNS (
    y STRING,
    m STRING,
    d STRING
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/proveedores/*'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/proveedores',
    require_hive_partition_filter = FALSE
);
