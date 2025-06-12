import queue
import threading

import json
from .config import Config
import telegramify_markdown
import telebot
from telebot.types import LinkPreviewOptions, InputMediaPhoto, InputFile
from telebot import apihelper
import requests
import datetime
class Message:
    def __init__(self, body: str, title = 'News Trade', format: str | None = "MarkdownV2", image: str | None = None, images: list[str] | None = None):
        self.title = title
        self.body = body
        self.format = format
        self.image = image
        self.images = images
    def __str__(self):
        payload = {
            "title": self.title,
            "body": self.body,
            "format": self.format,
            "image": self.image,
            "images": self.images
        }
        return json.dumps(payload)
    def build_text_notify(self):
        return f"**{self.title}**\n{self.body}"


class NotificationHandler:
    def __init__(self, cfg: Config, enabled=True):
        if enabled:
            self.config = cfg
            self.queue = queue.Queue()
            self.enabled = True
            self.telebot = telebot.TeleBot(token=cfg.TELEGRAM_BOT_TOKEN)
        else:
            self.enabled = False

    def notify(self, message: Message):
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
                self.telebot.send_media_group(chat_id = self.config.TELEGRAM_PEER_ID, media=list_media)
            except Exception as err:
                self.telebot.send_message(chat_id = self.config.TELEGRAM_PEER_ID, text=text_msg + "\n" + f"Error send media group, err: {err}", parse_mode=message.format, link_preview_options=LinkPreviewOptions(is_disabled=True))
        elif message.image is not None and message.image != "":
            try:
                self.telebot.send_photo(chat_id = self.config.TELEGRAM_PEER_ID, photo=message.image, caption = text_msg, parse_mode=message.format)
            except Exception as err:
                print(datetime.datetime.now(), " - ERROR - ", Message(
                    title=f"Error Notification.send_photo, image={message.image}",
                    body=f"Error: {err=}", 
                    format=None
                ))
                request = requests.get(message.image, stream=True)
                with open("photo.png", "wb+") as file:
                    for c in request:
                        file.write(c)
                self.telebot.send_photo(chat_id = self.config.TELEGRAM_PEER_ID, photo=InputFile("photo.png"), caption = text_msg, parse_mode=message.format)
        else:
            self.telebot.send_message(chat_id = self.config.TELEGRAM_PEER_ID, text=text_msg, parse_mode=message.format, link_preview_options=LinkPreviewOptions(is_disabled=True))
    def process_queue(self):
        limit = self.config.NOTIFICATION_LIMIT
        while self.queue.empty() == False and limit > 0:
            # message, attachments = self.queue.get()
            message = self.queue.get()
            self.notify(message)
            limit -= 1

    def send_notification(self, message: Message, attachments=None):
        if self.enabled:
            self.queue.put(message)
            # self.queue.put((message, attachments or []))
