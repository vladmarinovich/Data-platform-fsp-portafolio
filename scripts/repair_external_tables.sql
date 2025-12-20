
-- =========================================================================================
-- SCRIPT DE REPARACIÓN DE TABLAS EXTERNAS
-- Ejecuta esto en la consola de BigQuery para que reconozcan el nuevo particionado.
-- =========================================================================================

-- 1. DONACIONES (Particionado por Fecha de Donación)
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.fsp_raw.raw_donaciones`
WITH PARTITION COLUMNS (
    y STRING, -- Año
    m STRING, -- Mes
    d STRING  -- Día
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/donaciones/y=*/m=*/d=*/*.parquet'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/donaciones',
    require_hive_partition_filter = FALSE
);

-- 2. GASTOS (Particionado por Fecha de Pago)
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.fsp_raw.raw_gastos`
WITH PARTITION COLUMNS (
    y STRING, -- Año
    m STRING, -- Mes
    d STRING  -- Día
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/gastos/y=*/m=*/d=*/*.parquet'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/gastos',
    require_hive_partition_filter = FALSE
);

-- 3. CASOS (Particionado por Fecha de Ingreso)
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.fsp_raw.raw_casos`
WITH PARTITION COLUMNS (
    y STRING, -- Año
    m STRING, -- Mes
    d STRING  -- Día
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/casos/y=*/m=*/d=*/*.parquet'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/casos',
    require_hive_partition_filter = FALSE
);

-- 4. DONANTES (Particionado por Created At)
CREATE OR REPLACE EXTERNAL TABLE `fsp-pipeline-project.fsp_raw.raw_donantes`
WITH PARTITION COLUMNS (
    y STRING, -- Año
    m STRING, -- Mes
    d STRING  -- Día
)
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://fsp-pipeline-raw/supabase/donantes/y=*/m=*/d=*/*.parquet'],
    hive_partition_uri_prefix = 'gs://fsp-pipeline-raw/supabase/donantes',
    require_hive_partition_filter = FALSE
);

-- =========================================================================================
-- Al terminar, verifica con: SELECT count(*) FROM fsp_raw.raw_donaciones WHERE y = '2024';
-- =========================================================================================
