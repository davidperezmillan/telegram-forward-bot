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
TARGET_CHAT_EXCLUSIVO_ID = os.getenv("TARGET_CHAT_EXCLUSIVO_ID")
CHATS_EXCLUIDOS= os.getenv("CHATS_EXCLUIDOS", "9999").split(";") if os.getenv("CHATS_EXCLUIDOS") else ["0000"]
DEFAULT_FORWARD_MODE = os.getenv("FORWARD_MODE", "auto").lower()
FORWARD_MODE = DEFAULT_FORWARD_MODE

# Cache para medios
MEDIA_CACHE = {}