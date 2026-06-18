from arq.connections import RedisSettings
from arq.cron import cron

from autometrics_engine.infrastructure.settings import settings
from autometrics_engine.infrastructure.worker.functions import (
    run_etl_pipeline,
    generate_insights,
    generate_report,
)


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [run_etl_pipeline, generate_insights, generate_report]
    cron_jobs = [
        cron(run_etl_pipeline, hour=6, minute=0),
        cron(generate_insights, weekday="sun", hour=6, minute=30),
        cron(generate_report, weekday="sun", hour=7, minute=0),
    ]
    poll_delay = 0.5
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
    keep_result_failed = 3600
