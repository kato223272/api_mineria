from src.mining.engine import kb_engine
from src.domain.schemas import PacienteInput, DiagnosticoOutput
from src.domain.models import EnfermedadDocument, ReporteDocument
from datetime import datetime

async def realizar_diagnostico(paciente: PacienteInput) -> DiagnosticoOutput:
    sintomas = await kb_engine.extraer_sintomas(paciente.texto_sintomas)

    # CASO A: El usuario no puso nada válido
    if not sintomas:
        return await _guardar_reporte_real(
            paciente,
            diagnostico="No Concluyente / Sin Síntomas Claros",
            confianza=0.0,
            urgencia="Bajo",
            recomendacion="No pudimos detectar síntomas médicos conocidos. Por favor acuda a un médico para valoración.",
            sintomas_detectados=[]
        )
    # CASO B: TIENE EXACTAMENTE 1 SÍNTOMA

    if len(sintomas) == 1:
        doc_malestar = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == "Malestares Generales")
        
        if doc_malestar:
            diag_titulo = "Síntoma Aislado / Malestar General"
            rec_texto = doc_malestar.recomendacion_publica
            urg_nivel = doc_malestar.nivel_urgencia
        else:
            diag_titulo = "Síntoma Aislado"
            rec_texto = "Se detectó un síntoma aislado. Acuda a su médico."
            urg_nivel = "Bajo"

        return await _guardar_reporte_real(
            paciente,
            diagnostico=diag_titulo,
            confianza=85.0, 
            urgencia=urg_nivel,
            recomendacion=rec_texto,
            sintomas_detectados=sintomas
        )
    # CASO C: TIENE MÁS DE 1 SÍNTOMA

    enfermedades = await EnfermedadDocument.find_all().to_list()
    mejor_match = None
    mejor_score = 0.0

    for enf in enfermedades:
        if enf.nombre == "Malestares Generales": 
            continue

        # logica de coincidencia:
        db_set = {s.nombre for s in enf.sintomatologia}
        user_set = set(sintomas)
        
        # sintomas que coinciden
        coincidencias = user_set & db_set
        if not coincidencias: continue
        
        # que porcentaje de lo que dijo el usuario encaja con esta enfermedad
        score = (len(coincidencias) / len(user_set)) * 100
        for clave in enf.sintomas_clave:
            if clave in sintomas:
                score += 15 
        if score > 95.0: score = 95.0

        # Nos quedamos con la enfermedad que tenga el score más alto
        if score > mejor_score:
            mejor_score = score
            mejor_match = enf

    if mejor_match and mejor_score > 30:
        return await _guardar_reporte_real(
            paciente,
            diagnostico=f"Posible {mejor_match.nombre}",
            confianza=round(mejor_score, 2),
            urgencia=mejor_match.nivel_urgencia,
            recomendacion=mejor_match.recomendacion_publica,
            sintomas_detectados=list(set(sintomas) & {s.nombre for s in mejor_match.sintomatologia})
        )

    # CASO D: Tiene varios síntomas, pero no coinciden bien con ninguna enfermedad grave.
    
    return await _guardar_reporte_real(
        paciente, 
        diagnostico="Síntomas Inespecíficos / Requiere Valoración", 
        confianza=15.0, 
        urgencia="Bajo", 
        recomendacion="Presenta múltiples síntomas que no coinciden con un patrón viral específico (Dengue/Zika). Es necesario acudir al médico para estudios de laboratorio.", 
        sintomas_detectados=sintomas
    )

async def _guardar_reporte_real(p: PacienteInput, diagnostico: str, confianza: float, urgencia: str, recomendacion: str, sintomas_detectados: list):
    nuevo_reporte = ReporteDocument(
        fecha=datetime.now(),
        municipio=p.municipio, 
        genero=p.genero,       
        edad=p.edad,           
        peso=p.peso,           
        diagnostico_final=diagnostico,
        sintomas_detectados=sintomas_detectados,
        nivel_urgencia=urgencia
    )
    await nuevo_reporte.insert()
    return DiagnosticoOutput(
        diagnostico=diagnostico,
        confianza=confianza,
        nivel_urgencia=urgencia,
        recomendacion=recomendacion,
        sintomas_detectados=sintomas_detectados
    )