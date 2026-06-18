from datetime import date, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from autometrics_engine.api.dependencies import get_database

router = APIRouter(tags=["dashboard"])

_tpl_dir = str(Path(__file__).resolve().parents[4] / "templates")
_jinja_env = Environment(loader=FileSystemLoader(_tpl_dir))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    template = _jinja_env.get_template("dashboard.html")
    return HTMLResponse(template.render())


@router.get("/api/dashboard/data")
async def dashboard_data(db=Depends(get_database)):
    today = date.today()
    month_ago = today - timedelta(days=30)
    week_ago = today - timedelta(days=7)

    kpi_defs = await db.fetch(
        "SELECT name, unit, description FROM kpi_definitions ORDER BY id"
    )

    latest = await db.fetch("""
        SELECT DISTINCT ON (k.name) k.name, kr.value, kr.change_pct
        FROM kpi_results kr
        JOIN kpi_definitions k ON k.id = kr.kpi_id
        WHERE kr.date_id >= $1
        ORDER BY k.name, kr.date_id DESC
    """, week_ago)
    latest_map = {r["name"]: {"value": float(r["value"]), "change": float(r["change_pct"]) if r["change_pct"] else None} for r in latest}

    trends_raw = await db.fetch("""
        SELECT k.name, kr.date_id, kr.value
        FROM kpi_results kr
        JOIN kpi_definitions k ON k.id = kr.kpi_id
        WHERE kr.date_id >= $1
        ORDER BY kr.date_id, k.name
    """, month_ago)
    trends = {}
    for r in trends_raw:
        name = r["name"]
        if name not in trends:
            trends[name] = []
        trends[name].append({"date": str(r["date_id"]), "value": float(r["value"])})

    top_products = await db.fetch("""
        SELECT p.name, SUM(f.units_sold) as total
        FROM fact_sales f
        JOIN dim_product p ON p.id = f.product_id
        WHERE f.date_id >= $1
        GROUP BY p.name
        ORDER BY total DESC
        LIMIT 5
    """, month_ago)

    top_stores = await db.fetch("""
        SELECT s.name, SUM(f.revenue) as total
        FROM fact_sales f
        JOIN dim_store s ON s.id = f.store_id
        WHERE f.date_id >= $1
        GROUP BY s.name
        ORDER BY total DESC
        LIMIT 5
    """, month_ago)

    insights = await db.fetch("""
        SELECT title, summary, category, severity, generated_at
        FROM insights
        WHERE date_id >= $1
        ORDER BY generated_at DESC
        LIMIT 5
    """, week_ago)

    last_report = await db.fetch(
        "SELECT id, title, created_at FROM reports ORDER BY created_at DESC LIMIT 1"
    )

    return {
        "kpi_definitions": [dict(r) for r in kpi_defs],
        "latest": latest_map,
        "trends": trends,
        "top_products": [{"name": r["name"], "total": float(r["total"])} for r in top_products],
        "top_stores": [{"name": r["name"], "total": float(r["total"])} for r in top_stores],
        "insights": [dict(r) for r in insights],
        "last_report": dict(last_report[0]) if last_report else None,
    }
