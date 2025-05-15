from .logger import Logger
from .config import Config
from .notification import Message
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
from datetime import datetime, timedelta, timezone
import pytz
class Telegram:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH).start()
        self.map_offset_date = {}

    def pull_messages(self, channel: str):
        async def get_messages():
            offset_date = datetime.now(tz=timezone.utc) - timedelta(seconds = self.config.TELEGRAM_SLA)    
            if channel in self.map_offset_date:
                offset_date = self.map_offset_date[channel]
            result = []
            async for msg in self.client.iter_messages(channel, limit=self.config.TELEGRAM_LIMIT):
                if msg.date <= offset_date:
                    return result
                result.append(msg)
            return result
        loop = asyncio.get_event_loop()
        try:
            messages = loop.run_until_complete(get_messages())
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.scrape_messages - {channel}",
                body=f"Error: {err=}", 
                format=None
            ), True)
            messages = []
        if len(messages) > 0:
            self.map_offset_date[channel] = messages[0].date
        return messages
    
    def forward_messages(self, channel):
        async def forward(messages):
            await self.client.forward_messages(self.config.TELEGRAM_PEER_ID, messages)
        messages = self.pull_messages(channel)
        if len(messages) > 0:
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(forward(messages=messages))
            except Exception as err:
                self.logger.error(Message(
                    title=f"Error Telegram.forward_messages - {channel}",
                    body=f"Error: {err=}", 
                    format=None
                ), True)
    
    def scrape_channel_messages(self):
        if self.config.TELEGRAM_ENABLED == False:
            return
        self.logger.info(Message(f"Telegram.scrape_channel_messages with list channel: {', '.join(self.config.TELEGRAM_LIST_CHANNEL)}"))
        for channel in self.config.TELEGRAM_LIST_CHANNEL:
            self.forward_messages(channel)
