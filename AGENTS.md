# autometrics-engine

## Package name

Package is `autometrics_engine` (source at `src/autometrics_engine/`). All imports, Dockerfile CMD, and docker-compose now use `autometrics_engine`.

## Entrypoint

```bash
poetry install                    # install deps (pyproject.toml only, no lockfile)
poetry run uvicorn autometrics_engine.main:app --reload
docker compose up --build         # full stack (db + redis + app + worker + frontend)
```

## Architecture

- **FastAPI** + Gemini (LLM), asyncpg, arq worker + Redis
- **Stack**: Python ≥3.13, Poetry ≥2.0
- **Source**: SQL Server (retail sales data)
- **Warehouse**: PostgreSQL 17 with star schema (`dim_product`, `dim_store`, `dim_date`, `fact_sales`)
- **Config**: pydantic-settings reads `.env` via `Settings` in `infrastructure/settings.py`
- **Dependencies**: wired in `api/dependencies.py` (LLM singleton, request-scoped repos + use cases, DB via `app.state.db`, Redis via `app.state.redis`)
- **Lifespan** (`main.py`): connects asyncpg pool + arq Redis pool on startup

## Pipeline (arq worker)

Worker functions in `infrastructure/worker/functions.py`:

| Function            | What it does                                             |
| ------------------- | -------------------------------------------------------- |
| `run_etl_pipeline`  | SQL Server → dim\_\* / fact_sales → calculate daily KPIs |
| `generate_insights` | Read KPI results → Gemini → `insights` table             |
| `generate_report`   | Read KPIs + insights → Gemini → `reports` table          |

Run via: `arq autometrics_engine.infrastructure.worker.settings.WorkerSettings`

## Pipeline flow

```text
SQL Server → run_etl_pipeline → Warehouse + KPIs → generate_insights → insights → generate_report → reports
```

## DB schema (`db/init.sql`)

- **Dimensions**: `dim_product`, `dim_store`, `dim_date` (seeded 2020-2030)
- **Facts**: `fact_sales`
- **KPIs**: `kpi_definitions` (10 seeded), `kpi_results`
- **LLM outputs**: `insights`, `reports`
- **Control**: `etl_control` (tracks incremental ETL state)

## SQL Server settings (required)

Add to `.env`:

```env
sqlserver_host=
sqlserver_port=1433
sqlserver_database=
sqlserver_user=
sqlserver_password=
```

## Known issues (must fix before running)

- Package imports were renamed from `travel_planner_co` to `autometrics_engine` (Jun 2026)

## API endpoints

| Método | Ruta                     | Descripción                                          |
| ------ | ------------------------ | ---------------------------------------------------- |
| POST   | `/api/etl/run`           | Enqueue ETL (SQL Server → Warehouse → KPIs)          |
| POST   | `/api/etl/run-full`      | Enqueue pipeline completo (ETL + insights + reporte) |
| GET    | `/api/kpis`              | Listar últimos KPIs calculados                       |
| GET    | `/api/kpis/definitions`  | Listar definiciones de KPIs                          |
| GET    | `/api/insights`          | Listar insights generados                            |
| POST   | `/api/insights/generate` | Enqueue generación de insights                       |
| GET    | `/api/reports`           | Listar reportes                                      |
| GET    | `/api/reports/{id}`      | Obtener reporte por ID                               |
| POST   | `/api/reports/generate`  | Enqueue generación de reporte                        |

- `demo/` referenced in `docker-compose.yml` (frontend) does not exist
- Tests directory is empty, no test framework configured beyond `pytest` in dev deps
