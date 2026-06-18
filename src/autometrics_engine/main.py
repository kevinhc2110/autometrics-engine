from contextlib import asynccontextmanager

from arq.connections import RedisSettings, create_pool

from fastapi import FastAPI

from autometrics_engine.infrastructure.settings import settings
from autometrics_engine.infrastructure.data.postgres import PostgresDatabase

from autometrics_engine.api.routers.etl import router as etl_router
from autometrics_engine.api.routers.kpis import router as kpis_router
from autometrics_engine.api.routers.insights import router as insights_router
from autometrics_engine.api.routers.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()
    app.state.db = db

    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    app.state.redis = redis

    yield

    await redis.close()
    await db.disconnect()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(etl_router)
app.include_router(kpis_router)
app.include_router(insights_router)
app.include_router(reports_router)
