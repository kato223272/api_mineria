from fastapi import APIRouter
from src.domain.models import ReporteDocument
from collections import Counter

router = APIRouter(prefix="/analytics", tags=["Estadísticas"])

@router.get("/dashboard")
async def obtener_datos_dashboard():
    """Devuelve JSON procesado para gráficas"""
    reportes = await ReporteDocument.find_all().to_list()
    
    total = len(reportes)
    
    if total == 0:
        return {
            "total_reportes": 0,
            "mensaje": "No hay datos aún."
        }
    
    # Datos para Mapa de Calor (Municipio)
    municipios = dict(Counter([r.municipio for r in reportes]))
    # Datos para Tendencias (Pastel)
    diagnosticos = dict(Counter([r.diagnostico_final for r in reportes]))
    # Datos para Riesgo
    urgencias = dict(Counter([r.nivel_urgencia for r in reportes]))
    # Datos Demográficos
    generos = dict(Counter([r.genero for r in reportes]))
    
    # Top Síntomas
    all_sints = []
    for r in reportes: all_sints.extend(r.sintomas_detectados)
    top_sintomas = dict(Counter(all_sints).most_common(10))

    return {
        "total_reportes": total,
        "mapa_calor_municipios": municipios,
        "tendencias_enfermedad": diagnosticos,
        "niveles_riesgo": urgencias,
        "demografia": generos,
        "top_sintomas": top_sintomas
    }