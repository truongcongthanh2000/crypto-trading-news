import queue
import threading
from os import path

import json
from .config import Config
import telegramify_markdown
import telebot
from telebot.types import LinkPreviewOptions

class Message:
    def __init__(self, body: str, title = 'News Trade', format: str | None = "MarkdownV2", image: str | None = None):
        self.title = title
        self.body = body
        self.format = format
        self.image = image
    def __str__(self):
        payload = {
            "title": self.title,
            "body": self.body,
            "format": self.format,
            "image": self.image
        }
        return json.dumps(payload)
    def build_text_notify(self):
        return f"**{self.title}**\n{self.body}"


class NotificationHandler:
    def __init__(self, cfg: Config, enabled=True):
        if enabled:
            self.config = cfg
            self.queue = queue.Queue()
            self.start_worker()
            self.enabled = True
            self.telebot = telebot.TeleBot(token=cfg.TELEGRAM_BOT_TOKEN)
        else:
            self.enabled = False

    def start_worker(self):
        threading.Thread(target=self.process_queue, daemon=True).start()

    def notify(self, message: Message):
        text_msg = message.build_text_notify()
        if message.format is not None:
            text_msg = telegramify_markdown.markdownify(text_msg)
        if message.image is not None and message.image != "":
            self.telebot.send_photo(chat_id = self.config.TELEGRAM_PEER_ID, photo=message.image, caption = text_msg, parse_mode=message.format)
        else:
            self.telebot.send_message(chat_id = self.config.TELEGRAM_PEER_ID, text=text_msg, parse_mode=message.format, link_preview_options=LinkPreviewOptions(is_disabled=True))
    def process_queue(self):
        while True:
            # message, attachments = self.queue.get()
            message = self.queue.get()
            self.notify(message)
            self.queue.task_done()

    def send_notification(self, message: Message, attachments=None):
        if self.enabled:
            self.queue.put(message)
            # self.queue.put((message, attachments or []))
