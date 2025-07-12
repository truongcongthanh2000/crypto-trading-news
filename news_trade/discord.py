from .logger import Logger
from .config import Config
from .notification import Message
import requests
import time
from random import randint
from datetime import datetime
import pytz
from .util import is_command_trade

BASE_API_URL = "https://discord.com/api/v9"

def iso_to_unix(iso_timestamp: str):
    """Converts an ISO 8601 timestamp to a Unix timestamp.

    Args:
        iso_timestamp: The ISO 8601 timestamp string.

    Returns:
        The Unix timestamp (int).
    """
    dt_object = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    unix_timestamp = int(dt_object.timestamp())
    return unix_timestamp

class Discord:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.map_channel = {}
        self.map_guild = {}
        self.map_channel_last_message_id = {}
        self.base_headers = {"Authorization": self.config.DISCORD_TOKEN}
        self.init()
    
    def get_channel(self, channel_id: str):
        return requests.get(f"{BASE_API_URL}/channels/{channel_id}", headers=self.base_headers)

    def get_guild(self, guild_id: str):
        return requests.get(f"{BASE_API_URL}/guilds/{guild_id}", headers=self.base_headers)
    
    def init(self):
        try:
            for channel_id in self.config.DISCORD_LIST_CHANNEL_ID:
                response = self.get_channel(channel_id)
                response.raise_for_status()
                self.map_channel[channel_id] = response.json()
                time.sleep(randint(2, 5))
            for channel_id in self.map_channel:
                channel_info = self.map_channel[channel_id]
                guild_id = str(channel_info["guild_id"])
                if guild_id not in self.map_guild:
                    response = self.get_guild(guild_id)
                    response.raise_for_status()
                    self.map_guild[guild_id] = response.json()
                    time.sleep(randint(3, 7))
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Discord.init",
                body=f"Error: {err=}\nSo we must disabled discord", 
                format=None,
                chat_id=self.config.TELEGRAM_LOG_PEER_ID,
            ), True)
            self.config.DISCORD_ENABLED = False

    def build_message(self, message, channel_info, guild_info):
        message_timestamp = iso_to_unix(message['timestamp'])
        url = f"https://discord.com/channels/{guild_info['id']}/{channel_info['id']}/{message['id']}"
        payload = Message(title= f"Discord - {guild_info['name']}-{channel_info['name']} - Time: {datetime.fromtimestamp(message_timestamp, tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body="", chat_id=self.config.TELEGRAM_NEWS_PEER_ID)
        def capture(message):
            if is_command_trade(message['content']):
                payload.chat_id = self.config.TELEGRAM_TRADE_PEER_ID
            payload.body = f"{message['content']}\n\n[Link: {url}]({url})"
            if 'attachments' in message and len(message['attachments']) > 0:
                images = []
                for attachment in message['attachments']:
                    images.append(attachment['url'])
                if len(images) == 1:
                    payload.image = images[0]
                else:
                    payload.images = images
        if 'message_snapshots' in message and len(message['message_snapshots']) > 0:
            capture(message['message_snapshots'][0]['message'])
        else:
            capture(message)
        return payload

    def filter_messages(self, channel_info, guild_info, response_json) -> list[Message]:
        discord_messages = []
        time_now = int(time.time())
        for index, message in enumerate(response_json):
            message_id = message['id']
            message_timestamp = iso_to_unix(message['timestamp'])
            if index == 0:
                self.map_channel_last_message_id[channel_info["id"]] = message_id
            if time_now - message_timestamp >= self.config.DISCORD_SLA:
                continue
            discord_messages.append(self.build_message(message, channel_info, guild_info))
        return discord_messages
        
    def get_messages(self, channel_id):
        try:
            channel_info = self.map_channel[channel_id]
            guild_info = self.map_guild[str(channel_info["guild_id"])]
            url = f"{BASE_API_URL}/channels/{channel_id}/messages?limit={self.config.DISCORD_LIMIT}"
            if channel_id in self.map_channel_last_message_id:
                url += f"&after={self.map_channel_last_message_id[channel_id]}"
            # self.logger.info(Message(f"Threads.get_messages on {guild_info['name']}-{channel_info['name']} with url: {url}"))

            response = requests.get(url, headers=self.base_headers)
            response.raise_for_status()
            return self.filter_messages(channel_info, guild_info, response.json())
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Discord.get_messages - {guild_info['name']}-{channel_info['name']}({channel_id})",
                body=f"Error: {err=}", 
                format=None,
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), True)
        return []

    def scrape_channel_messages(self):
        if self.config.DISCORD_ENABLED == False:
            return
        messages = []
        for channel_id in self.map_channel:
            messages.extend(self.get_messages(channel_id))
            time.sleep(randint(5, 10))
        for message in messages:
            self.logger.info(message, True)