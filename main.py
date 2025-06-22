from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
from flask import Flask
from threading import Thread
import asyncio

# --- إعداد Flask للحفاظ على البوت حي في Render ---
app = Flask('')

@app.route('/')
def home():
    return "✅ I'm alive! The bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بيانات Telegram API ---
api_id = 24472149
api_hash = 'df7d7fa5c8d628b9bf822ef793598747'
phone = '+9647810424454'

# --- إنشاء عميل Telethon ---
client = TelegramClient('user_session', api_id, api_hash)

# --- دوال مساعدة ---
def remove_links(text):
    return re.sub(r'http\S+|www\S+|t\.me\S+|bit\.ly\S+', '', text).strip().lower()

def get_media_id(msg):
    if isinstance(msg.media, MessageMediaPhoto):
        return f"photo_{msg.media.photo.id}"
    elif isinstance(msg.media, MessageMediaDocument):
        return f"doc_{msg.media.document.id}"
    return None

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

# --- القنوات المصدر ---
channels = ['SabrenNews22', 'MydoctorA96', 'kararhassan']

# --- دالة معالجة الرسائل ---
async def process_message(msg):
    text = msg.message or ""
    clean_caption = remove_links(text)

    if msg.media:
        sent = await client.send_file('imamhussains', file=msg.media, caption=clean_caption or None)
    elif clean_caption:
        sent = await client.send_message('imamhussains', clean_caption)
    else:
        return
    print(f"📤 أُرسلت رسالة من: {msg.chat_id}")
    await delete_duplicates_in_channel(sent)

# --- مراقبة الرسائل الجديدة ---
@client.on(events.NewMessage(chats=channels))
async def handler(event):
    await process_message(event.message)

# --- مراقبة الرسائل المعدلة ---
@client.on(events.MessageEdited(chats=channels))
async def edited_handler(event):
    await process_message(event.message)

# --- تنظيف الرسائل القديمة عند التشغيل ---
async def full_deduplication():
    print("🔍 بدأ فحص الرسائل السابقة...")
    seen_texts = {}
    seen_media = {}

    async for msg in client.iter_messages('imamhussains', reverse=True, limit=1000):
        msg_text = remove_links(msg.message or "")
        media_id = get_media_id(msg)

        if msg_text:
            if msg_text in seen_texts:
                await msg.delete()
                print(f"🗑 حذف رسالة مكررة (نص): {msg.id}")
            else:
                seen_texts[msg_text] = msg.id
        elif media_id:
            if media_id in seen_media:
                await msg.delete()
                print(f"🗑 حذف وسائط مكررة: {msg.id}")
            else:
                seen_media[media_id] = msg.id

    print("✅ انتهى فحص الرسائل القديمة.")

# --- تشغيل البوت وكل شيء ---
async def main():
    try:
        await client.start(phone=phone)
    except SessionPasswordNeededError:
        await client.sign_in(password='KararH@1999@1')  # ← كلمة السر 2FA هنا

    print("✅ البوت شغال ويراقب القنوات المحددة ...")
    await full_deduplication()
    await client.run_until_disconnected()

if __name__ == '__main__':
    keep_alive()  # تشغيل Flask في ثريد منفصل
    asyncio.run(main())