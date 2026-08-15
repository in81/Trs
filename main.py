import streamlit as st
from telethon import TelegramClient, events
import threading
import asyncio

st.title("🤖 Smart Telegram Sync Bot (Active)")
st.write("البوت يعمل بذكاء وبشكل آمن لتنسيق، أرشفة، وتحديث الرسائل.")

# --- بياناتك الشخصية ومعرفات القنوات ---
API_ID = 32513200
API_HASH = '62ca0b406077222bc109b1f7dd6e4fc6'

SOURCE_ID = -1002227529341   # آيدي القناة المصدر
TARGET_ID = -1004327420602   # آيدي قناتك الخاصة

# قاموس لربط رسائل المصدر بالهدف لتحديثها عند التعديل لاحقاً
message_map = {}

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient('session', API_ID, API_HASH)

    async def main():
        print("جاري الاتصال وسحب الأرشيف القديم بترتيب زمني صحيح...")
        
        # سحب الأرشيف كاملاً من البداية إلى النهاية (reverse=True تعني من الأقدم للأحدث)
        async for message in client.iter_messages(SOURCE_ID, reverse=True):
            try:
                if message.text and not message.media:
                    sent = await client.send_message(TARGET_ID, message.text)
                    message_map[message.id] = sent.id
                elif message.media:
                    sent = await client.send_file(TARGET_ID, message.media, caption=message.text or "")
                    message_map[message.id] = sent.id
                
                # فاصل زمني آمن جداً (3 ثوانٍ) لمنع أي حظر أو ضغط على الحساب
                await asyncio.sleep(3)
            except Exception as e:
                print(f"خطأ في سحب رسالة أرشيفية: {e}")

        print("انتهى سحب الأرشيف بنجاح، وبدء الاستماع الفوري للرسائل الجديدة والتعديلات...")

        # الاستماع للرسائل الجديدة فور نزولها
        @client.on(events.NewMessage(chats=SOURCE_ID))
        async def new_msg_handler(event):
            try:
                msg = event.message
                if msg.text and not msg.media:
                    sent = await client.send_message(TARGET_ID, msg.text)
                    message_map[msg.id] = sent.id
                elif msg.media:
                    sent = await client.send_file(TARGET_ID, msg.media, caption=msg.text or "")
                    message_map[msg.id] = sent.id
                
                # تأخير بسيط وآمن للرسائل الجديدة
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"خطأ في إرسال رسالة جديدة: {e}")

        # الاستماع لتعديلات الرسائل وتطبيقها فوراً في قناتك
        @client.on(events.MessageEdited(chats=SOURCE_ID))
        async def edit_msg_handler(event):
            try:
                msg = event.message
                if msg.id in message_map:
                    target_msg_id = message_map[msg.id]
                    await client.edit_message(TARGET_ID, target_msg_id, text=msg.text or "")
            except Exception as e:
                print(f"خطأ في تحديث رسالة معدلة: {e}")

    client.loop.run_until_complete(main())
    client.run_until_disconnected()

if 'bot_started' not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
