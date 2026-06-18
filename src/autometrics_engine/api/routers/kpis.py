from fastapi import APIRouter, Depends

from autometrics_engine.api.dependencies import get_database

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("")
async def list_kpis(db=Depends(get_database)):
    rows = await db.fetch("""
        SELECT kr.id, k.name, kr.date_id, kr.value, kr.previous_value, kr.change_pct
        FROM kpi_results kr
        JOIN kpi_definitions k ON k.id = kr.kpi_id
        ORDER BY kr.date_id DESC, k.name
        LIMIT 100
    """)
    return [dict(r) for r in rows]


@router.get("/definitions")
async def list_kpi_definitions(db=Depends(get_database)):
    rows = await db.fetch(
        "SELECT id, name, description, unit, frequency, higher_is_better "
        "FROM kpi_definitions ORDER BY id"
    )
    return [dict(r) for r in rows]
