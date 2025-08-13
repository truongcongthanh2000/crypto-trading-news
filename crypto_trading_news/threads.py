import json
import time
from typing import Dict

import jmespath
from nested_lookup import nested_lookup
from .logger import Logger
from .config import Config
from .notification import Message
from datetime import datetime
import pytz
import re
from .util import is_command_trade
import os
import psutil
from pyppeteer import launch
from pyppeteer.browser import Browser
import asyncio

def remove_redundant_spaces(text: str):
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Check if it's a progress line
        if re.match(r'^\|\s*.*?\s*\|.*$', line):
            if '100%' in line:
                # Keep the 100% progress line, but remove redundant spaces
                line = re.sub(r'\|\s*', '|', line)  # Remove spaces after first |
                line = re.sub(r'\s*\|', '|', line)  # Remove spaces before second |
                cleaned_lines.append(line)
            else:
                # Skip all other progress lines (0%-90%)
                continue
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
class Threads:
    """
    A basic interface for interacting with Threads.
    """
    BASE_URL = "https://www.threads.net"
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.map_last_timestamp = {}
        self.process = psutil.Process(os.getpid())

    async def setup_browser(self):
        self.browser: Browser = await launch(defaultViewport={"width": 1920, "height": 1080}, args=['--no-sandbox', '--headless', '--disable-gpu'])

    async def close_browser(self):
        await self.browser.close()

    def log_resources(self, note=""):
        mem_mb = self.process.memory_info().rss / (1024 * 1024)
        cpu_percent = self.process.cpu_percent(interval=None)
        net_io = self.process.net_io_counters() if hasattr(self.process, "net_io_counters") else None

        net_info = ""
        if net_io:
            net_info = f", Net: sent={net_io.bytes_sent/1024:.1f} KB, recv={net_io.bytes_recv/1024:.1f} KB"

        self.logger.info(
            f"[Resources] {note} - CPU: {cpu_percent:.1f}% | RAM: {mem_mb:.2f} MB{net_info}"
        )

    # Note: we'll also be using parse_thread function we wrote earlier:

    def parse_thread(self, data: Dict) -> Dict:
        """Parse Twitter tweet JSON dataset for the most important fields"""
        result = jmespath.search(
            """{
            text: post.caption.text,
            published_on: post.taken_at,
            id: post.id,
            pk: post.pk,
            code: post.code,
            username: post.user.username,
            user_pic: post.user.profile_pic_url,
            user_verified: post.user.is_verified,
            user_pk: post.user.pk,
            user_id: post.user.id,
            has_audio: post.has_audio,
            reply_count: view_replies_cta_string,
            like_count: post.like_count,
            images: post.image_versions2.candidates[0].url,
            image_count: post.carousel_media_count,
            videos: post.video_versions[].url
        }""",
            data,
        )
        result["videos"] = list(set(result["videos"] or []))
        if result["reply_count"] and type(result["reply_count"]) != int:
            result["reply_count"] = int(result["reply_count"].split(" ")[0])
        result[
            "url"
        ] = f"{self.BASE_URL}/@{result['username']}/post/{result['code']}"
        return result

    def parse_profile(self, data: Dict) -> Dict:
        """Parse Threads profile JSON dataset for the most important fields"""
        result = jmespath.search(
            """{
            is_private: text_post_app_is_private,
            is_verified: is_verified,
            profile_pic: hd_profile_pic_versions[-1].url,
            username: username,
            full_name: full_name,
            bio: biography,
            bio_links: bio_links[].url,
            followers: follower_count
        }""",
            data,
        )
        result["url"] = f"{self.BASE_URL}/@{result['username']}"
        return result



    async def scrape_thread(self, url: str) -> dict:
        """Scrape Threads their recent posts and there profile if exists from a given URL"""
        parsed = {
            "user": {},
            "threads": [],
        }
        try:
            # page = await browser.new_page()
            page = await self.browser.newPage()

            await page.goto(url)
            # wait for page to finish loading
            await page.waitForSelector("[data-pressable-container=true]", timeout=3000)
            
            # Extract all JSON blobs directly in the browser
            hidden_datasets = await page.evaluate('''() => {
                return Array.from(
                    document.querySelectorAll('script[type="application/json"][data-sjs]'),
                    el => el.textContent
                );
            }''')
            hidden_datasets = await page.evaluate('''() => {
                const scripts = document.querySelectorAll('script[type="application/json"][data-sjs]');
                const parsed = [];
                for (const el of scripts) {
                    const txt = el.textContent;
                    if (!txt.includes('"ScheduledServerJS"')) continue;
                    const isProfile = txt.includes('follower_count');
                    const isThreads = txt.includes('thread_items');
                    if (!isProfile && !isThreads) continue;
                    try {
                        parsed.push({ data: JSON.parse(txt), isProfile, isThreads });
                    } catch {}
                }
                return parsed;
            }''')
            for item in hidden_datasets:
                if item['isProfile']:
                    user_data = nested_lookup('user', item['data'])
                    if user_data:
                        parsed['user'] = self.parse_profile(user_data[0])
                if item['isThreads']:
                    thread_items = nested_lookup('thread_items', item['data'])
                    parsed['threads'].extend(
                        self.parse_thread(t) for thread in thread_items for t in thread
                    )
            await page.close()
            return parsed
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Threads.scrape_thread - url={url}",
                body=f"Error: {err=}", 
                format=None,
                chat_id=self.config.TELEGRAM_LOG_PEER_ID
            ), notification=True)
            return parsed

    async def retrieve_user_posts(self, username: str) -> list[Message]:
        url = f'{self.BASE_URL}/@{username}'
        response = await self.scrape_thread(url)
        time_now = int(time.time())
        max_timestamp = 0
        for thread in response['threads']:
            # msg = 'Debug ' + str(thread) + ' - timenow: ' + str(time_now) + ' - published_on: ' + str(thread['published_on']) + ' - map_timestamp: '
            # if username in self.map_last_timestamp:
            #     msg += str(self.map_last_timestamp[username])
            # else:
            #     msg += "None"
            # self.logger.info(msg)
            if time_now - thread['published_on'] > self.config.THREADS_SLA:
                continue
            if username in self.map_last_timestamp and thread['published_on'] <= self.map_last_timestamp[username]:
                continue
            max_timestamp = max(max_timestamp, thread['published_on'])
            url = f"{thread['url']}?sort_order=recent"
            body=f"{thread['text']}\n[Link: {url}]({url})"
            chat_id = self.config.TELEGRAM_NEWS_PEER_ID
            if is_command_trade(thread['text']):
                chat_id = self.config.TELEGRAM_TRADE_PEER_ID
                body += f"\n\n`/freplies {url}`"
            message = Message(
                body = body,
                title = f"Threads - {username} - Time: {datetime.fromtimestamp(thread['published_on'], tz=pytz.timezone('Asia/Ho_Chi_Minh'))}",
                image=thread['images'],
                chat_id=chat_id
            )
            self.logger.info(message, notification=True)
        if max_timestamp > 0:
            self.map_last_timestamp[username] = max_timestamp
    
    async def scrape_user_posts(self):
        if self.config.THREADS_ENABLED == False:
            return
        list_username = self.config.THREADS_LIST_USERNAME
        # self.logger.info(Message(f"Threads.scrape_user_posts with list username: {', '.join(list_username)}"))
        self.log_resources("Before scraping")
        await asyncio.gather(*(self.retrieve_user_posts(u) for u in list_username))
        self.log_resources("After scraping all users")
