from config import MEDIA_CACHE, logger
from utils.helpers import delete_original_message
from utils.forward import forward_media_to_target

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
        await delete_original_message(entry["chat_id"], entry["message_id"], context)

        if action == "forward":
            await forward_media_to_target(context, entry["media_type"], entry["file_id"])

        try:
            await context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
            )
            logger.info(f"Mensaje de botones borrado tras acción {action}")
        except TelegramError as e:
            logger.warning(f"No se pudo borrar mensaje de botones tras acción {action}: {e}")

    except Exception as e:
        logger.error(f"Error manejando callback del botón: {e}", exc_info=True)

    MEDIA_CACHE.pop(short_id, None)