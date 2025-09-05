import os
import json
import logging

# Cargar mensajes desde messages.json
with open('messages.json', encoding='utf-8') as f:
    MSG = json.load(f)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
TARGET_CHAT_ID_ME = os.getenv("TARGET_CHAT_ID_ME")
if not TARGET_CHAT_ID_ME:
    logger.error("Environment variable TARGET_CHAT_ID_ME is missing or empty.")
    raise ValueError("TARGET_CHAT_ID_ME must be set in the environment.")
DEFAULT_FORWARD_MODE = os.getenv("FORWARD_MODE", "auto").lower()
FORWARD_MODE = DEFAULT_FORWARD_MODE
# para barridos, recupear de las variables de entorno un string separado por comas y convertirlo en una lista
BARRIDOS = os.getenv("BARRIDOS", "").split(",")


# Cache para medios
MEDIA_CACHE = {}