# Oddiy test bot
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Konfiguratsiya
BOT_TOKEN = "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"
ADMIN_ID = 422057508

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot obyektlari
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start komandasi"""
    try:
        user_id = message.from_user.id
        
        if user_id == ADMIN_ID:
            await message.answer("👨‍💻 Admin paneliga xush kelibsiz!")
        else:
            await message.answer("🤖 Oddiy foydalanuvchi paneliga xush kelibsiz!")
            
        logger.info(f"Start komandasi ishladi - User ID: {user_id}")
        
    except Exception as e:
        logger.error(f"Start komandasida xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi!")

@dp.message()
async def echo_handler(message: types.Message):
    """Echo handler"""
    try:
        await message.answer(f"Siz yuborgan xabar: {message.text}")
        logger.info(f"Echo ishladi - User ID: {message.from_user.id}")
    except Exception as e:
        logger.error(f"Echo handler xatolik: {e}")

async def main():
    """Asosiy funksiya"""
    try:
        print("🚀 Test bot ishga tushmoqda...")
        print(f"🤖 Bot ID: {bot.id}")
        print(f"👨‍💻 Admin ID: {ADMIN_ID}")
        
        # Botni ishga tushurish
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Asosiy xatolik: {e}")
