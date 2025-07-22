from config import FORWARD_MODE, MEDIA_CACHE, TARGET_CHAT_ID, MSG, logger
from utils.helpers import delete_original_message
from utils.forward import forward_media_to_target
from uuid import uuid4
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def forward_media(update, context):
    global FORWARD_MODE
    logger.info(f"Mensaje recibido de {update.message.chat_id}")
    logger.info(f"Chat de destino: {TARGET_CHAT_ID}")
    logger.info(f"Modo de reenvío: {FORWARD_MODE}")
    try:
        media_type = None
        file_id = None

        if update.message.photo:
            media_type = "photo"
            file_id = update.message.photo[-1].file_id
        elif update.message.video:
            media_type = "video"
            file_id = update.message.video.file_id
        else:
            logger.warning("Mensaje recibido sin imagen ni vídeo.")
            return

        if FORWARD_MODE == "auto":
            await forward_media_to_target(context, media_type, file_id)
            await delete_original_message(update.message.chat_id, update.message.message_id, context)
        elif FORWARD_MODE == "buttons":
            short_id = str(uuid4())[:8]
            MEDIA_CACHE[short_id] = {
                "chat_id": update.message.chat_id,
                "message_id": update.message.message_id,
                "media_type": media_type,
                "file_id": file_id,
            }
            ## recuperamos el chat de origen
            chat_origen = update.message.forward_origin.chat.title if update.message.forward_origin and update.message.forward_origin.chat else "Directo"
            textButton = MSG["choose_action"].format(
                #short_id=short_id,
                chat_origen=chat_origen,
                #media_type=media_type,
                #file_id=file_id,
            )
            try:
                file = await context.bot.get_file(file_id)
                if file:
                    textButton += f"\n{file.file_size / (1024 * 1024):.2f} MB"
            except Exception as e:
                logger.error(f"Error al obtener el archivo: {e}", exc_info=False)
                textButton += "\n(Error al obtener el tamaño del archivo)"

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(MSG["forward_button"], callback_data=f"forward|{short_id}"),
                        InlineKeyboardButton(MSG["discard_button"], callback_data=f"discard|{short_id}"),
                        InlineKeyboardButton(MSG["save_button"], callback_data=f"save|{short_id}"),  # Nuevo botón
                    ]
                ]
            )
            await update.message.reply_text(
                textButton,
                reply_markup=keyboard,
            )
        else:
            logger.warning(f"Variable FORWARD_MODE tiene un valor desconocido: {FORWARD_MODE}")

    except Exception as e:
        logger.error(f"Error manejando mensaje recibido: {e}", exc_info=True)