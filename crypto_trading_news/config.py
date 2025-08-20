import os
import json
import platform

from urllib.parse import urlparse
import random
from dotenv import load_dotenv

class ProxyConfig:
    def __init__(self, base_url: str | None, ports: int = 1):
        """
        base_url: like 'socks5://127.0.0.1'
        ports: number of sequential ports starting at 9050
        """
        self.base_url = base_url.strip() if base_url else None
        self.ports = ports if ports > 0 else 1

        if self.base_url:
            parsed = urlparse(self.base_url)
            self.scheme = parsed.scheme
            self.host = parsed.hostname
            self.start_port = parsed.port or 9050
            self.username = parsed.username
            self.password = parsed.password
            # generate port list
            self._ports = list(range(self.start_port, self.start_port + self.ports))
        else:
            self.scheme = None
            self.host = None
            self.start_port = None
            self.username = None
            self.password = None
            self._ports = []

    def _pick_port(self) -> int | None:
        if not self._ports:
            return None
        return random.choice(self._ports)

    @property
    def playwright_proxy(self) -> dict | None:
        port = self._pick_port()
        if not port:
            return None
        proxy = {"server": f"{self.scheme}://{self.host}:{port}"}
        if self.username and self.password:
            proxy["username"] = self.username
            proxy["password"] = self.password
        return proxy

    @property
    def python_telegram_bot_proxy(self) -> str | None:
        port = self._pick_port()
        if not port:
            return None
        return f"{self.scheme}://{self.host}:{port}"

    @property
    def telethon_proxy(self) -> dict | None:
        port = self._pick_port()
        if not port:
            return None
        proxy = {
            "proxy_type": self.scheme,
            "addr": self.host,
            "port": port,
        }
        if self.username:
            proxy["username"] = self.username
        if self.password:
            proxy["password"] = self.password
        return proxy

    @property
    def binance_proxies(self) -> dict | None:
        port = self._pick_port()
        if not port:
            return None
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        url = f"{self.scheme}://{auth}{self.host}:{port}"
        return {"http": url, "https": url}

    def to_dict(self) -> dict:
        if not self.base_url:
            return {
                "base_url": None,
                "scheme": None,
                "host": None,
                "ports": [],
                "username": None,
                "password": None,
            }
        return {
            "base_url": self.base_url,
            "scheme": self.scheme,
            "host": self.host,
            "ports": [self._ports[0], "....", self._ports[-1]],
            "username": "***" if self.username else None,
            "password": "***" if self.password else None,
        }

    def __repr__(self):
        return f"ProxyConfig({self.to_dict()})"

class Config:
    def __init__(self):
        # Load .env only if it exists (so production won't break)
        load_dotenv(dotenv_path=".env", override=False)
        # Twitter
        self.TWITTER_COOKIES_DICT = json.loads(os.environ.get("TWITTER_COOKIES", "{}"))
        self.TWITTER_LIST_QUERY = [query.strip() for query in os.environ.get("TWITTER_LIST_QUERY", "").split() if query.strip()]
        self.TWITTER_SCRAPE_SLEEP_TIME = int(os.environ.get("TWITTER_SCRAPE_SLEEP_TIME", 600))
        self.TWITTER_SLA = int(os.environ.get("TWITTER_SLA", 86400))
        self.TWITTER_TWEETS_COUNT = int(os.environ.get("TWITTER_TWEETS_COUNT", 5))
        self.TWITTER_ENABLED = os.environ.get("TWITTER_ENABLED", "false").lower() == "true"

        # Threads
        self.THREADS_LIST_USERNAME = [thread.strip() for thread in os.environ.get("THREADS_LIST_USERNAME", "").split() if thread.strip()]
        self.THREADS_SLA = int(os.environ.get("THREADS_SLA", 600))
        self.THREADS_SCRAPE_SLEEP_TIME = int(os.environ.get("THREADS_SCRAPE_SLEEP_TIME", 60))
        self.THREADS_ENABLED = os.environ.get("THREADS_ENABLED", "false").lower() == "true"

        # Telegram
        self.TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", "")
        self.TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
        self.TELEGRAM_SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING", "")
        self.TELEGRAM_TRADE_PEER_ID = int(os.environ.get("TELEGRAM_TRADE_PEER_ID", -1))
        self.TELEGRAM_NEWS_PEER_ID = int(os.environ.get("TELEGRAM_NEWS_PEER_ID", -1))
        self.TELEGRAM_LOG_PEER_ID = int(os.environ.get("TELEGRAM_LOG_PEER_ID", -1))
        self.TELEGRAM_ALERT_CHAT_ID = int(os.environ.get("TELEGRAM_ALERT_CHAT_ID", -1))
        self.TELEGRAM_GROUP_CHAT_ID = int(os.environ.get("TELEGRAM_GROUP_CHAT_ID", -1))
        self.TELEGRAM_PNL_CHAT_ID = int(os.environ.get("TELEGRAM_PNL_CHAT_ID", 0))
        self.TELEGRAM_ROI_SIGNAL = float(os.environ.get("TELEGRAM_ROI_SIGNAL", 10))
        self.TELEGRAM_LIST_CHANNEL = [channel.strip() for channel in os.environ.get("TELEGRAM_LIST_CHANNEL", "").split() if channel.strip()]
        self.TELEGRAM_LIMIT = int(os.environ.get("TELEGRAM_LIMIT", 10))
        self.TELEGRAM_SLA = int(os.environ.get("TELEGRAM_SLA", 600))
        self.TELEGRAM_SCRAPE_SLEEP_TIME = int(os.environ.get("TELEGRAM_SCRAPE_SLEEP_TIME", 30))
        self.TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED", "false").lower() == "true"
        self.TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_BOT_TRADING_TOKEN = os.environ.get("TELEGRAM_BOT_TRADING_TOKEN", "")
        self.TELEGRAM_ME = os.environ.get("TELEGRAM_ME", "")

        # Discord
        self.DISCORD_ENABLED = os.environ.get("DISCORD_ENABLED", "false").lower() == "true"
        self.DISCORD_SLA = int(os.environ.get("DISCORD_SLA", 600))
        self.DISCORD_LIMIT = int(os.environ.get("DISCORD_LIMIT", 10))
        self.DISCORD_SCRAPE_SLEEP_TIME = int(os.environ.get("DISCORD_SCRAPE_SLEEP_TIME", 60))
        self.DISCORD_LIST_CHANNEL_ID = [channel.strip() for channel in os.environ.get("DISCORD_LIST_CHANNEL_ID", "").split() if channel.strip()]
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")

        # Binance
        self.BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
        self.BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET", "")
        self.BINANCE_TLD = os.environ.get("BINANCE_TLD", "com")
        self.BINANCE_PROXY_URL = os.environ.get("BINANCE_PROXY_URL", "")

        # General
        self.TIMEZONE = os.environ.get("TIMEZONE", "Asia/Ho_Chi_Minh")

        # Proxy configs
        self.TOR_PROXY = ProxyConfig(os.environ.get("TOR_PROXY_URL"), int(os.environ.get("TOR_PROXY_NUM_PORTS", 1)))
        self.TELEGRAM_PROXY = ProxyConfig(os.environ.get("TELEGRAM_PROXY_URL"), int(os.environ.get("TELEGRAM_PROXY_NUM_PORTS", 1)))
    def beautify(self):
        response = {}
        for k, v in vars(self).items():
            if isinstance(v, ProxyConfig):
                response[k] = v.to_dict()   # safe masked dict
            else:
                response[k] = v
        response["platform"] = platform.system()
        response["TWITTER_COOKIES_TYPE"] = str(type(response["TWITTER_COOKIES_DICT"]))
        response["TWITTER_COOKIES_DICT"] = "{.....}"
        response["TELEGRAM_SESSION_STRING"] = "...."
        response["DISCORD_TOKEN"] = "...."
        response["BINANCE_API_KEY"] = "...."
        response["BINANCE_API_SECRET"] = "...."
        return response