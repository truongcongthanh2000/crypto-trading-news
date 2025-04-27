import yaml
class Config:
    def __init__(self):
        with open("config/config_remote.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.TWITTER_USERNAME = config["twitter"]["username"]
        self.TWITTER_EMAIL = config["twitter"]["email"]
        self.TWITTER_PASSWORD = config["twitter"]["password"]
        self.THREADS_LIST_USERNAME = config["threads"]["list_username"]
        self.THREADS_SLA = config["threads"]["sla"]
