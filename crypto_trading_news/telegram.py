from .logger import Logger
from .config import Config
from .notification import Message
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
from datetime import datetime, timedelta, timezone
import pytz
from .util import is_command_trade
class Telegram:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        self.map_offset_date = {}

    async def connect(self):
        await self.client.start()

    async def pull_messages(self, channel: str):
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
        try:
            messages = await get_messages()
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.scrape_messages - {channel}",
                body=f"Error: {err=}", 
                format=None,
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)
            messages = []
        if len(messages) > 0:
            self.map_offset_date[channel] = messages[0].date
        return messages
    
    async def forward_messages(self, channel):
        async def forward(messages, channel_id):
            if len(messages) == 0:
                return
            try:
                await self.client.forward_messages(channel_id, messages)
            except Exception as err:
                self.logger.error(Message(
                    title=f"Error Telegram.forward_messages - {channel}",
                    body=f"Error: {err=}", 
                    format=None,
                    chat_id=self.config.TELEGRAM_LOG_PEER_ID
                ))
                for message in messages:
                    body = message.message
                    body += f"\n\n**[Link: https://t.me/{channel[1:]}/{message.id}](https://t.me/{channel[1:]}/{message.id})**"
                    self.logger.info(Message(
                        title= f"Telegram - {channel} - Time: {message.date.astimezone(pytz.timezone(self.config.TIMEZONE))}",
                        body=body,
                        chat_id=channel_id
                    ), notification=True)
                await asyncio.sleep(1)
        messages = await self.pull_messages(channel)
        messages_news = []
        messages_trade = []
        for message in messages:
            if is_command_trade(message.message):
                messages_trade.append(message)
            else:
                messages_news.append(message)
        try:
            await forward(messages_trade, self.config.TELEGRAM_TRADE_PEER_ID)
            await forward(messages_news, self.config.TELEGRAM_NEWS_PEER_ID)
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.forward_messages - {channel}",
                body=f"Error: {err=}", 
                format=None,
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)

    async def scrape_channel_messages(self):
        if self.config.TELEGRAM_ENABLED == False:
            return
        # self.logger.info(Message(f"Telegram.scrape_channel_messages with list channel: {', '.join(self.config.TELEGRAM_LIST_CHANNEL)}"))
        # Prepare all tasks concurrently
        tasks = [
            self.forward_messages(channel)
            for channel in self.config.TELEGRAM_LIST_CHANNEL
        ]

        # Run all profile scrapes in parallel
        await asyncio.gather(*tasks)