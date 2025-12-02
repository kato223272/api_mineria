from rapidfuzz import process, fuzz, utils
from src.domain.models import EnfermedadDocument

class RAGEngine:
    def __init__(self):
        self.base_conocimiento = {}

    async def cargar_conocimiento(self):
        enfermedades = await EnfermedadDocument.find_all().to_list()
        self.base_conocimiento = {}
        for enf in enfermedades:
            for sint in enf.sintomatologia:
                formal = sint.nombre
                self.base_conocimiento[formal.lower()] = formal
                for var in sint.otros_nombres:
                    self.base_conocimiento[var.lower()] = formal

    async def extraer_sintomas(self, texto: str) -> list:
        if not self.base_conocimiento:
            await self.cargar_conocimiento()
        
        detectados = set()
        texto_proc = utils.default_process(texto)
        claves = list(self.base_conocimiento.keys())

        matches = process.extract(
            texto_proc, claves, scorer=fuzz.token_set_ratio, score_cutoff=85, limit=10
        )

        for match in matches:
            termino = match[0]
            formal = self.base_conocimiento[termino]
            detectados.add(formal)
            
        return list(detectados)

kb_engine = RAGEngine()