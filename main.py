import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.database import iniciar_db
from src.api.main_router import api_router
from src.mining.engine import kb_engine

app = FastAPI(title="SaludXChiapas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await iniciar_db()
    await kb_engine.cargar_conocimiento()
    print("Sistema SaludXChiapas: ONLINE")

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)