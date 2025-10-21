from .logger import Logger
from .config import Config
from .notification import Message
from telethon import TelegramClient, types
from telethon.sessions import StringSession
from datetime import datetime, timedelta, timezone
import asyncio
import pytz
from .util import is_command_trade
class Telegram:
    TTL_SECONDS = 3600  # for example: 1 hour TTL for cache

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH, proxy=config.TELEGRAM_PROXY.telethon_proxy)
        self.channels = []
        self.map_latest_text = {}
        self.map_offset_date = {}

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
            if len(messages) > 0:
                for message in messages:
                    date = message.date
                    if message.edit_date is not None:
                        date = message.edit_date
                    if date > self.map_offset_date[channel.id]:
                        self.map_offset_date[channel.id] = date
                    await self.handle_message(channel, message)
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.pull_messages - {channel.title} - {channel.id}",
                body=f"Error: {err=}", 
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)
            messages = []
        return messages
    
    async def connect(self):
        await self.client.start()
        for channel in self.config.TELEGRAM_LIST_CHANNEL:
            if channel[0] != '@':
                channel_v = await self.client.get_entity(types.PeerChannel(int(channel)))
            else:
                channel_v = await self.client.get_entity(channel)
            self.channels.append(channel_v)
            self.map_offset_date[channel_v.id] = datetime.now(tz=timezone.utc) - timedelta(seconds = self.config.TELEGRAM_SLA)

    async def cleanup_map_latest_text(self):
        """Periodically clean up old entries from map_latest_text"""
        while True:
            try:
                now = datetime.now(tz=timezone.utc)
                expired_keys = [
                    k for k, (_, ts) in self.map_latest_text.items()
                    if (now - ts).total_seconds() > self.TTL_SECONDS
                ]
                for k in expired_keys:
                    del self.map_latest_text[k]
                if expired_keys:
                    self.logger.info(f"Cleaned {len(expired_keys)} expired Telegram cache entries")
            except Exception as err:
                self.logger.error(Message(
                    title="Error cleaning map_latest_text",
                    body=f"Error: {err}",
                    chat_id=self.config.TELEGRAM_LOG_PEER_ID
                ))
            await asyncio.sleep(300)  # cleanup every 5 minutes

    async def handle_message(self, channel: types.Channel, message: types.Message):
        """Handles forwarding or logging of a single message."""
        try:
            body = message.message or ""
            # No handle message same as previous
            key = f"{channel.id}_{message.id}"
            now = datetime.now(tz=timezone.utc)

            # Skip if same as last text
            if key in self.map_latest_text:
                last_text, _ = self.map_latest_text[key]
                if last_text == body:
                    return

            # Update cache with new text + timestamp
            self.map_latest_text[key] = (body, now)

            url = f"https://t.me/{channel.id}/{message.id}"
            if channel.username:
                url = f"https://t.me/{channel.username}/{message.id}"
            body += f"\n\n**[Link: {url}]({url})**"
            title = f"Telegram - {channel.title} - Time: {message.date.astimezone(pytz.timezone(self.config.TIMEZONE))}"

            # Split logic: trade vs news
            if is_command_trade(body):
                target = self.config.TELEGRAM_TRADE_PEER_ID
            else:
                target = self.config.TELEGRAM_NEWS_PEER_ID

            # Try to forward directly
            if not channel.noforwards:
                try:
                    await self.client.forward_messages(target, message)
                except Exception as err:
                    self.logger.error(Message(
                        title=f"Error forwarding message - {channel.title}",
                        body=f"Error: {err}",
                        chat_id=self.config.TELEGRAM_LOG_PEER_ID
                    ))
                    # fallback: send plain text
                    self.logger.info(Message(title=title, body=body, chat_id=target), notification=True)
            else:
                # channel.noforwards = True
                self.logger.info(Message(title=title, body=body, chat_id=target), notification=True)

        except Exception as err:
            self.logger.error(Message(
                title=f"Error Telegram.handle_message - {channel.title}",
                body=f"Error: {err}",
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ))

    async def scrape_channel_messages(self):
        if self.config.TELEGRAM_ENABLED == False:
            return
        # self.logger.info(Message(f"Telegram.scrape_channel_messages with list channel: {', '.join(self.config.TELEGRAM_LIST_CHANNEL)}"))
        # Prepare all tasks concurrently
        tasks = [
            self.pull_messages(channel)
            for channel in self.channels
        ]

        # Run all profile scrapes in parallel
        await asyncio.gather(*tasks)