# Salvando Patitas Data Platform

Un pipeline ELT serverless diseñado para ingestar, transformar y analizar datos operativos para la fundación *Salvando Patitas*. El sistema integra fuentes de Supabase (PostgreSQL) en un ecosistema Google Cloud Platform, utilizando **Cloud Run Jobs** para la extracción orquestada y **BigQuery + Dataform** para el almacenamiento y transformaciones de datos.

## Definición del Problema

La fundación enfrentaba desafíos con la fragmentación de datos operativos a través de su aplicación CRM personalizada. Acceder a insights históricos requería extracciones manuales de datos, lo que llevaba a inconsistencias y reportes desactualizados.

Esta plataforma aborda estos problemas mediante:
*   **Centralización de Datos**: Unificación de registros de donaciones, gastos y gestión de casos en una única fuente analítica de verdad.
*   **Consistencia**: Implementación de estrategias robustas de carga incremental para capturar todos los cambios de datos sin procesamiento redundante.
*   **Confiabilidad Operativa**: Automatización del pipeline para ejecutarse diariamente con mínima sobrecarga de mantenimiento, asegurando trazabilidad y manejo de errores.

## Arquitectura

La arquitectura sigue un patrón ELT modular, aprovechando componentes serverless para minimizar costos operativos mientras se maximiza la escalabilidad.


![Diagrama de Arquitectura](docs/img/Flujo%20Pipeline.jpeg)

```
[Supabase (PostgreSQL)] 
       |
       | (Python ETL Container / Cloud Run Jobs)
       v
[Google Cloud Storage] <--- (Gestión de Estado / watermarks.json)
(Zona: Raw / Parquet)
       |
       | (Tablas Externas)
       v
[BigQuery: Capa Raw]
       |
       | (Ejecución Dataform)
       v
[BigQuery: Capa Silver] ---> [Dashboard en Looker Studio]
```

#### Modelo de Datos Operativo (CRM)
Para dar contexto sobre la complejidad de la fuente de datos, este es el modelo relacional que nuestro pipeline ingesta y transforma:

![Modelo de Datos Operativo](docs/img/oltp-layer-modelo-de-base-de-datos-transacional.jpeg)


### Componentes Principales
1.  **Extracción (Python)**: Una aplicación Python contenerizada extrae datos desde Supabase.
    *   **Tablas Incrementales**: Recupera solo registros modificados desde la última marca de agua de ejecución (persistida en GCS).
    *   **Tablas Snapshot**: Realiza recargas completas para tablas de dimensión pequeñas para asegurar integridad referencial.
    *   **Ingesta**: Los datos se escriben en GCS en formato Parquet particionado para un rendimiento de consulta óptimo.
    
    *Flujo Interno del Extractor (Inicialización y Estado):*
    ![ETL Init](docs/img/etl-unner-11-inicializacion-y-gestion-de-estado.jpeg)

    *Orquestación de Tablas:*
    ![ETL Orchestration](docs/img/etl-runner-12-orquestacion-de-tablas.jpeg)
2.  **Almacenamiento (GCS & BigQuery)**: Google Cloud Storage actúa como el Data Lake. BigQuery monta estos archivos como Tablas Externas (Capa Raw).
3.  **Transformación (Dataform)**: Pipelines SQLX transforman datos Raw hacia la capa Silver, aplicando limpieza, tipeo y lógica de negocio.
4.  **Orquestación**: Cloud Scheduler dispara el Job de Cloud Run diariamente.

## Ejecución en Producción

El pipeline está desplegado como un contenedor Docker en **Google Cloud Run Jobs**.

*   **Trigger**: Cloud Scheduler inicia el trabajo diariamente a las **07:00 AM (America/Santiago)**.
*   **Ejecución del Job**:
    1.  El contenedor inicia y carga la configuración desde variables de entorno.
    2.  Recupera el estado actual (`watermarks.json`) desde GCS.
    3.  Realiza la extracción incremental para tablas de alto volumen (`donaciones`, `gastos`, `casos`) y extracción snapshot para catálogos.
    4.  Tras la subida exitosa a GCS, actualiza el estado de la marca de agua.
    5.  (Integración Conectada) Dataform ejecuta las transformaciones posteriores.
*   **Monitoreo**: Logs de ejecución, métricas de volumen de datos y trazas de errores son capturados en Cloud Logging.

## Visualización y Documentación

*   **[Dashboard en Looker Studio](https://lookerstudio.google.com/u/0/reporting/cb2392ff-d151-4b16-9bc3-49df863ced2c/page/p_97ri4w4xyd)**
    *   Muestra la salida final del pipeline. Los evaluadores pueden verificar la frescura de los datos, agregaciones y la aplicación práctica de las capas de datos Gold/Silver.

*   **[Diagrama de Arquitectura y Sistemas (Miro)](https://miro.com/welcomeonboard/UkduTDRzZFZlSW9xek1EL2dwRG1XVG8rQmRvcVFWbGhRMEhjVHBmUnU5MSs0ek5LdlZxSHcyOE15UXNydlNkOHQ1N3ROTEdEd2dQOVhEcDN4MlF6S0d0WEJySWE5c2xhNGNnVHB1WXRGNGl2OWJZNlhydU00bWVoOFRZK095bkNhWWluRVAxeXRuUUgwWDl3Mk1qRGVRPT0hdjE=?share_link_id=538214555000)**
    *   Representación visual detallada de los componentes del sistema, flujo de datos e interacciones entre el CRM, el pipeline ETL y la capa de visualización.

## Decisiones Técnicas Clave

*   **Cloud Run Jobs para ETL**: Seleccionado por su naturaleza serverless. El tiempo de inicio es rápido y la facturación es por segundo. A diferencia de Cloud Functions, maneja tiempos de espera de validación más largos y procesamiento por lotes intensivo en memoria con gracia. A diferencia de Dataproc, requiere cero gestión de clústeres.
*   **BigQuery**: Elegido por su separación de almacenamiento y cómputo. Permite consultar archivos Parquet crudos directamente desde GCS sin costos de carga, y escala sin esfuerzo para consultas analíticas.
*   **Dataform**: Proporciona mejores prácticas de ingeniería de software a la transformación SQL (CI/CD, control de versiones, gestión de dependencias y pruebas de aserción), superior a la gestión de scripts SQL crudos programados vía cron.
*   **Carga Incremental con Estado Persistente**: Esencial para escalar. En lugar de recargar todo el conjunto de datos diariamente, el sistema rastrea la marca de tiempo `last_modified_at`. Esto reduce los costos de egreso de Supabase y el tiempo de procesamiento de minutos a segundos para deltas diarios.

## Estado de la Plataforma

*   **Implementado**:
    *   ✅ Pipeline de extracción completo (Python/Docker).
    *   ✅ Capa de almacenamiento (GCS Parquet + BigQuery Raw).
    *   ✅ Lógica de transformación (Capa Silver Dataform).
    *   ✅ Orquestación (Cloud Run + Scheduler).
    *   ✅ Visualización (Dashboard Básico).

*   **Pendiente**:
    *   🚧 Modelado de Capa Gold (Esquema Estrella).
    *   🚧 Aserciones de Calidad de Datos Avanzadas (Nivel Gold).
    *   🚧 Integración ML.

## Próximos Pasos (Roadmap)

*   **Implementación Capa Gold**: Desarrollar modelos dimensionales finales optimizados para herramientas de BI.
*   **Aserciones Estrictas**: Implementar pruebas de conteo de filas y distribución para bloquear datos incorrectos antes de que lleguen a la capa Gold.
*   **Integración Vertex AI**: Desplegar modelos de ML para predecir tendencias de donación basadas en datos históricos.
*   **Interfaz Agéntica**: Implementar un agente basado en LLM para permitir consultas en lenguaje natural del conjunto de datos.
*   **Exposición API**: Crear una capa API ligera para servir métricas procesadas de vuelta al CRM operativo.
