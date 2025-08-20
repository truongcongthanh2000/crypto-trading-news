# 📈 Social Trading News Crawler & Command Trading Bot

This project contains **two complementary tools** for cryptocurrency and financial markets:

1. **Social Trading News Crawler Bot** – Automatically collects and organizes market news from multiple online sources.  
2. **Command Trading Bot** – A CLI-based trading bot for automating cryptocurrency trades.

---

## 🚀 Features

### **Social Trading News Crawler Bot**
- **Real-time crawler**: Monitors news websites, blogs, forums, and social media (Threads, Twitter/X, Telegram, Discord) for discussions about social trading, markets, and investment strategies.
- **Real-time Telegram notifications**: Automatically sends alerts to your Telegram after crawling news.

### **Command Trading Bot**
- **Command-Line Interface**: Simple commands to control the bot.
- **Exchange Support**: Currently supports **Binance**.
- **Live Market Data**: Fetches real-time price data for trading decisions.
- **Risk Management**: Set stop-loss and take-profit levels.
- **Trade Notifications**: Alerts for trades and market events.

---

## 🛠 Getting Started

### 1️⃣ Prerequisites
- Python **3.10**
- Telegram bot & chat ID ([Guide](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a))

---

### 2️⃣ Install & Run

```bash
# Clone repository
git clone https://github.com/truongcongthanh2000/crypto-trading-news
cd crypto-trading-news

# Create config
cp config/config_remote.yaml.cfg config/config_remote.yaml
# Fill required fields in config_remote.yaml

# Install dependencies
pip3 install -r requirements.txt

# Run
python3 -m crypto_trading_news
```

## Deployment
### Cloud platform
In this project, I use [Heroku](https://www.heroku.com/) as cloud platform for deployment. Here is the config 
- [Buildpacks](https://devcenter.heroku.com/articles/buildpacks)
    - heroku/python
    - https://github.com/playwright-community/heroku-playwright-buildpack.git
- Region: **Europe** (**Note: Avoid choose USA because lack of support API from binance.us**)
- Stack: **heroku-22** (**Note: Do not use latest version heroku-24 because of incompatible with playwright**)
- Add-ons: **[Fixie](https://elements.heroku.com/addons/fixie)** for forward-proxy to binance APIs.

**Notes**: To scrape [Threads](https://www.threads.com), you need proxies to avoid rate limits. If you already have a rotating proxy service, set the environment variable ```TOR_PROXY_URL``` with its address. If not, note that [Heroku](https://www.heroku.com) is not suitable for this project because it cannot run Tor or custom proxy services. In that case, it’s recommended to deploy on a VPS, where you have full control over networking and proxy configuration.
### VPS
If you prefer to run this project on your own server instead of a PaaS like Heroku, you can deploy to a Virtual Private Server (VPS) such as **AWS EC2**, **DigitalOcean Droplet**, or **Vultr Instance**.

#### Provision a VPS
   - Choose a Linux distribution (Ubuntu 22.04 LTS recommended) with default version Python 3.10.
   - Minimum resources: **2 vCPU, 2 GB RAM** for smooth operation with Playwright.
#### Install & Run
```bash
# Clone repository
git clone https://github.com/truongcongthanh2000/crypto-trading-news
cd crypto-trading-news

# Create config
cp config/config_remote.yaml.cfg config/config_remote.yaml
# Fill required fields in config_remote.yaml

# Install system dependencies
bash install.sh

# Run without tor proxy
source .venv/bin/activate
python3 -m crypto_trading_news

# Run with tor proxy, fill field tor_proxy and num_ports in config_remote.yaml, ex: "socks5://127.0.0.1:9050", 4
NUM_PORTS=<number_of_ports> MAX_CIRCUIT=<seconds> pm2 start ecosystem.config.js
# Example: NUM_PORTS=5 MAX_CIRCUIT=300 pm2 start ecosystem.config.js -> opens 9050..9054, circuit rotates every 300s
# Example: NUM_PORTS=5 pm2 start ecosystem.config.js -> opens 9050..9052, circuit rotates every 600s
# Example: pm2 start ecosystem.config.js -> opens only 9050, circuit rotates every 600s
```
## Disclaimer

This bot collects publicly available information. The developers **ARE NOT RESPONSIBLE FOR** the accuracy or completeness of the information collected. Users should always conduct their own independent research and due diligence before making any investment decisions. The information provided by this bot should not be considered financial advice.
