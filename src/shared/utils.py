import re
import unicodedata
from datetime import datetime
from rapidfuzz import utils

def limpiar_texto(texto: str) -> str:
    return utils.default_process(texto)

def normalizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""

    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                    if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    
    return re.sub(r'\s+', ' ', texto).strip()

def obtener_fecha_iso() -> str:
    """Retorna la fecha actual en formato ISO string"""
    return datetime.now().isoformat()