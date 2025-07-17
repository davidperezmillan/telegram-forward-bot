import logging
import os
import json
from uuid import uuid4

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError

# Cargar mensajes desde messages.json
with open('messages.json', encoding='utf-8') as f:
    MSG = json.load(f)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
DEFAULT_FORWARD_MODE = os.getenv("FORWARD_MODE", "auto").lower()
FORWARD_MODE = DEFAULT_FORWARD_MODE
MEDIA_CACHE = {}

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global FORWARD_MODE
    args = context.args
    if not args:
        # Alternar modo
        if FORWARD_MODE == "auto":
            FORWARD_MODE = "buttons"
            await update.message.reply_text(MSG["mode_toggled"].format(mode=FORWARD_MODE))
        else:
            FORWARD_MODE = "auto"
            await update.message.reply_text(MSG["mode_toggled"].format(mode=FORWARD_MODE))
    elif args[0].lower() in ["auto", "buttons"]:
        FORWARD_MODE = args[0].lower()
        await update.message.reply_text(MSG["mode_changed"].format(mode=FORWARD_MODE))
    else:
        await update.message.reply_text(MSG["mode_usage"])

async def delete_original_message(chat_id, message_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Mensaje {message_id} borrado de {chat_id}")
    except TelegramError as e:
        logger.warning(f"No se pudo borrar el mensaje {message_id}: {e}")

async def forward_media_to_target(context: ContextTypes.DEFAULT_TYPE, media_type: str, file_id: str):
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

async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global FORWARD_MODE
    logger.info(f"Mensaje recibido de {update.message.chat_id}")
    logger.info(f"Chat de destino: {TARGET_CHAT_ID}")
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

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(MSG["forward_button"], callback_data=f"forward|{short_id}"),
                        InlineKeyboardButton(MSG["discard_button"], callback_data=f"discard|{short_id}"),
                    ]
                ]
            )
            await update.message.reply_text(
                MSG["choose_action"],
                reply_markup=keyboard,
            )
        else:
            logger.warning(f"Variable FORWARD_MODE tiene un valor desconocido: {FORWARD_MODE}")

    except Exception as e:
        logger.error(f"Error manejando mensaje recibido: {e}", exc_info=True)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # Borrar mensaje original (foto/vídeo)
        await delete_original_message(entry["chat_id"], entry["message_id"], context)

        if action == "forward":
            await forward_media_to_target(context, entry["media_type"], entry["file_id"])

        # Borrar mensaje con botones
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

if __name__ == "__main__":
    logger.info("Iniciando bot de Telegram...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("modo", set_mode))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, forward_media))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()
