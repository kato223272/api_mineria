from typing import List, Optional
from beanie import Document
from pydantic import BaseModel
from datetime import datetime

class Sintoma(BaseModel):
    nombre: str
    otros_nombres: List[str]

class EnfermedadDocument(Document):
    nombre: str
    nivel_urgencia: str
    recomendacion_publica: str
    sintomas_clave: List[str]
    sintomatologia: List[Sintoma]
    
    class Settings:
        name = "enfermedades"

class ReporteDocument(Document):
    """Historial para Analytics: Mapas de calor y tendencias"""
    fecha: datetime = datetime.now()
    municipio: str
    genero: str
    edad: int
    peso: Optional[float]
    diagnostico_final: str
    sintomas_detectados: List[str]
    nivel_urgencia: str
    
    class Settings:
        name = "reportes_epidemiologicos"