from .logger import Logger
from .config import Config
from .notification import Message
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from datetime import datetime, timedelta, timezone
import pytz
from .util import is_command_trade
class Telegram:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH, proxy=config.TELEGRAM_PROXY.telethon_proxy)
        self.channels = []

    async def connect(self):
        await self.client.start()
        for channel in self.config.TELEGRAM_LIST_CHANNEL:
            if channel[0] != '@':
                channel_v = await self.client.get_entity(types.PeerChannel(int(channel)))
            else:
                channel_v = await self.client.get_entity(channel)
            self.channels.append(channel_v)
        # Register handlers after connecting
        self._register_handlers()
        self.logger.info(Message("Telegram connected and event handlers registered"))

    def _register_handlers(self):
        # Handle new messages
        @self.client.on(events.NewMessage(chats=[c.id for c in self.channels]))
        async def handler_new(event: events.NewMessage.Event):
            message = event.message
            print("Debug handler_new ", event)
            self.logger.info(f"Debug handler_new, text: {message.message}, id: {message.id}")
            channel = await event.get_chat()
            await self.handle_message(channel, message)

        # Handle edits (optional)
        @self.client.on(events.MessageEdited(chats=[c.id for c in self.channels]))
        async def handler_edit(event: events.MessageEdited.Event):
            message = event.message
            print("Debug handler_edit ", event)
            self.logger.info(f"Debug handler_edit, text: {message.message}, id: {message.id}")
            channel = await event.get_chat()
            await self.handle_message(channel, message, edited=True)

    async def handle_message(self, channel, message, edited=False):
        """Handles forwarding or logging of a single message."""
        try:
            body = message.message or ""
            url = f"https://t.me/{channel.id}/{message.id}"
            if channel.username:
                url = f"https://t.me/{channel.username}/{message.id}"
            body += f"\n\n**[Link: {url}]({url})**"
            title = f"Telegram - {channel.title} - Time: {message.date.astimezone(pytz.timezone(self.config.TIMEZONE))}"
            if edited:
                title += " (Edited)"

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

    async def run_forever(self):
        self.logger.info(Message("Telegram event loop started"))
        await self.client.run_until_disconnected()