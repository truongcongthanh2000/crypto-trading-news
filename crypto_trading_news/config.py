import yaml
import os
import json
import platform

from urllib.parse import urlparse
import random

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
            "ports": self._ports,
            "username": "***" if self.username else None,
            "password": "***" if self.password else None,
        }

    def __repr__(self):
        return f"ProxyConfig({self.to_dict()})"

class Config:
    def __init__(self):
        config = {
            "twitter": {
                "cookies": "{}",
                "scrape_sleep_time": 600,
                "sla": "86400",
                "list_query": [],
                "enabled": False,
                "tweets_count": 5
            },
            "threads": {
                "list_username": [],
                "sla": 86400,
                "scrape_sleep_time": 60,
                "enabled": False
            },
            "telegram": {
                "api_id": "",
                "api_hash": "",
                "session_string": "",
                "trade_peer_id": -1,
                "news_peer_id": -1,
                "log_peer_id": -1,
                "group_chat_id": -1,
                "pnl_chat_id": 0,
                "roi_signal": 10,
                "alert_chat_id": -1,
                "list_channel": [],
                "limit": 10,
                "sla": 600,
                "scrape_sleep_time": 30,
                "enabled": False,
                "bot_token": "",
                "bot_trading_token": "",
                "me": ""
            },
            "discord": {
                "enabled": False,
                "sla": 600,
                "limit": 10,
                "scrape_sleep_time": 60,
                "list_channel_id": [],
                "token": ""
            },
            "binance": {
                "api_key": "",
                "api_secret": "",
                "tld": "com",
                "proxy_url": ""
            },
            "tor_proxy": {
                "url": "",
                "num_ports": ""
            }
        }
        self.TWITTER_COOKIES_DICT = {}
        if os.path.exists("config/config_remote.yaml"):
            with open("config/config_remote.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

        self.THREADS_LIST_USERNAME = [thread.strip() for thread in os.environ.get("THREADS_LIST_USERNAME", "").split() if thread.strip()] or config["threads"]["list_username"]
        self.THREADS_SLA = int(os.environ.get("THREADS_SLA") or config["threads"]["sla"])
        self.THREADS_SCRAPE_SLEEP_TIME = int(os.environ.get("THREADS_SCRAPE_SLEEP_TIME") or config["threads"]["scrape_sleep_time"])
        if "THREADS_ENABLED" in os.environ:
            self.THREADS_ENABLED = os.environ.get("THREADS_ENABLED").lower() == "true"
        else:
            self.THREADS_ENABLED = config["threads"]["enabled"]

        self.TWITTER_COOKIES_DICT = json.loads(os.environ.get("TWITTER_COOKIES") or config["twitter"]["cookies"])
        self.TWITTER_SCRAPE_SLEEP_TIME = int(os.environ.get("TWITTER_SCRAPE_SLEEP_TIME") or config["twitter"]["scrape_sleep_time"])
        self.TWITTER_LIST_QUERY = [query.strip() for query in os.environ.get("TWITTER_LIST_QUERY", "").split() if query.strip()] or config["twitter"]["list_query"]
        self.TWITTER_SLA = int(os.environ.get("TWITTER_SLA") or config["twitter"]["sla"])
        self.TWITTER_TWEETS_COUNT = int(os.environ.get("TWITTER_TWEETS_COUNT") or config["twitter"]["tweets_count"])
        if "TWITTER_ENABLED" in os.environ:
            self.TWITTER_ENABLED = os.environ.get("TWITTER_ENABLED").lower() == "true"
        else:
            self.TWITTER_ENABLED = config["twitter"]["enabled"]

        self.TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID") or config["telegram"]["api_id"]
        self.TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH") or config["telegram"]["api_hash"]
        self.TELEGRAM_SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING") or config["telegram"]["session_string"]
        self.TELEGRAM_TRADE_PEER_ID = int(os.environ.get("TELEGRAM_TRADE_PEER_ID") or config["telegram"]["trade_peer_id"])
        self.TELEGRAM_NEWS_PEER_ID = int(os.environ.get("TELEGRAM_NEWS_PEER_ID") or config["telegram"]["news_peer_id"])
        self.TELEGRAM_LOG_PEER_ID = int(os.environ.get("TELEGRAM_LOG_PEER_ID") or config["telegram"]["log_peer_id"])
        self.TELEGRAM_ALERT_CHAT_ID = int(os.environ.get("TELEGRAM_ALERT_CHAT_ID") or config["telegram"]["alert_chat_id"])
        self.TELEGRAM_GROUP_CHAT_ID = int(os.environ.get("TELEGRAM_GROUP_CHAT_ID") or config["telegram"]["group_chat_id"])
        self.TELEGRAM_PNL_CHAT_ID = int(os.environ.get("TELEGRAM_PNL_CHAT_ID") or config["telegram"]["pnl_chat_id"])
        self.TELEGRAM_ROI_SIGNAL = int(os.environ.get("TELEGRAM_ROI_SIGNAL") or config["telegram"]["roi_signal"])
        self.TELEGRAM_LIST_CHANNEL = [channel.strip() for channel in os.environ.get("TELEGRAM_LIST_CHANNEL", "").split() if channel.strip()] or config["telegram"]["list_channel"]
        self.TELEGRAM_LIMIT = int(os.environ.get("TELEGRAM_LIMIT") or config["telegram"]["limit"])
        self.TELEGRAM_SLA = int(os.environ.get("TELEGRAM_SLA") or config["telegram"]["sla"])
        self.TELEGRAM_SCRAPE_SLEEP_TIME = int(os.environ.get("TELEGRAM_SCRAPE_SLEEP_TIME") or config["telegram"]["scrape_sleep_time"])
        if "TELEGRAM_ENABLED" in os.environ:
            self.TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED").lower() == "true"
        else:
            self.TELEGRAM_ENABLED = config["telegram"]["enabled"]
        self.TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or config["telegram"]["bot_token"]
        self.TELEGRAM_BOT_TRADING_TOKEN = os.environ.get("TELEGRAM_BOT_TRADING_TOKEN") or config["telegram"]["bot_trading_token"]
        self.TELEGRAM_ME = os.environ.get("TELEGRAM_ME") or config["telegram"]["me"]

        if "DISCORD_ENABLED" in os.environ:
            self.DISCORD_ENABLED = os.environ.get("DISCORD_ENABLED").lower() == "true"
        else:
            self.DISCORD_ENABLED = config["discord"]["enabled"]
        self.DISCORD_SLA = int(os.environ.get("DISCORD_SLA") or config["discord"]["sla"])
        self.DISCORD_LIMIT = int(os.environ.get("DISCORD_LIMIT") or config["discord"]["limit"])
        self.DISCORD_SCRAPE_SLEEP_TIME = int(os.environ.get("DISCORD_SCRAPE_SLEEP_TIME") or config["discord"]["scrape_sleep_time"])
        self.DISCORD_LIST_CHANNEL_ID =  [channel.strip() for channel in os.environ.get("DISCORD_LIST_CHANNEL_ID", "").split() if channel.strip()] or config["discord"]["list_channel_id"]
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN") or config["discord"]["token"]

        self.BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY") or config["binance"]["api_key"]
        self.BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET") or config["binance"]["api_secret"]
        self.BINANCE_TLD = os.environ.get("BINANCE_TLD") or config["binance"]["tld"]
        self.BINANCE_PROXY_URL = os.environ.get("BINANCE_PROXY_URL") or config["binance"]["proxy_url"]

        self.TIMEZONE = os.environ.get("TIMEZONE") or "Asia/Ho_Chi_Minh"
        self.TOR_PROXY = ProxyConfig(os.environ.get("TOR_PROXY_URL") or config["tor_proxy"]["url"], int(os.environ.get("TOR_PROXY_NUM_PORTS") or config["tor_proxy"]["num_ports"] or "1"))
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