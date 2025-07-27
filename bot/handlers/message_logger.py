import os
from datetime import datetime

# Ruta del archivo de registro
LOG_FILE_PATH = "./logs/message_log.txt"

# Asegúrate de que la carpeta exista
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def log_message(action, message_data):
    """
    Registra un mensaje en el archivo de log.
    :param action: Acción realizada (e.g., "received", "forwarded").
    :param chat_id: ID del chat.
    :param message_id: ID del mensaje.
    :param media_type: Tipo de medio (opcional).
    :param file_id: ID del archivo (opcional).
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ACTION: {action}, "

    # Chat de origen
    if message_data.chat_origen:
        log_entry += f"CHAT_ORIGEN: {message_data.chat_origen}, "
    if message_data.chat_origen_title:
        log_entry += f"CHAT_ORIGEN_TITLE: {message_data.chat_origen_title}, "

    # ids de mensaje
    log_entry += f"CHAT_ID: {message_data.chat_id}, MESSAGE_ID: {message_data.message_id}, "

    # fichero
    if message_data.media_type:
        log_entry += f"MEDIA_TYPE: {message_data.media_type}, "
    if message_data.file_id:
        log_entry += f"FILE_ID: {message_data.file_id}, "

    # separación de registros
    log_entry += f"\n"
    
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(log_entry)


'''
    # Crear objeto MessageData
    message_data = MessageData(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        chat_origen=chat_origen,
        #media_type=media_type,
        #file_id=file_id,
    )
'''


class MessageData:
    def __init__(self, chat_id, message_id, media_type=None, file_id=None, chat_origen=None, chat_origen_title=None, file_size=None):
        self.chat_id = chat_id
        self.message_id = message_id
        self.media_type = media_type
        self.file_id = file_id
        self.chat_origen = chat_origen
        self.chat_origen_title = chat_origen_title
        self.file_size = file_size