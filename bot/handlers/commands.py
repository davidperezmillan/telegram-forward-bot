from config import MSG, FORWARD_MODE, logger

async def set_mode(update, context):
    global FORWARD_MODE
    args = context.args
    logger.info(f"Comando /modo recibido con argumentos: {args}")
    if not args:
        if FORWARD_MODE == "auto":
            FORWARD_MODE = "buttons"
        else:
            FORWARD_MODE = "auto"
        await update.message.reply_text(MSG["mode_toggled"].format(mode=FORWARD_MODE))
    elif args[0].lower() in ["auto", "buttons"]:
        FORWARD_MODE = args[0].lower()
        await update.message.reply_text(MSG["mode_changed"].format(mode=FORWARD_MODE))
    else:
        await update.message.reply_text(MSG["mode_usage"])

    logger.info(f"Modo de reenvío actualizado a: {FORWARD_MODE}")