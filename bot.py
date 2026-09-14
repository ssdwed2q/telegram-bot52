import asyncio
import sqlite3
import logging
import os


from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

BOT_TOKEN = "8673158060:AAGi3V-WY7I-N7sifaDSMrLSWT69Iot6eRk"
CHANNEL_LINK = "https://t.me/+2DZuWdY6qFw5ZmE6"
ADMIN_ID = 420441017
logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ---
db = sqlite3.connect("db.sqlite3")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    source TEXT
)
""")
db.commit()


# --- КНОПКИ ---
def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 الاشتراك في القناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ لقد أرسلت الطلب", callback_data="done")]
    ])


def final_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 تواصل معي", url="https://t.me/Faditr")]
    ])


# --- START ---
@dp.message(CommandStart())
async def start(msg: types.Message):
    args = msg.text.split()
    source = args[1] if len(args) > 1 else "unknown"

    cur.execute("INSERT OR IGNORE INTO users (user_id, source) VALUES (?, ?)",
                (msg.from_user.id, source))
    db.commit()

    caption = (
        "اشتركوا حتمًا في قناتي على تيليجرام، حيث أشارككم إعدادات مجرّبة لروبوت التداول المجاني الخاص بي، "
        "وإشارات الذكاء الاصطناعي، وإعدادات نسخ الصفقات من أفضل المتداولين على المنصة!\n\n"

        "لِتبدؤوا بتحقيق 500 دولار يوميًا والتداول من اليوم، كل ما تحتاجونه هو تخصيص نصف ساعة فقط من وقتكم "
        "الحر لتوصيل وضبط هذه الأدوات المالية المساعدة! وستبدأ بتحقيق الأرباح لكم من الدقائق الأولى مجانًا تمامًا! 😱🔥\n\n"

        "🎁 وبعد الاشتراك مباشرة، سأرسل لكم في رسالة خاصة فيديو يشرح طريقة سرية استخدمتها شخصيًا لبدء تحقيق الأرباح، "
        "وما زالت حتى اليوم تساعد آلاف الأشخاص على تغيير حياتهم! كل ما عليكم هو تكرار الخطوات الموجودة في الفيديو، "
        "والأمر سهل جدًا ويمكن لأي شخص تطبيقه!\n\n"

        "⚡️ أسرعوا، فقناتي تستقبل عددًا محدودًا من المشتركين، وعدد الأماكن يتناقص مع كل ساعة:"
    )

    try:
        photo = FSInputFile("photo.jpg.jpg.jpg")

        await msg.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=sub_kb()
        )
    except:
        await msg.answer(caption, reply_markup=sub_kb())


# --- КНОПКА "Я ОТПРАВИЛ ЗАЯВКУ" ---
@dp.callback_query(F.data == "done")
async def done(call: types.CallbackQuery):
    await call.message.answer(
        "⏳ إذا أرسلت الطلب سيتم قبولك تلقائيًا خلال ثواني\n\n"
        "✉️ بعد الدخول اكتب لي للحصول على التعليمات✉️",
        reply_markup=final_kb()
    )


# --- АВТОПРИНЯТИЕ ЗАЯВОК ---
@dp.chat_join_request()
async def approve(event: types.ChatJoinRequest):
    try:
        await bot.approve_chat_join_request(
            chat_id=event.chat.id,
            user_id=event.from_user.id
        )
    except:
        pass


# --- АДМИН ПАНЕЛЬ ---
@dp.message(F.from_user.id == ADMIN_ID)
async def admin(msg: types.Message):
    # 📊 Статистика
    if msg.text == "/stats":
        total = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        yt1 = cur.execute("SELECT COUNT(*) FROM users WHERE source='yt1'").fetchone()[0]

        await msg.answer(
            f"📊 Статистика:\n\n"
            f"👥 Всего: {total}\n"
            f"🎯 yt1: {yt1}"
        )

    # 👥 Все пользователи
    elif msg.text == "/users":
        users = cur.execute("SELECT user_id FROM users").fetchall()

        text = "👥 Пользователи:\n\n"
        for u in users[:50]:
            text += f"{u[0]}\n"

        await msg.answer(text)

    # 🎯 Только yt1
    elif msg.text == "/yt1":
        users = cur.execute("SELECT user_id FROM users WHERE source='yt1'").fetchall()

        text = "🎯 Пользователи с yt1:\n\n"
        for u in users[:50]:
            text += f"{u[0]}\n"

        await msg.answer(text)

    # 📩 Рассылка
    elif msg.text.startswith("/send "):
        text_to_send = msg.text.replace("/send ", "")
        users = cur.execute("SELECT user_id FROM users").fetchall()

        sent = 0
        for u in users:
            try:
                await bot.send_message(u[0], text_to_send)
                sent += 1
            except:
                pass

        await msg.answer(f"📩 Отправлено: {sent}")


# --- ФОЛБЭК ---
@dp.message()
async def any_msg(msg: types.Message):
    await msg.answer("اضغط /start")


# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



