import asyncio
import sys

print("Python version:", sys.version)
print("Test boshlanishi...")

try:
    import aiogram
    print("✅ aiogram import ok")
except Exception as e:
    print(f"❌ aiogram error: {e}")
    sys.exit(1)

try:
    from aiogram import Bot
    print("✅ Bot class import ok")
except Exception as e:
    print(f"❌ Bot class error: {e}")
    sys.exit(1)

# Token
TOKEN = "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"

async def test():
    try:
        print("Bot yaratilmoqda...")
        bot = Bot(token=TOKEN)
        print("✅ Bot yaratildi")
        
        print("Bot ma'lumotlari olinmoqda...")
        info = await bot.get_me()
        print(f"✅ Bot info: {info.username}")
        
        print("Bot to'g'ri ishlaydi!")
        
    except Exception as e:
        print(f"❌ Bot xatolik: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test())
    except Exception as e:
        print(f"❌ Async xatolik: {e}")
        import traceback
        traceback.print_exc()
