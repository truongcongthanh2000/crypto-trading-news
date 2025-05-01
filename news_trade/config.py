import yaml
import os
import json
class Config:
    def __init__(self):
        config = {
            "twitter": {
                "cookies": "{}",
                "scrape_sleep_time": 600,
                "sla": "86400",
                "list_query": []
            },
            "threads": {
                "list_username": [],
                "sla": 86400,
                "scrape_sleep_time": 60
            }
        }
        self.TWITTER_COOKIES_DICT = {}
        if os.path.exists("config/config_remote.yaml"):
            with open("config/config_remote.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        self.THREADS_LIST_USERNAME = [thread.strip() for thread in os.environ.get("THREADS_LIST_USERNAME", "").split() if thread.strip()] or config["threads"]["list_username"]
        self.THREADS_SLA = int(os.environ.get("THREADS_SLA") or config["threads"]["sla"])
        self.THREADS_SCRAPE_SLEEP_TIME = int(os.environ.get("THREADS_SCRAPE_SLEEP_TIME") or config["threads"]["scrape_sleep_time"])
        self.TELEGRAM_NOTIFY_URL = os.environ.get("TELEGRAM_NOTIFY_URL")
        self.CHROMIUM_EXECUTABLE_PATH = os.environ.get("CHROMIUM_EXECUTABLE_PATH")
        self.TWITTER_COOKIES_DICT = json.loads(os.environ.get("TWITTER_COOKIES") or config["twitter"]["cookies"])
        self.TWITTER_SCRAPE_SLEEP_TIME = int(os.environ.get("TWITTER_SCRAPE_SLEEP_TIME") or config["twitter"]["scrape_sleep_time"])
        self.TWITTER_LIST_QUERY = [query.strip() for query in os.environ.get("TWITTER_LIST_QUERY", "").split() if query.strip()] or config["twitter"]["list_query"]
        self.TWITTER_SLA = int(os.environ.get("TWITTER_SLA") or config["twitter"]["sla"])
