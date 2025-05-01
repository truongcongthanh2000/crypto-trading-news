from .logger import Logger
from .config import Config
from telethon import TelegramClient, events
from telethon.sessions import StringSession

class Telegram:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        if config.TELEGRAM_ENABLED == False:
            return
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH).start()

        @self.client.on(events.NewMessage(chats=self.config.TELEGRAM_LIST_CHANNEL))
        async def handler(event: events.NewMessage.Event):
            # self.logger.info(event.stringify())
            await self.client.forward_messages(self.config.TELEGRAM_BOT_USERNAME, event.message)
        self.client.loop.run_forever()