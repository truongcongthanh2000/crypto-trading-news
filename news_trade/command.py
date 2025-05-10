from .logger import Logger
from .config import Config
from .notification import Message
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, Updater
import apprise
import socket

class Command:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    def start_bot(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_error_handler(self.error)
        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles command /start from the admin"""
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)        
        await update.message.reply_text(text=f"👋 Hello, your server IP is {IPAddr}")

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.error(Message(
            title=f"Error Command.Update {update}",
            body=f"Error Msg: {context.error}",
            format=apprise.NotifyFormat.TEXT
        ), True)