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
                "peer_id": -1,
                "list_channel": [],
                "limit": 10,
                "sla": 600,
                "scrape_sleep_time": 30,
                "enabled": False,
                "bot_token": ""
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
        self.TELEGRAM_PEER_ID = int(os.environ.get("TELEGRAM_PEER_ID") or config["telegram"]["peer_id"])
        self.TELEGRAM_LIST_CHANNEL = [channel.strip() for channel in os.environ.get("TELEGRAM_LIST_CHANNEL", "").split() if channel.strip()] or config["telegram"]["list_channel"]
        self.TELEGRAM_LIMIT = int(os.environ.get("TELEGRAM_LIMIT") or config["telegram"]["limit"])
        self.TELEGRAM_SLA = int(os.environ.get("TELEGRAM_SLA") or config["telegram"]["sla"])
        self.TELEGRAM_SCRAPE_SLEEP_TIME = int(os.environ.get("TELEGRAM_SCRAPE_SLEEP_TIME") or config["telegram"]["scrape_sleep_time"])
        if "TELEGRAM_ENABLED" in os.environ:
            self.TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED").lower() == "true"
        else:
            self.TELEGRAM_ENABLED = config["telegram"]["enabled"]
        self.TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or config["telegram"]["bot_token"]
    def beautify(self):
        response = vars(self).copy()
        response["platform"] = platform.system()
        response["TWITTER_COOKIES_TYPE"] = str(type(response["TWITTER_COOKIES_DICT"]))
        response["TWITTER_COOKIES_DICT"] = "{.....}"
        response["TELEGRAM_SESSION_STRING"] = "...."
        return response