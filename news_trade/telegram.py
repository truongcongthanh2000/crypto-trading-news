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
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH).start()
        self.map_offset_date = {}

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
        async def forward(messages):
            try:
                messages_news = []
                messages_trade = []
                for message in messages:
                    if is_command_trade(message.message):
                        messages_trade.append(message)
                    else:
                        messages_news.append(message)
                if len(messages_trade) > 0:
                    await self.client.forward_messages(self.config.TELEGRAM_TRADE_PEER_ID, messages_trade)
                if len(messages_news) > 0:
                    await self.client.forward_messages(self.config.TELEGRAM_NEWS_PEER_ID, messages_news)
            except Exception as err:
                self.logger.error(Message(
                    title=f"Error Telegram.forward_messages - {channel}",
                    body=f"Error: {err=}", 
                    format=None,
                    chat_id=self.config.TELEGRAM_LOG_PEER_ID
                ))
                for message in messages:
                    body = message.message
                    chat_id = self.config.TELEGRAM_NEWS_PEER_ID
                    if is_command_trade(message.message):
                        chat_id = self.config.TELEGRAM_TRADE_PEER_ID
                    body += f"\n\n**[Link: https://t.me/{channel[1:]}/{message.id}](https://t.me/{channel[1:]}/{message.id})**"
                    self.logger.info(Message(
                        title= f"Telegram - {channel} - Time: {message.date.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))}",
                        body=body,
                        chat_id=chat_id
                    ), notification=True)
                await asyncio.sleep(1)
        messages = await self.pull_messages(channel)
        if len(messages) > 0:
            try:
                await forward(messages=messages)
            except Exception as err:
                self.logger.error(Message(
                    title=f"Error Telegram.forward_messages - {channel}",
                    body=f"Error: {err=}", 
                    format=None,
                    chat_id=self.config.TELEGRAM_LOG_PEER_ID
                ), notification=True)
        await asyncio.sleep(1)
    
    async def scrape_channel_messages(self):
        if self.config.TELEGRAM_ENABLED == False:
            return
        # self.logger.info(Message(f"Telegram.scrape_channel_messages with list channel: {', '.join(self.config.TELEGRAM_LIST_CHANNEL)}"))
        for channel in self.config.TELEGRAM_LIST_CHANNEL:
            await self.forward_messages(channel)
