import json
import time
from typing import Dict

import jmespath
from parsel import Selector
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from .logger import Logger
from .config import Config
from .notification import Message
from datetime import datetime
import pytz
import subprocess
import sys
import re

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

        command = [sys.executable, "-m", "playwright", "install", "chromium"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            self.logger.error(Message(title=f"Error installing Playwright - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}', body=f'{stderr.decode('utf-8')}"), True)
        else:
            msg = stdout.decode('utf-8') or 'Successful'
            msg = msg.replace('\u25a0', '')
            msg = remove_redundant_spaces(msg)
            self.logger.info(Message(title=f"Playwright installation successful - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body=msg), False)
    
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
            images: post.carousel_media[].image_versions2.candidates[1].url,
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



    def scrape_profile(self, username: str) -> dict:
        """Scrape Threads profile and their recent posts from a given URL"""
        with sync_playwright() as pw:
            # start Playwright browser
            browser = pw.chromium.launch(chromium_sandbox=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            url = f'{self.BASE_URL}/@{username}'

            page.goto(url)
            # wait for page to finish loading
            # page.wait_for_selector("[data-pressable-container=true]")
            page.wait_for_load_state('load')
            selector = Selector(page.content())
        parsed = {
            "user": {},
            "threads": [],
        }
        # find all hidden datasets
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        for hidden_dataset in hidden_datasets:
            # skip loading datasets that clearly don't contain threads data
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            is_profile = 'follower_count' in hidden_dataset
            is_threads = 'thread_items' in hidden_dataset
            if not is_profile and not is_threads:
                continue
            data = json.loads(hidden_dataset)
            if is_profile:
                user_data = nested_lookup('user', data)
                parsed['user'] = self.parse_profile(user_data[0])
            if is_threads:
                thread_items = nested_lookup('thread_items', data)
                threads = [
                    self.parse_thread(t) for thread in thread_items for t in thread
                ]
                parsed['threads'].extend(threads)
        return parsed

    def retrieve_user_posts(self, username: str) -> list[Message]:
        response = self.scrape_profile(username)
        time_now = int(time.time())
        threads_post = []
        max_timestamp = 0
        for thread in response['threads']:
            if time_now - thread['published_on'] > self.config.THREADS_SLA:
                continue
            if username in self.map_last_timestamp and thread['published_on'] <= self.map_last_timestamp[username]:
                continue
            max_timestamp = max(max_timestamp, thread['published_on'])
            threads_post.append(Message(
                body = f"{thread['text']}\n\n[Link: {thread['url']}]({thread['url']})",
                title = f"Threads - {username} - Time: {datetime.fromtimestamp(thread['published_on'], tz=pytz.timezone('Asia/Ho_Chi_Minh'))}"
            ))
        if max_timestamp > 0:
            self.map_last_timestamp[username] = max_timestamp
        return threads_post
    
    def scrape_user_posts(self):
        if self.config.THREADS_ENABLED == False:
            return
        list_username = self.config.THREADS_LIST_USERNAME
        posts = []
        for username in list_username:
            posts.extend(self.retrieve_user_posts(username))
        for post in posts:
            self.logger.info(post, True)
