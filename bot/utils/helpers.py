from telegram.error import TelegramError
from config import logger

async def delete_original_message(chat_id, message_id, context):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Mensaje {message_id} borrado de {chat_id}")
    except TelegramError as e:
        logger.warning(f"No se pudo borrar el mensaje {message_id}: {e}")