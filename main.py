from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ I'm alive! The bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# بيانات تسجيل الدخول
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

# 🧽 تنظيف النص
def remove_links(text):
    return re.sub(r'http\S+|www\S+|t\.me\S+|bit\.ly\S+', '', text).strip().lower()

# 🔍 استخراج معرف الوسائط
def get_media_id(msg):
    if isinstance(msg.media, MessageMediaPhoto):
        return f"photo_{msg.media.photo.id}"
    elif isinstance(msg.media, MessageMediaDocument):
        return f"doc_{msg.media.document.id}"
    return None

# 🧹 دالة حذف التكرار من القناة
async def delete_duplicates_in_channel(new_msg):
    target_channel = 'imamhussains'
    clean_text = remove_links(new_msg.message or "")
    media_id = get_media_id(new_msg)

    async for msg in client.iter_messages(target_channel, limit=100):
        if msg.id == new_msg.id:
            continue
        old_text = remove_links(msg.message or "")
        old_media_id = get_media_id(msg)

        if (clean_text and clean_text == old_text) or (media_id and media_id == old_media_id):
            await msg.delete()
            print(f"🗑 حذف مكرر (ID: {msg.id})")

channels = ['SabrenNews22', 'MydoctorA96', 'kararhassan']

@client.on(events.NewMessage(chats=channels))
async def handler(event):
    msg = event.message
    text = msg.message or ""
    clean_caption = remove_links(text)

    if msg.media:
        sent = await client.send_file('imamhussains', file=msg.media, caption=clean_caption or None)
    elif clean_caption:
        sent = await client.send_message('imamhussains', clean_caption)

    await delete_duplicates_in_channel(sent)

@client.on(events.MessageEdited(chats=channels))
async def edited_handler(event):
    msg = event.message
    text = msg.message or ""
    clean_caption = remove_links(text)

    if msg.media:
        sent = await client.send_file('imamhussains', file=msg.media, caption=clean_caption or None)
    elif clean_caption:
        sent = await client.send_message('imamhussains', clean_caption)

    await delete_duplicates_in_channel(sent)

keep_alive()
print("✅ البوت يعمل الآن ويراقب القنوات المحددة ويحذف التكرارات...")
client.run_until_disconnected()