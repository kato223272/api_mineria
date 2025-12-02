from fastapi import APIRouter
from src.domain.models import ReporteDocument
from collections import Counter

router = APIRouter(prefix="/analytics", tags=["Estadísticas"])

@router.get("/dashboard")
async def obtener_datos_dashboard():
    reportes = await ReporteDocument.find_all().to_list()
    
    if not reportes:
        return {
            "total_reportes": 0,
            "mapa_municipios": [],
            "genero_stats": [],
            "edad_peso_stats": [],
            "tendencia_diaria": []
        }

    mapa_data = {}
    generos = {"M": 0, "F": 0} 
    bio_stats = {}
    timeline = {}
    
    # --- BUCLE PRINCIPAL (Todo esto debe ir identado) ---
    for r in reportes:
        # 1. Mapa
        muni = r.municipio if r.municipio else "Desconocido"
        diag = r.diagnostico_final.split(" / ")[0] 
        
        if muni not in mapa_data: mapa_data[muni] = {}
        if diag not in mapa_data[muni]: mapa_data[muni][diag] = 0
        mapa_data[muni][diag] += 1

        # 2. Género
        g = r.genero.upper() if r.genero and r.genero.upper() in ["M", "F"] else "M"
        generos[g] += 1
        
        # 3. Bio Stats 
        if diag not in bio_stats: bio_stats[diag] = {"edad": [], "peso": []}
        if r.edad: bio_stats[diag]["edad"].append(r.edad)
        if r.peso: bio_stats[diag]["peso"].append(r.peso)
        
        if r.fecha:
            fecha_str = r.fecha.strftime("%Y-%m-%d")
            timeline[fecha_str] = timeline.get(fecha_str, 0) + 1

    # --- FORMATEO DE RESPUESTA ---

    # A. Mapa
    mapa_final = []
    for muni, enfermedades in mapa_data.items():
        total_muni = sum(enfermedades.values())
        top_enf = max(enfermedades, key=enfermedades.get)
        mapa_final.append({
            "municipio": muni,
            "total": total_muni,
            "predominante": top_enf,
            "detalle": enfermedades
        })

    # B. Género
    genero_final = [
        {"name": "Hombres", "value": generos["M"]},
        {"name": "Mujeres", "value": generos["F"]}
    ]

    # C. Bio (Promedios)
    bio_final = []
    for diag, values in bio_stats.items():
        if len(values["edad"]) > 0:
            prom_edad = sum(values["edad"]) / len(values["edad"])
            prom_peso = sum(values["peso"]) / len(values["peso"])
            bio_final.append({
                "enfermedad": diag.replace("Posible ", ""),
                "edad_promedio": round(prom_edad, 1),
                "peso_promedio": round(prom_peso, 1)
            })

    # D. Timeline
    timeline_final = [{"fecha": k, "casos": v} for k, v in sorted(timeline.items())]

    return {
        "total_reportes": len(reportes),
        "mapa_municipios": mapa_final,
        "genero_stats": genero_final,
        "edad_peso_stats": bio_final,
        "tendencia_diaria": timeline_final
    }