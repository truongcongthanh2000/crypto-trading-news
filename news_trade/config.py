import yaml
import os
class Config:
    def __init__(self):
        config = {
            "twitter": {
                "username": "",
                "email": "",
                "password": ""
            },
            "threads": {
                "list_username": [],
                "sla": 86400,
                "scrape_sleep_time": 60
            }
        }
        if os.path.exists("config/config_remote.yaml"):
            with open("config/config_remote.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        self.TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME") or config["twitter"]["username"]
        self.TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL") or config["twitter"]["email"]
        self.TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD") or config["twitter"]["password"]
        self.THREADS_LIST_USERNAME = [thread.strip() for thread in os.environ.get("THREADS_LIST_USERNAME", "").split() if thread.strip()] or config["threads"]["list_username"]
        self.THREADS_SLA = int(os.environ.get("THREADS_SLA") or config["threads"]["sla"])
        self.THREADS_SCRAPE_SLEEP_TIME = int(os.environ.get("THREADS_SCRAPE_SLEEP_TIME") or config["threads"]["scrape_sleep_time"])
        self.TELEGRAM_NOTIFY_URL = os.environ.get("TELEGRAM_NOTIFY_URL")
