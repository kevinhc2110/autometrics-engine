from fastapi import APIRouter, Depends

from autometrics_engine.api.dependencies import get_redis_pool

router = APIRouter(prefix="/api/etl", tags=["etl"])


@router.post("/run", status_code=202)
async def run_etl(redis=Depends(get_redis_pool)):
    await redis.enqueue_job("run_etl_pipeline")
    return {"message": "ETL job enqueued"}


@router.post("/run-full", status_code=202)
async def run_full_pipeline(redis=Depends(get_redis_pool)):
    await redis.enqueue_job("run_etl_pipeline")
    await redis.enqueue_job("generate_insights")
    await redis.enqueue_job("generate_report")
    return {"message": "Full pipeline job enqueued"}
