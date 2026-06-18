from fastapi import APIRouter, Depends

from autometrics_engine.api.dependencies import get_redis_pool, get_database

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("")
async def list_insights(db=Depends(get_database)):
    rows = await db.fetch(
        "SELECT id, title, summary, category, severity, generated_at "
        "FROM insights ORDER BY generated_at DESC LIMIT 50"
    )
    return [dict(r) for r in rows]


@router.post("/generate", status_code=202)
async def generate_insights(redis=Depends(get_redis_pool)):
    await redis.enqueue_job("generate_insights")
    return {"message": "Insight generation job enqueued"}
