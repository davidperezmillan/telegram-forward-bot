from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_TOKEN, logger
from handlers.commands import set_mode
from handlers.messages import forward_media
from handlers.callbacks import button_callback

if __name__ == "__main__":
    logger.info("Iniciando bot de Telegram...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("modo", set_mode))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, forward_media))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()