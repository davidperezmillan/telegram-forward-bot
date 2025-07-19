from telegram.error import TelegramError
from config import logger, TARGET_CHAT_ID

async def forward_media_to_target(context, media_type, file_id):
    try:
        if media_type == "photo":
            await context.bot.send_photo(chat_id=TARGET_CHAT_ID, photo=file_id)
            logger.info(f"Imagen reenviada de forma anónima a {TARGET_CHAT_ID}")
        elif media_type == "video":
            await context.bot.send_video(chat_id=TARGET_CHAT_ID, video=file_id)
            logger.info(f"Video reenviado de forma anónima a {TARGET_CHAT_ID}")
        else:
            logger.warning(f"Tipo de media no soportada para reenvío: {media_type}")
    except TelegramError as e:
        logger.error(f"Error reenviando media al destino: {e}", exc_info=True)