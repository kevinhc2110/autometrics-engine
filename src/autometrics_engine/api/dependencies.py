from arq.connections import ArqRedis
from fastapi import Depends
from starlette.requests import HTTPConnection

from autometrics_engine.infrastructure.settings import settings
from autometrics_engine.infrastructure.services.gemini_provider import GeminiProvider

from autometrics_engine.application.use_cases.run_etl import RunEtlUseCase
from autometrics_engine.application.use_cases.generate_insights import GenerateInsightsUseCase
from autometrics_engine.application.use_cases.generate_report import GenerateReportUseCase

from autometrics_engine.infrastructure.data.repositories.postgres_product_repository import PostgresProductRepository
from autometrics_engine.infrastructure.data.repositories.postgres_store_repository import PostgresStoreRepository
from autometrics_engine.infrastructure.data.repositories.postgres_sale_repository import PostgresSaleRepository
from autometrics_engine.infrastructure.data.repositories.postgres_kpi_repository import PostgresKpiRepository
from autometrics_engine.infrastructure.data.repositories.postgres_insight_repository import PostgresInsightRepository
from autometrics_engine.infrastructure.data.repositories.postgres_report_repository import PostgresReportRepository
from autometrics_engine.infrastructure.data.repositories.pymssql_extractor import PymssqlExtractor


# --- LLM singleton ---

llm_provider = GeminiProvider(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)


def get_llm_provider():
    return llm_provider


# --- DB request-scoped ---

def get_database(request: HTTPConnection):
    return request.app.state.db


def get_redis_pool(request: HTTPConnection) -> ArqRedis:
    return request.app.state.redis


# --- Repositories (request-scoped, DB-based) ---

def get_product_repository(db=Depends(get_database)):
    return PostgresProductRepository(db)

def get_store_repository(db=Depends(get_database)):
    return PostgresStoreRepository(db)

def get_sale_repository(db=Depends(get_database)):
    return PostgresSaleRepository(db)

def get_kpi_repository(db=Depends(get_database)):
    return PostgresKpiRepository(db)

def get_insight_repository(db=Depends(get_database)):
    return PostgresInsightRepository(db)

def get_report_repository(db=Depends(get_database)):
    return PostgresReportRepository(db)


# --- Source extractor ---

def get_source_extractor():
    return PymssqlExtractor(
        host=settings.sqlserver_host,
        port=settings.sqlserver_port,
        database=settings.sqlserver_database,
        user=settings.sqlserver_user,
        password=settings.sqlserver_password,
    )


# --- Use Cases ---

def get_etl_use_case(
    product_repo=Depends(get_product_repository),
    store_repo=Depends(get_store_repository),
    sale_repo=Depends(get_sale_repository),
    kpi_repo=Depends(get_kpi_repository),
    source=Depends(get_source_extractor),
):
    return RunEtlUseCase(
        product_repo=product_repo,
        store_repo=store_repo,
        sale_repo=sale_repo,
        kpi_repo=kpi_repo,
        source=source,
    )

def get_insight_use_case(
    kpi_repo=Depends(get_kpi_repository),
    insight_repo=Depends(get_insight_repository),
    llm=Depends(get_llm_provider),
):
    return GenerateInsightsUseCase(
        kpi_repo=kpi_repo,
        insight_repo=insight_repo,
        llm=llm,
    )

def get_report_use_case(
    kpi_repo=Depends(get_kpi_repository),
    insight_repo=Depends(get_insight_repository),
    report_repo=Depends(get_report_repository),
    sale_repo=Depends(get_sale_repository),
    store_repo=Depends(get_store_repository),
    product_repo=Depends(get_product_repository),
    llm=Depends(get_llm_provider),
):
    return GenerateReportUseCase(
        kpi_repo=kpi_repo,
        insight_repo=insight_repo,
        report_repo=report_repo,
        product_repo=product_repo,
        store_repo=store_repo,
        sale_repo=sale_repo,
        llm=llm,
    )
