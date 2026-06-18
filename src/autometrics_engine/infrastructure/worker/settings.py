from arq.connections import RedisSettings

from autometrics_engine.infrastructure.settings import settings
from autometrics_engine.infrastructure.worker.functions import (
    run_etl_pipeline,
    generate_insights,
    generate_report,
)


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [run_etl_pipeline, generate_insights, generate_report]
    poll_delay = 0.5
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
    keep_result_failed = 3600
