# Autometrics Engine

Automated retail analytics pipeline. Extracts data from SQL Server into a PostgreSQL Data Warehouse, calculates KPIs, and generates executive insights and reports using Gemini.

## Stack

- **FastAPI** + **asyncpg** — REST API
- **arq** + **Redis** — Worker and task queue
- **PostgreSQL 17** — Data Warehouse (star schema)
- **SQL Server** — Source database (retail)
- **Gemini (LLM)** — Insight and report generation
- **Chart.js** — Interactive dashboard
- **Docker Compose** — Full orchestration
- **Python ≥3.13 + Poetry ≥2.0**

## Prerequisites

- Docker + Docker Compose
- Copy `.env.example` → `.env` and fill in the variables
- Gemini API key (free at Google AI Studio)

## Usage with Docker

```bash
# Clone and start
git clone <repo>
cd autometrics-engine
cp .env.example .env
# Edit .env with your credentials (gemini_api_key is required)

# Build and launch everything
docker compose up --build

# Detached mode (background)
docker compose up --build -d
```

This starts 5 services:

| Service     | Port | Role                                |
| ----------- | ---- | ----------------------------------- |
| `app`       | 8000 | REST API + Dashboard                |
| `worker`    | —    | arq worker (ETL, insights, reports) |
| `db`        | 5432 | PostgreSQL (Data Warehouse)         |
| `redis`     | 6379 | Task queue                          |
| `sqlserver` | 1433 | Source database (test data)         |

## Automatic schedule

| Time    | Days   | What                               |
| ------- | ------ | ---------------------------------- |
| 6:00 AM | Daily  | ETL: SQL Server → Warehouse + KPIs |
| 6:30 AM | Sunday | Weekly insights via Gemini         |
| 7:00 AM | Sunday | Executive HTML report              |

Each step can also be triggered manually from the dashboard or API.

## Dashboard

Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

- Dynamic KPI cards formatted by type (COP, %, units)
- 30-day trend chart
- Top 5 products and stores
- AI-generated insights
- Buttons to trigger ETL, insights, and reports
- Link to the latest HTML report
- Auto-refresh every 30 seconds

## API

| Method | Endpoint                 | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| POST   | `/api/etl/run`           | Run ETL                                 |
| POST   | `/api/etl/run-full`      | Full pipeline (ETL + insights + report) |
| GET    | `/api/kpis`              | Latest KPIs                             |
| GET    | `/api/kpis/definitions`  | KPI definitions                         |
| GET    | `/api/insights`          | Generated insights                      |
| POST   | `/api/insights/generate` | Generate insights                       |
| GET    | `/api/reports`           | List reports                            |
| GET    | `/api/reports/{id}`      | Report by ID (JSON)                     |
| GET    | `/api/reports/{id}/html` | Report as full HTML page                |
| POST   | `/api/reports/generate`  | Generate report                         |

## Useful commands

```bash
# View logs from all services
docker compose logs -f

# View logs from a specific service
docker compose logs -f worker

# Reset databases (fresh test data)
docker compose down -v && docker compose up --build

# Run worker manually (debugging)
docker compose run --rm worker

# Stop everything
docker compose down
```

## Environment variables (`.env`)

```text
gemini_api_key=                  # Required
gemini_model=gemini-2.0-flash    # Gemini model
sqlserver_host=sqlserver         # Docker service name
sqlserver_port=1433
sqlserver_database=RetailDB
sqlserver_user=sa
sqlserver_sa_password=TuPass123!
sqlserver_password=TuPass123!
postgres_user=autometrics
postgres_password=autometrics
postgres_db=autometrics
redis_url=redis://redis:6379/0
```

## Project structure

```text
├── docker-compose.yml
├── Dockerfile
├── db/
│   ├── Dockerfile
│   ├── init.sql               # Schema + seeds + test data
│   └── sqlserver/
│       ├── Dockerfile
│       ├── entrypoint.sh
│       └── init.sql            # SQL Server test data
├── src/
│   └── autometrics_engine/
│       ├── main.py             # FastAPI app + lifespan
│       ├── api/
│       │   ├── dependencies.py # Dependency wiring
│       │   └── routers/        # etl, kpis, insights, reports, dashboard
│       ├── application/
│       │   └── use_cases/      # run_etl, generate_insights, generate_report
│       ├── domain/
│       │   ├── entities/       # Product, Store, Sale, KpiResult, etc.
│       │   ├── repositories/   # ABCs
│       │   └── services/       # LLMProvider ABC
│       └── infrastructure/
│           ├── constants.py    # Gemini prompts
│           ├── settings.py     # pydantic-settings
│           ├── data/
│           │   └── repositories/  # Postgres*Repo, PymssqlExtractor
│           ├── services/
│           │   └── gemini_provider.py
│           └── worker/
│               ├── functions.py   # async worker functions
│               └── settings.py    # arq WorkerSettings + cron jobs
└── templates/
    └── dashboard.html              # Jinja2 + Chart.js
```

## License

MIT
