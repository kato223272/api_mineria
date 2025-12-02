from fastapi import APIRouter
from src.domain.schemas import PacienteInput, DiagnosticoOutput
from src.mining.service import realizar_diagnostico

router = APIRouter(prefix="/analisis", tags=["Minería"])

@router.post("/diagnosticar", response_model=DiagnosticoOutput)
async def diagnosticar(paciente: PacienteInput):
    return await realizar_diagnostico(paciente)