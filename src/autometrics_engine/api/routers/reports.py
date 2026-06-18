from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

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
        "SELECT id, title, period_start, period_end, summary, content, html_content, status, created_at "
        "FROM reports WHERE id = $1", report_id
    )
    if not rows:
        return {"error": "Report not found"}, 404
    return dict(rows[0])


@router.get("/{report_id}/html", response_class=HTMLResponse)
async def get_report_html(report_id: str, db=Depends(get_database)):
    rows = await db.fetch(
        "SELECT title, html_content FROM reports WHERE id = $1", report_id
    )
    if not rows or not rows[0]["html_content"]:
        return HTMLResponse("<h1>Reporte no encontrado</h1>", status_code=404)
    r = rows[0]
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{r['title']} - Autometrics</title>
<style>body {{ font-family:system-ui,sans-serif; background:#f1f5f9; margin:0; padding:24px; }}
a {{ color:#3b82f6; text-decoration:none; }}</style>
</head>
<body>
<div style="max-width:900px;margin:0 auto;">
<a href="/dashboard" style="display:inline-block;margin-bottom:16px;font-size:.85rem;">&larr; Volver al Dashboard</a>
{r['html_content']}
</div>
</body>
</html>""")


@router.post("/generate", status_code=202)
async def generate_report(redis=Depends(get_redis_pool)):
    await redis.enqueue_job("generate_report")
    return {"message": "Report generation job enqueued"}
