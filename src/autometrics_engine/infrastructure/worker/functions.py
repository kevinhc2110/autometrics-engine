from autometrics_engine.infrastructure.settings import settings
from autometrics_engine.infrastructure.data.postgres import PostgresDatabase
from autometrics_engine.infrastructure.services.gemini_provider import GeminiProvider

from autometrics_engine.infrastructure.data.repositories.postgres_product_repository import PostgresProductRepository
from autometrics_engine.infrastructure.data.repositories.postgres_store_repository import PostgresStoreRepository
from autometrics_engine.infrastructure.data.repositories.postgres_sale_repository import PostgresSaleRepository
from autometrics_engine.infrastructure.data.repositories.postgres_kpi_repository import PostgresKpiRepository
from autometrics_engine.infrastructure.data.repositories.postgres_insight_repository import PostgresInsightRepository
from autometrics_engine.infrastructure.data.repositories.postgres_report_repository import PostgresReportRepository

from autometrics_engine.application.use_cases.run_etl import RunEtlUseCase
from autometrics_engine.application.use_cases.generate_insights import GenerateInsightsUseCase
from autometrics_engine.application.use_cases.generate_report import GenerateReportUseCase

from autometrics_engine.infrastructure.data.repositories.pymssql_extractor import PymssqlExtractor

POSTGRES_DSN = settings.postgres_dsn


async def startup(ctx):
    db = PostgresDatabase(dsn=POSTGRES_DSN)
    await db.connect()
    ctx['db'] = db


async def shutdown(ctx):
    db = ctx.get('db')
    if db:
        await db.disconnect()


async def _build_use_cases(db):
    product_repo = PostgresProductRepository(db)
    store_repo = PostgresStoreRepository(db)
    sale_repo = PostgresSaleRepository(db)
    kpi_repo = PostgresKpiRepository(db)
    insight_repo = PostgresInsightRepository(db)
    report_repo = PostgresReportRepository(db)

    source = PymssqlExtractor(
        host=settings.sqlserver_host,
        port=settings.sqlserver_port,
        database=settings.sqlserver_database,
        user=settings.sqlserver_user,
        password=settings.sqlserver_password,
    )

    llm = GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)

    etl = RunEtlUseCase(
        product_repo=product_repo,
        store_repo=store_repo,
        sale_repo=sale_repo,
        kpi_repo=kpi_repo,
        source=source,
    )
    insights = GenerateInsightsUseCase(
        kpi_repo=kpi_repo,
        insight_repo=insight_repo,
        llm=llm,
    )
    report = GenerateReportUseCase(
        kpi_repo=kpi_repo,
        insight_repo=insight_repo,
        report_repo=report_repo,
        product_repo=product_repo,
        store_repo=store_repo,
        sale_repo=sale_repo,
        llm=llm,
    )
    return etl, insights, report


async def run_etl_pipeline(ctx):
    etl, _, _ = await _build_use_cases(ctx['db'])
    await etl.execute()


async def generate_insights(ctx):
    _, insights, _ = await _build_use_cases(ctx['db'])
    await insights.execute()


async def generate_report(ctx):
    _, _, report = await _build_use_cases(ctx['db'])
    await report.execute()
