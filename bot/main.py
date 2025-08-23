from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_TOKEN, logger
from handlers.commands import set_mode
from handlers.messages import forward_media
from handlers.callbacks import button_callback, handle_caption

if __name__ == "__main__":
    logger.info("Iniciando bot de Telegram...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("modo", set_mode))
    app.add_handler(MessageHandler(filters.PHOTO, forward_media))
    app.add_handler(MessageHandler(filters.VIDEO, forward_media))
    app.add_handler(MessageHandler(filters.ANIMATION, forward_media))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))  # Capturar el caption

    app.run_polling()