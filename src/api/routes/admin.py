from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.domain.models import EnfermedadDocument, Sintoma
from src.mining.engine import kb_engine

router = APIRouter(prefix="/admin", tags=["Administración Total"])
# GESTIÓN DE ENFERMEDADES (CRUD)
# CREAR ENFERMEDAD
@router.post("/enfermedad")
async def crear_enfermedad(enfermedad: EnfermedadDocument):
    existe = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == enfermedad.nombre)
    if existe: raise HTTPException(400, f"La enfermedad '{enfermedad.nombre}' ya existe.")
    
    await enfermedad.insert()
    await kb_engine.cargar_conocimiento() # Recargar IA
    return {"msg": f"Enfermedad '{enfermedad.nombre}' creada."}

#ELIMINAR ENFERMEDAD
@router.delete("/enfermedad")
async def borrar_enfermedad(nombre: str):
    enf = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == nombre)
    if not enf: raise HTTPException(404, "Enfermedad no encontrada.")
    
    await enf.delete()
    await kb_engine.cargar_conocimiento()
    return {"msg": f"Enfermedad '{nombre}' eliminada."}

#EDITAR ENFERMEDAD (Nombre, Urgencia, Recomendación)
class EdicionEnfermedadInput(BaseModel):
    nombre_actual: str
    nuevo_nombre: str | None = None
    nueva_urgencia: str | None = None
    nueva_recomendacion: str | None = None

@router.put("/enfermedad")
async def editar_enfermedad(data: EdicionEnfermedadInput):
    enf = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == data.nombre_actual)
    if not enf: raise HTTPException(404, "Enfermedad no encontrada.")

    # Si cambia el nombre, verificamos que no exista ya el nuevo
    if data.nuevo_nombre and data.nuevo_nombre != data.nombre_actual:
        if await EnfermedadDocument.find_one(EnfermedadDocument.nombre == data.nuevo_nombre):
             raise HTTPException(400, "Ya existe otra enfermedad con ese nuevo nombre.")
        enf.nombre = data.nuevo_nombre

    if data.nueva_urgencia: enf.nivel_urgencia = data.nueva_urgencia
    if data.nueva_recomendacion: enf.recomendacion_publica = data.nueva_recomendacion

    await enf.save()
    await kb_engine.cargar_conocimiento()
    return {"msg": "Datos de la enfermedad actualizados."}

#  GESTIÓN DE SÍNTOMAS (CRUD)

class GestionSintomaInput(BaseModel):
    enfermedad_nombre: str
    sintoma_objetivo: str # El nombre del síntoma a buscar

# AGREGAR NUEVO SÍNTOMA (Un bloque entero nuevo)
class NuevoSintomaFull(BaseModel):
    enfermedad_nombre: str
    nuevo_sintoma: Sintoma 

@router.post("/sintoma")
async def agregar_sintoma_completo(data: NuevoSintomaFull):
    enf = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == data.enfermedad_nombre)
    if not enf: raise HTTPException(404, "Enfermedad no encontrada.")

    # Verificar si ya existe ese síntoma
    for s in enf.sintomatologia:
        if s.nombre == data.nuevo_sintoma.nombre:
            raise HTTPException(400, "Ese síntoma ya existe en esta enfermedad.")

    enf.sintomatologia.append(data.nuevo_sintoma)
    await enf.save()
    await kb_engine.cargar_conocimiento()
    return {"msg": f"Síntoma '{data.nuevo_sintoma.nombre}' agregado a {data.enfermedad_nombre}."}

# ELIMINAR SÍNTOMA
@router.delete("/sintoma")
async def eliminar_sintoma_completo(enfermedad: str, sintoma: str):
    enf = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == enfermedad)
    if not enf: raise HTTPException(404, "Enfermedad no encontrada.")

    # Filtramos la lista para quitar el síntoma
    longitud_antes = len(enf.sintomatologia)
    enf.sintomatologia = [s for s in enf.sintomatologia if s.nombre != sintoma]
    
    if len(enf.sintomatologia) == longitud_antes:
        raise HTTPException(404, "El síntoma no existía en la lista.")

    await enf.save()
    await kb_engine.cargar_conocimiento()
    return {"msg": f"Síntoma '{sintoma}' eliminado de {enfermedad}."}

# EDITAR SÍNTOMA (Renombrar o Editar Sinónimos en bloque)
class EdicionSintomaInput(BaseModel):
    enfermedad_nombre: str
    sintoma_actual: str
    nuevo_nombre: str | None = None
    nuevos_sinonimos: list[str] | None = None

@router.put("/sintoma")
async def editar_sintoma(data: EdicionSintomaInput):
    enf = await EnfermedadDocument.find_one(EnfermedadDocument.nombre == data.enfermedad_nombre)
    if not enf: raise HTTPException(404, "Enfermedad no encontrada.")

    encontrado = False
    for s in enf.sintomatologia:
        if s.nombre == data.sintoma_actual:
            if data.nuevo_nombre: s.nombre = data.nuevo_nombre
            if data.nuevos_sinonimos is not None: s.otros_nombres = data.nuevos_sinonimos
            encontrado = True
            break
    
    if not encontrado: raise HTTPException(404, "Síntoma no encontrado.")

    await enf.save()
    await kb_engine.cargar_conocimiento()
    return {"msg": "Síntoma actualizado correctamente."}

@router.post("/seed")
async def seed():
    return {"msg": "Usa la función de Crear Enfermedad para insertar datos manuales o carga los JSON en Mongo Atlas."}

@router.get("/catalogo-sintomas")
async def obtener_catalogo_sintomas():
    enfermedades = await EnfermedadDocument.find_all().to_list()
    return enfermedades