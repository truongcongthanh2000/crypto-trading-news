import yaml
import os
from os import path

CONFIG_REMOTE_PATH = path.join(path.dirname(path.dirname(path.abspath(__file__))), "config/config_remote.yaml")

class Config:
    def __init__(self):
        with open(CONFIG_REMOTE_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME") or config["twitter"]["username"]
        self.TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL") or config["twitter"]["email"]
        self.TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD") or config["twitter"]["password"]
        self.THREADS_LIST_USERNAME = [thread.strip() for thread in os.environ.get("THREADS_LIST_USERNAME", "").split() if thread.strip()] or config["threads"]["list_username"]
        self.THREADS_SLA = os.environ.get("THREADS_SLA") or config["threads"]["sla"]
        self.THREADS_SCRAPE_SLEEP_TIME = os.environ.get("THREADS_SCRAPE_SLEEP_TIME") or config["threads"]["scrape_sleep_time"]
