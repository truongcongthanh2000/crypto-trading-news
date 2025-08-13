import json

from .config import Config
import telegramify_markdown
from telebot.types import LinkPreviewOptions, InputMediaPhoto, InputFile
from telebot import asyncio_helper
from telebot.async_telebot import AsyncTeleBot
import datetime
import asyncio
import aiohttp
import aiofiles
class Message:
    def __init__(self, body: str, chat_id: int = 0, title = 'News Trade', format: str | None = "MarkdownV2", image: str | None = None, images: list[str] | None = None, group_message_id: int | None = None):
        self.title = title
        self.body = body
        self.format = format
        self.image = image
        self.images = images
        self.chat_id = chat_id
        self.group_message_id = group_message_id
    def __str__(self):
        payload = {
            "title": self.title,
            "body": self.body,
            "format": self.format,
            "image": self.image,
            "images": self.images,
            "chat_id": self.chat_id,
            "group_message_id": self.group_message_id
        }
        return json.dumps(payload)
    def build_text_notify(self):
        return f"**{self.title}**\n{self.body}"


class NotificationHandler:
    def __init__(self, cfg: Config, enabled=True):
        if enabled:
            self.config = cfg
            self.queue = asyncio.Queue()
            self.enabled = True
            self.telebot = AsyncTeleBot(token=cfg.TELEGRAM_BOT_TOKEN)
        else:
            self.enabled = False

    async def notify(self, message: Message):
        text_msg = message.build_text_notify()
        if message.format is not None:
            text_msg = telegramify_markdown.markdownify(text_msg)
        if message.images is not None and len(message.images) > 1:
            list_media = []
            for index, image in enumerate(message.images):
                if index == 0:
                    list_media.append(InputMediaPhoto(
                        media=image,
                        caption=text_msg,
                        parse_mode=message.format
                    ))
                else:
                    list_media.append(InputMediaPhoto(media=image))
            try:
                await self.telebot.send_media_group(chat_id = message.chat_id, media=list_media, reply_to_message_id=message.group_message_id)
            except Exception as err:
                await self.telebot.send_message(chat_id = message.chat_id, text=text_msg + "\n" + f"Error send media group, err: {err}", parse_mode=message.format, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_to_message_id=message.group_message_id)
        elif message.image is not None and message.image != "":
            try:
                await self.telebot.send_photo(chat_id = message.chat_id, photo=message.image, caption = text_msg, parse_mode=message.format, reply_to_message_id=message.group_message_id)
            except Exception as err:
                # print(datetime.datetime.now(), " - ERROR - ", Message(
                #     title=f"Error Notification.send_photo, image={message.image}",
                #     body=f"Error: {err=}", 
                #     format=None,
                #     chat_id=self.config.TELEGRAM_LOG_PEER_ID
                # ))
                # Async HTTP request
                async with aiohttp.ClientSession() as session:
                    async with session.get(message.image) as resp:
                        resp.raise_for_status()  # Raise exception for HTTP errors
                        async with aiofiles.open("photo.png", "wb") as file:
                            async for chunk in resp.content.iter_chunked(1024):
                                await file.write(chunk)

                # Async send photo
                await self.telebot.send_photo(chat_id = message.chat_id, photo=InputFile("photo.png"), caption = text_msg, parse_mode=message.format, reply_to_message_id=message.group_message_id)
        else:
            await self.telebot.send_message(chat_id = message.chat_id, text=text_msg, parse_mode=message.format, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_to_message_id=message.group_message_id)

    async def process_queue(self):
        while True:
            message: Message = await self.queue.get()
            await self.notify(message)

    def send_notification(self, message: Message, attachments=None):
        if self.enabled:
            self.queue.put_nowait(message)
            # self.queue.put((message, attachments or []))
