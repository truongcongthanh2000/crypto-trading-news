# Social Trading News Crawler Bot

This bot is designed to automatically collect and organize news and information relevant to social trading platforms and related financial markets. It continuously monitors various online sources to provide users with a consolidated feed of potentially valuable insights.

## Features

* **Real-time crawler:** The bot actively crawls news websites, blogs, forums, and social media platforms such as [Threads](https://www.threads.com/), [Twitter](https://x.com/home), [Telegram](https://telegram.org/), and [Discord](https://discord.com/) that discuss social trading, financial markets, and investment strategies.
* **Real-time notify:** The bot will auto notify into telegram after crawls news.

## Getting Started

- This repo is developed on Python version >= 3.10
- **Clone this repo**:  https://github.com/truongcongthanh2000/news_trade
- Add file config
    - Setup bot telegram and chat_id [how to get chat_id telegram](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a)
    - Create new file config_remote.yaml and fill all fields
- Install all dependencies ```pip3 install -r requirements.txt```
- Run code ```python3 -m news_trade```

## Deployment
In this project, I use [Heroku](https://www.heroku.com/) as cloud platform for deployment. Here is the config 
- [Buildpacks](https://devcenter.heroku.com/articles/buildpacks)
    - heroku/python
    - https://github.com/playwright-community/heroku-playwright-buildpack.git
- Region: **Europe**
- Stack: **heroku-22** (**Note: Do not use latest version heroku-24 because of incompatible with playwright**)

## Disclaimer

This bot collects publicly available information. The developers **ARE NOT RESPONSIBLE FOR** the accuracy or completeness of the information collected. Users should always conduct their own independent research and due diligence before making any investment decisions. The information provided by this bot should not be considered financial advice.
