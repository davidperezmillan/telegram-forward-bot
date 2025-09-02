from datetime import time
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, logger, MEDIA_CACHE, TARGET_CHAT_ID, MSG
from utils.helpers import delete_original_message
from handlers.commands import set_mode
from handlers.messages import forward_media
from handlers.callbacks import button_callback, handle_caption
from utils.forward import forward_media_to_target



async def send_videos_at_20(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Iniciando el envío automático de videos a las 20:00...")
    videos_to_delete = []

    for short_id, media_data in MEDIA_CACHE.items():
        try:
            entry = MEDIA_CACHE.get(short_id) 
            media_type = media_data["media_type"]
            chat_id = media_data["chat_id"]
            message_id = media_data["message_id"]
            file_id = media_data["file_id"]

            # Reenviar el video al chat objetivo
            await forward_media_to_target(context, TARGET_CHAT_ID, media_type, file_id, has_spoiler=True)
            await delete_all_messages(context,entry)
            logger.info(f"Video reenviado desde chat {chat_id}, mensaje {message_id}")

            # Agregar el video a la lista para eliminar
            videos_to_delete.append(short_id)
        except Exception as e:
            logger.error(f"Error al reenviar video {short_id}: {e}", exc_info=True)

    # Eliminar los videos del MEDIA_CACHE
    for short_id in videos_to_delete:
        del MEDIA_CACHE[short_id]
        logger.info(f"Video con ID {short_id} eliminado del MEDIA_CACHE")

    logger.info("Proceso de envío automático de videos completado.")


async def delete_all_messages(context, entry):
    await delete_original_message(entry["chat_id"], entry["message_id"], context)
    if "message_alt_id" in entry:
        for msg_id in entry["message_alt_id"]:
            await delete_original_message(entry["chat_id"], msg_id, context)


if __name__ == "__main__":
    logger.info("Iniciando bot de Telegram...")
    
    hour = int(MSG.get("hora_barrido", 20))
    minute = int(MSG.get("minuto_barrido", 0))

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(lambda app: app.job_queue.start()).build()

    app.add_handler(CommandHandler("modo", set_mode))
    app.add_handler(MessageHandler(filters.PHOTO, forward_media))
    app.add_handler(MessageHandler(filters.VIDEO, forward_media))
    app.add_handler(MessageHandler(filters.ANIMATION, forward_media))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))  # Capturar el caption

    # Programar el envío automático de videos a las 20:00
    app.job_queue.run_daily(send_videos_at_20, time(hour=hour, minute=minute, second=0))

    app.run_polling()