import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.domain.models import EnfermedadDocument, ReporteDocument

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

async def iniciar_db():
    if not MONGO_URL:
        print("No se encontro la variable MONGO_URL en el archivo .env")
        return

    client = AsyncIOMotorClient(MONGO_URL)
    
    await init_beanie(
        database=client.saludxchiapas_db,
        document_models=[
            EnfermedadDocument,
            ReporteDocument
        ]
    )