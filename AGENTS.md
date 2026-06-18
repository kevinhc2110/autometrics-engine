# autometrics-engine

Pipeline automatizado de análisis retail. Extrae datos desde SQL Server, los transforma en un Data Warehouse PostgreSQL con esquema estrella, calcula KPIs y genera insights + reportes ejecutivos vía Gemini. Orquestado con arq + Redis, servido con FastAPI y desplegado con Docker Compose.

## Package name

`autometrics_engine` (source at `src/autometrics_engine/`). All imports, Dockerfile CMD, and docker-compose use `autometrics_engine`.

## Entrypoint

```bash
docker compose up --build         # full stack
docker compose up --build -d      # detached
docker compose down -v            # stop + delete volumes
```

## Services

| Service       | Container             | Dockerfile                | Port |
| ------------- | --------------------- | ------------------------- | ---- |
| **sqlserver** | autometrics-sqlserver | `db/sqlserver/Dockerfile` | 1433 |
| **db**        | autometrics-db        | `db/Dockerfile`           | 5432 |
| **redis**     | autometrics-redis     | `redis:7-alpine`          | 6379 |
| **app**       | autometrics-app       | `Dockerfile` (root)       | 8000 |
| **worker**    | autometrics-worker    | `Dockerfile` (root)       | —    |

## Cron schedule (arq worker)

Worker corre via `arq autometrics_engine.infrastructure.worker.settings.WorkerSettings`:

| Hora    | Días    | Función             | Qué hace                                |
| ------- | ------- | ------------------- | --------------------------------------- |
| 6:00 AM | Diario  | `run_etl_pipeline`  | SQL Server → Warehouse + KPIs diarios   |
| 6:30 AM | Domingo | `generate_insights` | KPIs → Gemini → insights semanales      |
| 7:00 AM | Domingo | `generate_report`   | KPIs + insights → Gemini → reporte HTML |

Config en `infrastructure/worker/settings.py`.

## Pipeline flow

```text
SQL Server → run_etl_pipeline → Warehouse + KPIs → generate_insights → insights → generate_report → reports
```

## DB schema (`db/init.sql`)

- **Dimensions**: `dim_product`, `dim_store`, `dim_date` (seeded 2020–2030)
- **Facts**: `fact_sales`
- **KPIs**: `kpi_definitions` (10 seeded con unit: COP, %, units), `kpi_results`
- **LLM outputs**: `insights`, `reports` (incluye `html_content` para render directo)
- **Control**: `etl_control`

## Config (`.env`)

```env
sqlserver_host=
sqlserver_port=1433
sqlserver_database=
sqlserver_user=
sqlserver_password=
gemini_api_key=
```

## API endpoints

| Método | Ruta                     | Descripción                                    |
| ------ | ------------------------ | ---------------------------------------------- |
| POST   | `/api/etl/run`           | Enqueue ETL                                    |
| POST   | `/api/etl/run-full`      | Enqueue pipeline completo                      |
| GET    | `/api/kpis`              | Últimos KPIs calculados                        |
| GET    | `/api/kpis/definitions`  | Definiciones de KPIs                           |
| GET    | `/api/insights`          | Insights generados                             |
| POST   | `/api/insights/generate` | Enqueue generación de insights                 |
| GET    | `/api/reports`           | Listar reportes                                |
| GET    | `/api/reports/{id}`      | Reporte por ID (JSON + html_content)           |
| GET    | `/api/reports/{id}/html` | Reporte renderizado como página HTML completa  |
| POST   | `/api/reports/generate`  | Enqueue generación de reporte                  |
| GET    | `/dashboard`             | Dashboard visual con Chart.js (auto-refresh)   |
| GET    | `/api/dashboard/data`    | JSON con KPIs, tendencias, top productos, etc. |

## Dashboard

- Jinja2 + Chart.js, auto-refresh cada 30s
- Tarjetas dinámicas según `kpi_definitions.unit` (COP → $, % → %, units → número)
- Gráfico de tendencia con todos los KPIs que tengan datos
- Botones para trigger manual de ETL, insights y reporte
- Link al último reporte HTML generado

## Key decisions

- `Jinja2Templates` reemplazado por `jinja2.Environment` + `FileSystemLoader` para evitar `TypeError: unhashable type: 'dict'` de Starlette
- Dashboard usa Chart.js cliente (fetch + setInterval), sin SSE/WebSocket
- Reportes se generan como HTML directo por Gemini (estilos inline), servidos en `/reports/{id}/html`

## SQL Server test data

`db/sqlserver/init.sql` genera 10 productos, 8 tiendas, 90 días de ventas aleatorias con `RAND()` en WHILE loop. Cada `docker compose down -v` + `up` regenera datos frescos.

## Known issues

- `demo/` referenced in old docker-compose no existe (ya removido)
- Tests directory empty
- Dashboard path resolution: `Path(__file__).resolve().parents[4] / "templates"`
