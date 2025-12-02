from pydantic import BaseModel
from typing import List, Optional

class PacienteInput(BaseModel):
    texto_sintomas: str
    municipio: str
    genero: str  
    edad: int
    peso: Optional[float] = None

class DiagnosticoOutput(BaseModel):
    diagnostico: str
    confianza: float
    nivel_urgencia: str
    recomendacion: str
    sintomas_detectados: List[str]

class NuevoSinonimoInput(BaseModel):
    enfermedad_nombre: str
    sintoma_nombre: str
    nuevo_sinonimo: str