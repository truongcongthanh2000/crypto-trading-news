from .logger import Logger
from .config import Config
from .notification import Message
from telethon import TelegramClient, types
from telethon.sessions import StringSession
import asyncio
from datetime import datetime, timedelta, timezone
import pytz
from .util import is_command_trade
class Telegram:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH, proxy=config.TELEGRAM_PROXY.telethon_proxy)
        self.map_offset_date = {}
        self.channels = []

    async def connect(self):
        await self.client.start()
        for channel in self.config.TELEGRAM_LIST_CHANNEL:
            if channel[0] != '@':
                channel_v = await self.client.get_entity(types.PeerChannel(int(channel)))
            else:
                channel_v = await self.client.get_entity(channel)
            self.channels.append(channel_v)
            self.map_offset_date[channel_v.id] = datetime.now(tz=timezone.utc) - timedelta(seconds = self.config.TELEGRAM_SLA)

    async def pull_messages(self, channel: types.Channel):
        async def get_messages():
            offset_date = self.map_offset_date[channel.id]
            result = []
            async for msg in self.client.iter_messages(channel, limit=self.config.TELEGRAM_LIMIT):
                if msg.date <= offset_date and (msg.edit_date is None or msg.edit_date <= offset_date):
                    continue
                result.append(msg)
            return result
        try:
            messages = await get_messages()
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.pull_messages - {channel.title} - {channel.id}",
                body=f"Error: {err=}", 
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)
            messages = []
        if len(messages) > 0:
            for message in messages:
                date = message.date
                if message.edit_date is not None:
                    date = message.edit_date
                if date > self.map_offset_date[channel.id]:
                    self.map_offset_date[channel.id] = date
        return messages
    
    async def forward_messages(self, channel: types.Channel):
        def send_message(messages, channel_id):
            for message in messages:
                body = message.message
                url = f"https://t.me/{channel.id}/{message.id}"
                if channel.username is not None:
                    url = f"https://t.me/{channel.username}/{message.id}"
                body += f"\n\n**[Link: {url}]({url})**"
                self.logger.info(Message(
                    title= f"Telegram - {channel.title} - Time: {message.date.astimezone(pytz.timezone(self.config.TIMEZONE))}",
                    body=body,
                    chat_id=channel_id
                ), notification=True)
        async def forward(messages, channel_id):
            if len(messages) == 0:
                return
            if channel.noforwards:
                send_message(messages, channel_id)
                return
            try:
                await self.client.forward_messages(channel_id, messages)
            except Exception as err:
                self.logger.error(Message(
                    title=f"Error Telegram.forward_messages - {channel.title} - {channel.id}",
                    body=f"Error: {err=}", 
                    chat_id=self.config.TELEGRAM_LOG_PEER_ID
                ))
                send_message(messages, channel_id)
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
                title=f"Error Telegram.forward_messages - {channel.title} - {channel.id}",
                body=f"Error: {err=}", 
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)

    async def scrape_channel_messages(self):
        if self.config.TELEGRAM_ENABLED == False:
            return
        # self.logger.info(Message(f"Telegram.scrape_channel_messages with list channel: {', '.join(self.config.TELEGRAM_LIST_CHANNEL)}"))
        # Prepare all tasks concurrently
        tasks = [
            self.forward_messages(channel)
            for channel in self.channels
        ]

        # Run all profile scrapes in parallel
        await asyncio.gather(*tasks)