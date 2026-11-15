"""Configuración leída del entorno (nunca valores fijos en el código)."""
import logging
import os

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("config")


def _si(nombre: str) -> bool:
    return (os.environ.get(nombre) or "").strip().lower() in ("1", "true", "si", "sí", "yes", "on")


AGENT_ID = "agente-ale-ubi"
# Modo económico: Haiku y topes más bajos (útil para desarrollar y probar sin gastar de más).
ECONOMICO = _si("ECONOMICO")
MODELO_BARATO = "claude-haiku-5-5"
MODELO = MODELO_BARATO if ECONOMICO else (os.environ.get("MODELO") or "claude-sonnet-5-5")
# Topes de longitud de respuesta (una respuesta cortada se avisa) y ventana de historial enviada al modelo.
MAX_TOKENS = int(os.environ.get("MAX_TOKENS") or (1500 if ECONOMICO else 2500))
HISTORIAL_MAX_MENSAJES = int(os.environ.get("HISTORIAL_MAX_MENSAJES") or (12 if ECONOMICO else 24))
PROMPT_CACHE = (os.environ.get("PROMPT_CACHE") or "1").strip().lower() not in ("0", "false", "no", "off")

# Claves válidas separadas por coma (permite rotar sin cortar el servicio). Sin clave => el servidor se niega a atender.
# La clave de ejemplo de .env.example es pública (está en GitHub): si alguien la deja sin cambiar, NO se acepta como válida.
CLAVE_DE_EJEMPLO = "clave-ficticia-cambiar-por-una-larga-y-aleatoria"
_claves = [k.strip() for k in os.environ.get("API_KEYS", "").split(",") if k.strip()]
if CLAVE_DE_EJEMPLO in _claves:
    log.error("API_KEYS contiene la clave de ejemplo de .env.example: se ignora. Genere una propia (ver .env.example).")
API_KEYS = [k for k in _claves if k != CLAVE_DE_EJEMPLO]
# Dirección pública del servicio en la nube: la ficha (Agent Card) publica aquí dónde encontrar al agente.
# URL_PUBLICA es el nombre oficial; PUBLIC_URL se acepta por compatibilidad.
URL_PUBLICA = (os.environ.get("URL_PUBLICA") or os.environ.get("PUBLIC_URL") or "http://127.0.0.1:8000").rstrip("/")
PUBLIC_URL = URL_PUBLICA
# Control de costos: consultas por minuto y por clave en /chat (0 = sin límite).
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN") or "20")
