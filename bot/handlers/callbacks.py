import os
from config import MEDIA_CACHE, logger
import aiohttp
from utils.forward import forward_media_to_target
from utils.helpers import delete_original_message
from telegram.error import TelegramError


# Ruta donde se guardarán los archivos
MEDIA_SAVE_PATH = "./media/"

# Asegúrate de que la carpeta exista
os.makedirs(MEDIA_SAVE_PATH, exist_ok=True)

async def button_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    action = data[0]

    if len(data) < 2:
        logger.warning("Callback recibido con datos insuficientes.")
        return

    short_id = data[1]
    entry = MEDIA_CACHE.get(short_id)

    if not entry:
        logger.warning(f"No se encontró cache para short_id {short_id}")
        return

    try:

        if action == "forward":
            await forward_media_to_target(context, entry["target_chat_id"], entry["media_type"], entry["file_id"])
            await delete_all_messages(context, query, entry)
        elif action == "save":
            msg_alt_id = await save_media_to_disk(context, entry["media_type"], entry["file_id"], entry["chat_id"])
            # Verificar si la clave "message_alt_id" existe, si no, inicializarla como una lista vacía
            entry.setdefault("message_alt_id", []).append(msg_alt_id)
            logger.info(f"Mensaje {entry} guardado en disco.")
        elif action == "discard":
            await delete_all_messages(context, query, entry)
            logger.info(f"Mensaje {entry['message_id']} descartado.")
        


    except Exception as e:
        logger.error(f"Error manejando callback del botón: {e}", exc_info=True)


    # MEDIA_CACHE.pop(short_id, None)

async def save_media_to_disk(context, media_type, file_id, chat_bot_id):
    file = None
    try:
        # Crear directorio si no existe
        if not os.path.exists(MEDIA_SAVE_PATH):
            os.makedirs(MEDIA_SAVE_PATH)

        logger.info(f"Iniciando descarga del archivo con file_id: {file_id} y tipo: {media_type}")
        file = await context.bot.get_file(file_id)
        logger.info(f"URL del archivo: {file.file_path}")
        logger.info(f"Guardando archivo en disco... tamaño: {file.file_size} bytes")

        # Determina la extensión del archivo
        file_extension = "jpg" if media_type == "photo" else "mp4" if media_type == "video" else "bin"
        file_path = os.path.join(MEDIA_SAVE_PATH, f"{file_id}.{file_extension}")

        # Descarga el archivo usando aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_path) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())
                    logger.info(f"Archivo guardado en disco: {file_path}")

                    # editar mensaje
                    msg_alt_id = await context.bot.send_message(
                        chat_id=chat_bot_id,    
                        text=f"✅ Archivo descargado correctamente"
                    )
                    return msg_alt_id.message_id
                else:
                    logger.error(f"Error al descargar el archivo: HTTP {response.status}")
    except TelegramError as e:
        # Manejo de errores específicos de Telegram
        msgError = f"Error de Telegram al obtener el archivo con file_id {file_id}: {e}"
        if file is not None:  # Check if file is defined
            msgError = f"El archivo con file_id {file_id} es demasiado grande para descargarlo. Tamaño: {file.file_size} bytes"
        logger.error(f"{msgError}", exc_info=False)

    except Exception as e:
        logger.error(f"Error al guardar el archivo en disco: {e}", exc_info=True)



async def delete_all_messages(context, query, entry):
    await delete_original_message(entry["chat_id"], entry["message_id"], context)
    if "message_alt_id" in entry:
        for msg_id in entry["message_alt_id"]:
            await delete_original_message(entry["chat_id"], msg_id, context)
    await delete_original_message(query.message.chat_id, query.message.message_id, context)