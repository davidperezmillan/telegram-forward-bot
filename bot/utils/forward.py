from telegram.error import TelegramError
from config import logger, TARGET_CHAT_ID

async def forward_media_to_target(context, chat_id, media_type, file_id, has_spoiler=False):
    try:
        if media_type == "photo":
            await context.bot.send_photo(chat_id=chat_id, photo=file_id, has_spoiler=has_spoiler)
            logger.info(f"Imagen reenviada de forma anónima a {chat_id}")
        elif media_type == "video":
            await context.bot.send_video(chat_id=chat_id, video=file_id, has_spoiler=has_spoiler)
            logger.info(f"Video reenviado de forma anónima a {chat_id}")
        else:
            logger.warning(f"Tipo de media no soportada para reenvío: {media_type}")
    except TelegramError as e:
        logger.error(f"Error reenviando media al destino: {e}", exc_info=True)