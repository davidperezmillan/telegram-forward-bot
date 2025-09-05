import time  # Importa el módulo estándar de time
from datetime import time as datetime_time  # Si necesitas usar datetime.time
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, logger, MEDIA_CACHE, TARGET_CHAT_ID, MSG, BARRIDOS
from utils.helpers import delete_original_message
from handlers.commands import set_mode
from handlers.messages import forward_media
from handlers.callbacks import button_callback, handle_caption
from utils.forward import forward_media_to_target




async def send_videos_at_barrido(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Iniciando proceso de envío automático de videos...")
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

def convertTime(horaMinuto):
    """ quita dos horas a la hora recibida en formato HH:MM """
    try:
        hora = int(horaMinuto.split(":")[0]) - 2
        minuto = int(horaMinuto.split(":")[1])
        if hora < 0:
            hora = 24 + hora
        return f"{hora}:{minuto}"
    except Exception as e:
        logger.error(f"Error al convertir la hora {horaMinuto}: {e}", exc_info=True)
        return horaMinuto  # Devuelve la hora original en caso de error


if __name__ == "__main__":
    logger.info("Iniciando bot de Telegram...")
  
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(lambda app: app.job_queue.start()).build()

    app.add_handler(CommandHandler("modo", set_mode))
    app.add_handler(MessageHandler(filters.PHOTO, forward_media))
    app.add_handler(MessageHandler(filters.VIDEO, forward_media))
    app.add_handler(MessageHandler(filters.ANIMATION, forward_media))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))  # Capturar el caption

    barridos = BARRIDOS
    if not barridos:
        logger.warning("No se han definido barridos en messages.json")
    else:
        logger.info(f"Barridos configurados: {barridos}")
        for barrido in barridos:
            # llamamos a convertTime para ajustar la hora
            hora, minuto = convertTime(barrido).split(":")
            hora = int(hora)
            minuto = int(minuto)
            logger.info(f"Programando barrido a las {hora:02}:{minuto:02}")
            # Programar el envío automático de videos a las hora especificada
            app.job_queue.run_daily(
                send_videos_at_barrido,
                datetime_time(hour=hora, minute=minuto, second=0)  # Usa datetime.time aquí
            )

    ## logeamos todos los trabajos programados
    for job in app.job_queue.jobs():
        logger.info(f"Trabajo programado: {job}")

    ## que hora es
    logger.info(f"La hora actual es: {time.strftime('%H:%M:%S', time.localtime())}")    


    app.run_polling()