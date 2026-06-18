from fastapi import APIRouter, Depends

from autometrics_engine.api.dependencies import get_redis_pool, get_database

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
async def list_reports(db=Depends(get_database)):
    rows = await db.fetch(
        "SELECT id, title, period_start, period_end, summary, status, created_at "
        "FROM reports ORDER BY created_at DESC LIMIT 20"
    )
    return [dict(r) for r in rows]


@router.get("/{report_id}")
async def get_report(report_id: str, db=Depends(get_database)):
    rows = await db.fetch(
        "SELECT id, title, period_start, period_end, summary, content, status, created_at "
        "FROM reports WHERE id = $1", report_id
    )
    if not rows:
        return {"error": "Report not found"}, 404
    return dict(rows[0])


@router.post("/generate", status_code=202)
async def generate_report(redis=Depends(get_redis_pool)):
    await redis.enqueue_job("generate_report")
    return {"message": "Report generation job enqueued"}
