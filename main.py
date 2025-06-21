from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import re

from flask import Flask
from threading import Thread

# إعداد سيرفر Flask ليبقى البوت شغال 24/7
app = Flask('')

@app.route('/')
def home():
    return "✅ I'm alive! The bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# بيانات تسجيل الدخول مباشرة في الكود
api_id = 24472149
api_hash = 'df7d7fa5c8d628b9bf822ef793598747'
phone = '+9647810424454'

client = TelegramClient('user_session', api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(phone)
    code = input("📩 أدخل كود التحقق من Telegram: ")
    try:
        client.sign_in(phone, code)
    except SessionPasswordNeededError:
        password = input("🔐 الحساب محمي بكلمة مرور، أدخلها: ")
        client.sign_in(password=password)

def remove_links(text):
    return re.sub(r'http\S+|www\S+|t\.me\S+|bit\.ly\S+', '', text).strip()

channels = ['SabrenNews22', 'MydoctorA96', 'kararhassan']

@client.on(events.NewMessage(chats=channels))
async def handler(event):
    msg = event.message
    text = msg.message or ""
    clean_caption = remove_links(text)

    if msg.media:
        await client.send_file(
            'imamhussains',
            file=msg.media,
            caption=clean_caption if clean_caption else None
        )
    elif clean_caption:
        await client.send_message('imamhussains', clean_caption)
@client.on(events.MessageEdited(chats=channels))
async def edited_handler(event):
    msg = event.message
    text = msg.message or ""
    clean_caption = remove_links(text)

    if msg.media:
        await client.send_file(
            'imamhussains',
            file=msg.media,
            caption=clean_caption if clean_caption else None
        )
    elif clean_caption:
        await client.send_message('imamhussains', clean_caption)
        
keep_alive()

print("✅ البوت يعمل الآن ويراقب القنوات المحددة...")
client.run_until_disconnected()