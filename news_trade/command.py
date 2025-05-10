from .logger import Logger
from .config import Config
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start_cmd_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles command /start from the admin"""
    await update.message.reply_text(text="👋 Hello, admin!")

class Command:
    def __init__(self, config: Config):
        self.config = config
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    def start_bot(self):
        self.application.add_handler(CommandHandler("start", start_cmd_from_admin))

        self.application.run_polling()

