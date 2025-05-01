from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = ""
api_hash = ""
phone = ""
with TelegramClient(StringSession(), api_id, api_hash).start(phone=phone) as client:
    print('\n\nBelow is your session string ⬇️\n\n')
    print(client.session.save())
    print('\nAbove is your session string ⬆️\n\n')