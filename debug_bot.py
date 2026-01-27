# Debug bot - barcha muammolarni topish uchun
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Konfiguratsiya
BOT_TOKEN = "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"
ADMIN_ID = 422057508

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot obyektlari
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Oddiy klaviatura
test_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Test 1")],
        [KeyboardButton(text="ℹ️ Test 2")],
        [KeyboardButton(text="🔙 Test 3")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start komandasi"""
    try:
        user_id = message.from_user.id
        print(f"Start bosildi - User ID: {user_id}")
        
        await message.answer(
            "🤖 Test botiga xush kelibsiz!\n\n"
            "Tugmalardan birini bosing:",
            reply_markup=test_keyboard
        )
        
    except Exception as e:
        print(f"Start xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi!")

@dp.message()
async def handle_message(message: types.Message):
    """Xabar handler"""
    try:
        user_id = message.from_user.id
        text = message.text
        print(f"Xabar keldi - User: {user_id}, Text: {text}")
        
        if text == "🔍 Test 1":
            await message.answer("✅ Test 1 ishladi!")
        elif text == "ℹ️ Test 2":
            await message.answer("✅ Test 2 ishladi!")
        elif text == "🔙 Test 3":
            await message.answer("✅ Test 3 ishladi!")
        else:
            await message.answer(f"❌ Noma'lum tugma: {text}")
            
    except Exception as e:
        print(f"Message handler xatolik: {e}")
        await message.answer("❌ Xatolik!")

async def main():
    try:
        print("🚀 Test bot ishga tushmoqda...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot xatolik: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Bot to'xtatildi")
