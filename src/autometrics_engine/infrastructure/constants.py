SYSTEM_PROMPT = """
Eres un asistente experto en análisis de datos de retail. Tus funciones:
- Analizar métricas de ventas, ingresos, márgenes y crecimiento
- Identificar tendencias, anomalías y oportunidades de negocio
- Generar insights accionables basados en datos históricos
- Redactar reportes ejecutivos claros y profesionales

Reglas:
- Responde siempre en español
- Basa tus análisis únicamente en los datos proporcionados
- Sé específico con números y porcentajes
- Prioriza insights accionables sobre observaciones genéricas
- Si falta información relevante, indícalo claramente
"""

INSIGHT_PROMPT = """
Analiza los siguientes KPIs de retail y genera insights accionables.

Datos del período {period_start} a {period_end}:

{metrics}

Genera un JSON con esta estructura:
{{
    "insights": [
        {{
            "title": "Título corto del insight",
            "summary": "Análisis detallado con datos específicos",
            "category": "trend | anomaly | opportunity | warning",
            "severity": "low | medium | high | critical"
        }}
    ]
}}
"""

REPORT_PROMPT = """
Genera un reporte ejecutivo de retail basado en los siguientes datos.
El reporte debe verse profesional, listo para presentar a la gerencia.

PERÍODO: {period_start} a {period_end}

KPIs PRINCIPALES:
{kpis}

INSIGHTS DETECTADOS:
{insights}

TOP PRODUCTOS:
{top_products}

TOP TIENDAS:
{top_stores}

Devuelve SOLO un JSON con dos campos: "title" (string), "html_content" (string con HTML INLINE con estilos CSS inline, profesional y listo para incrustar en una página), "executive_summary", "highlights", "concerns", "recommendations", y "sections" (misma estructura de antes).

Estructura exacta:
{{
    "title": "Reporte automático - {period_start} a {period_end}",
    "html_content": "<div style='font-family:system-ui,sans-serif;max-width:800px;margin:0 auto;padding:20px;color:#1e293b;'><h2 style='color:#0f172a;border-bottom:3px solid #3b82f6;padding-bottom:8px;'>Resumen Ejecutivo</h2><p>...</p>... todo el HTML con estilos inline aquí ...</div>",
    "executive_summary": "Resumen ejecutivo de 2-3 párrafos",
    "highlights": ["Logro clave 1", "Logro clave 2", "Logro clave 3"],
    "concerns": ["Riesgo 1", "Riesgo 2"],
    "recommendations": ["Recomendación 1", "Recomendación 2", "Recomendación 3"],
    "sections": [
        {{
            "title": "Nombre de sección",
            "content": "Contenido detallado de la sección",
            "metrics": {{ "kpi_name": valor }}
        }}
    ]
}}
"""
