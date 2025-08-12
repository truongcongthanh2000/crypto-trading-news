import yaml
import os
import json
import platform
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
            "notification": {
                "sleep_time": 10,
                "limit": 5
            },
            "proxies": {
                "nscriptiod_http": "",
                "nscriptiod_https": ""
            },
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

        self.NOTIFICATION_SLEEP_TIME = int(os.environ.get("NOTIFICATION_SLEEP_TIME") or config["notification"]["sleep_time"])
        self.NOTIFICATION_LIMIT = int(os.environ.get("NOTIFICATION_LIMIT") or config["notification"]["limit"])

        self.BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY") or config["binance"]["api_key"]
        self.BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET") or config["binance"]["api_secret"]
        self.BINANCE_TLD = os.environ.get("BINANCE_TLD") or config["binance"]["tld"]
        self.PROXIES = {
            "http": os.environ.get(os.environ.get("HTTP_FIELD") or "HTTP_FIELD") or config["proxies"]["nscriptiod_http"],
            "https": os.environ.get(os.environ.get("HTTPS_FIELD") or "HTTPS_FIELD") or config["proxies"]["nscriptiod_https"]
        }
    def beautify(self):
        response = vars(self).copy()
        response["platform"] = platform.system()
        response["TWITTER_COOKIES_TYPE"] = str(type(response["TWITTER_COOKIES_DICT"]))
        response["TWITTER_COOKIES_DICT"] = "{.....}"
        response["TELEGRAM_SESSION_STRING"] = "...."
        response["DISCORD_TOKEN"] = "...."
        response["BINANCE_API_KEY"] = "...."
        response["BINANCE_API_SECRET"] = "...."
        return response