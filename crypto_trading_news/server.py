from .logger import Logger
from .twitter import Twitter
from .config import Config
from .threads import Threads
from .telegram import Telegram
from .discord import Discord
from .notification import NotificationHandler
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .binance_api import BinanceAPI
from .command import Command

async def run_all(logger: Logger, config: Config, threads: Threads, twitter: Twitter, telegram: Telegram, discord: Discord, notification: NotificationHandler, command: Command):
    scheduler = AsyncIOScheduler(logger=logger)
    if config.THREADS_ENABLED:
        for username in config.THREADS_LIST_USERNAME:
            scheduler.add_job(threads.retrieve_user_posts, 'interval', seconds=config.THREADS_SCRAPE_SLEEP_TIME, id=f"threads-{username}", args=[username])
    scheduler.add_job(twitter.scrape_user_tweets, 'interval', seconds=config.TWITTER_SCRAPE_SLEEP_TIME, id="twitter")
    scheduler.add_job(telegram.scrape_channel_messages, 'interval', seconds=config.TELEGRAM_SCRAPE_SLEEP_TIME, id="telegram")
    scheduler.add_job(discord.scrape_channel_messages, 'interval', seconds=config.DISCORD_SCRAPE_SLEEP_TIME, id="discord")
    scheduler.start()

    application = Application.builder().token(config.TELEGRAM_BOT_TRADING_TOKEN).read_timeout(7).get_updates_read_timeout(42).build()
    application.add_handler(CommandHandler("help", command.help))
    application.add_handler(CommandHandler("start", command.start))
    application.add_handler(CommandHandler("info", command.info))
    application.add_handler(CommandHandler("forder", command.forder))
    application.add_handler(CommandHandler("fclose", command.fclose))
    application.add_handler(CommandHandler("fch", command.fchart))
    application.add_handler(CommandHandler("fp", command.fprices))
    application.add_handler(CommandHandler("fstats", command.fstats))
    application.add_handler(CommandHandler("flimit", command.flimit))
    application.add_handler(CommandHandler("ftpsl", command.ftpsl))
    application.add_handler(CommandHandler("falert", command.falert))
    application.add_handler(CommandHandler("falert_track", command.falert_track))
    application.add_handler(CommandHandler("falert_list", command.falert_list))
    application.add_handler(CommandHandler("falert_remove", command.falert_remove))
    application.add_handler(CommandHandler("freplies", command.freplies))
    application.add_handler(CommandHandler("freplies_track", command.freplies_track))
    application.add_handler(CommandHandler("freplies_list", command.freplies_list))
    application.add_handler(CommandHandler("freplies_remove", command.freplies_remove))
    application.add_handler(MessageHandler(~filters.COMMAND, command.info_message))
    application.add_error_handler(command.error)

    async with application:
        await application.start()
        await command.post_init(application)
        await threads.setup_browser()
        await telegram.connect()

        await asyncio.gather(
            application.updater.start_polling(),
            notification.process_queue(),
            asyncio.Event().wait(),  # Keeps the loop alive unless interrupted
        )

        await threads.close_browser()
        await application.updater.stop()
        await application.stop()
    scheduler.shutdown()

def main():
    config = Config()
    notification = NotificationHandler(config)
    logger = Logger(config, notification, "news_trade_server")

    twitter = Twitter(config, logger)
    threads = Threads(config, logger)
    telegram = Telegram(config, logger)
    discord = Discord(config, logger)
    binanceAPI = BinanceAPI(config, logger)
    command = Command(config, logger, binance_api=binanceAPI, threads=threads)

    asyncio.run(run_all(logger=logger, config=config, threads=threads, twitter=twitter, telegram=telegram, discord=discord, notification=notification, command=command))
