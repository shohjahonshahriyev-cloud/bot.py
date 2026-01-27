# Telegram bot - Excel qidiruv tizimi
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
from excel_handler import ExcelHandler
from database import Database
from config import BOT_TOKEN, ADMIN_ID, EXCEL_FILES_DIR

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot obyektlari
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Global obyektlar
excel_handler = ExcelHandler()
db = Database()

# Admin klaviaturasi
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📁 Fayllar")],
        [KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="🔙 Orqaga")]
    ],
    resize_keyboard=True
)

# Asosiy klaviatura
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 ID bilan qidirish")],
        [KeyboardButton(text="ℹ️ Yordam")]
    ],
    resize_keyboard=True
)

class TelegramBot:
    """Asosiy bot klassi"""
    
    def is_admin(user_id: int) -> bool:
        """Foydalanuvchi admin ekanligini tekshirish"""
        return user_id == ADMIN_ID

@dp.message(Command("start"))
async def start_command(message: Message):
    """Botni ishga tushurish komandasi"""
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Foydalanuvchini bazaga qo'shish
    db.add_user(user_id, username, full_name)
    db.update_user_activity(user_id)
    
    if TelegramBot.is_admin(user_id):
        await message.answer(
            "👨‍💻 **Admin paneliga xush kelibsiz!**\n\n"
            "🤖 Excel qidiruv boti admin interfeysi\n\n"
            "📋 Admin imkoniyatlari:\n"
            "• 📊 Statistika ko'rish\n"
            "• 📁 Excel fayl yuklash\n"
            "• 📢 Foydalanuvchilarga xabar yuborish\n\n"
            "📄 Excel fayl yuklash uchun faylni to'g'ridan-to'g'ri yuboring!",
            reply_markup=admin_keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.answer(
            "🤖 **Excel qidiruv botiga xush kelibsiz!**\n\n"
            "Men Excel fayllaridan ID orqali ma'lumotlarni topishim mumkin.\n\n"
            "📋 Qo'llanma:\n"
            "• 6 xonali ID raqamini yuboring\n"
            "• Bot siz yuborgan ID bo'yicha ma'lumot topadi\n\n"
            "🔍 **Iltimos, 6 xonali ID raqamingizni yuboring!**",
            reply_markup=main_keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Yordam komandasi"""
    user_id = message.from_user.id
    
    if TelegramBot.is_admin(user_id):
        help_text = """
📚 **Admin qo'llanmasi:**

1️⃣ **Fayl yuklash:**
   - Excel (.xlsx) faylni yuboring
   - Fayllar bazaga saqlanadi

2️⃣ **Fayllarni boshqarish:**
   - 📁 Fayllar - Barcha fayllarni ko'rish
   - 📊 Statistika - Bot statistikasi

3️⃣ **Foydalanuvchi so'rovlari:**
   - Foydalanuvchilar ID orqali qidiradi
   - Siz yuklagan fayllarda qidiriladi

4️⃣ **Xavfsizlik:**
   - Faqat admin fayl yuklay oladi
   - Foydalanuvchilar faqat qidirishi mumkin
        """
    else:
        help_text = """
📚 **Botdan foydalanish qo'llanmasi:**

1️⃣ **ID bilan qidirish:**
   - Qidirish uchun 6 xonali ID raqamini yuboring
   - Bot admin yuklagan Excel fayllarda qidiradi

2️⃣ **Natijalar:**
   - Topilgan ma'lumotlar chiroyli formatda ko'rsatiladi
   - Agar ma'lumot topilmasa, xabar beriladi

3️⃣ **Qo'llab-quvvatlanadigan format:**
   • Excel (.xlsx)

❓ Savollaringiz bo'lsa, admin ga murojaat qiling!
        """
    
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(F.document)
async def handle_document(message: Message):
    """Faylni qabul qilish va saqlash (faqat admin uchun)"""
    try:
        user_id = message.from_user.id
        
        # Faqat admin fayl yuklay oladi
        if not TelegramBot.is_admin(user_id):
            await message.answer(
                "❌ Siz fayl yuklay olmaysiz!\n"
                "📋 Faqat admin fayl yuklay oladi.\n"
                "🔍 ID orqali qidirish uchun raqam yuboring."
            )
            return
        
        document = message.document
        if not document:
            await message.answer("❌ Fayl topilmadi!")
            return
        
        # Fayl nomini olish
        file_name = document.file_name
        if not file_name:
            file_name = f"document_{document.file_id}.xlsx"
        
        # Faqat .xlsx formatini qabul qilish
        if not file_name.endswith('.xlsx'):
            await message.answer(
                "❌ Faqat Excel (.xlsx) fayllar qabul qilinadi!\n"
                "📋 Iltimos, to'g'ri formatdagi fayl yuboring."
            )
            return
        
        # Faylni yuklab olish
        file_info = await bot.get_file(document.file_id)
        
        # Faylni saqlash
        os.makedirs(EXCEL_FILES_DIR, exist_ok=True)
        file_path = os.path.join(EXCEL_FILES_DIR, file_name)
        
        await bot.download_file(file_info.file_path, file_path)
        
        # Excel handler ga faylni qo'shish
        if excel_handler.add_excel_file(file_path):
            # Statistikani yangilash
            db.update_files_count(len(excel_handler.get_file_list()))
            
            await message.answer(
                f"✅ Excel fayli muvaffaqiyatli yuklandi: {file_name}\n"
                f"📁 Saqlandi: {EXCEL_FILES_DIR}\n"
                f"🔍 Endi barcha foydalanuvchilar qidirishi mumkin!"
            )
        else:
            await message.answer(
                "❌ Faylni qo'shishda xatolik yuz berdi!\n"
                "🔄 Qaytadan urinib ko'ring."
            )
        
    except Exception as e:
        logger.error(f"Faylni yuklashda xatolik: {e}")
        await message.answer(
            f"❌ Faylni yuklashda xatolik yuz berdi: {str(e)}\n"
            "🔄 Qaytadan urinib ko'ring."
        )

@dp.message(F.text)
async def handle_message(message: Message):
    """Xabarlarni qabul qilish (ID qidirish va admin tugmalari)"""
    try:
        user_id = message.from_user.id
        message_text = message.text.strip()
        
        # Foydalanuvchi faoliyatini yangilash
        db.update_user_activity(user_id)
        
        # Admin tugmalari
        if TelegramBot.is_admin(user_id):
            if message_text == "📊 Statistika":
                await show_stats(message)
                return
            elif message_text == "📁 Fayllar":
                await list_files(message)
                return
            elif message_text == "📢 Xabar yuborish":
                await message.answer(
                    "📢 **Xabar yuborish**\n\n"
                    "Yubormoqchi bo'lgan xabaringizni yozing.\n"
                    "Xabar barcha foydalanuvchilarga yuboriladi.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            elif message_text == "🔙 Orqaga":
                await start_command(message)
                return
        
        # Oddiy foydalanuvchi tugmalari
        if message_text == "🔍 ID bilan qidirish":
            await message.answer(
                "🔍 **ID qidirish**\n\n"
                "Iltimos, 6 xonali ID raqamingizni yuboring:\n"
                "Masalan: 123456",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        elif message_text == "ℹ️ Yordam":
            await help_command(message)
            return
        
        # ID qidirish (faqat raqamlar uchun)
        if message_text.isdigit():
            # ID validation
            if len(message_text) != 6:
                await message.answer(
                    "❌ ID 6 xonali raqam bo'lishi kerak!\n\n"
                    "📋 Masalan: 123456\n"
                    "🔄 Qaytadan urinib ko'ring.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Qidiruvni amalga oshirish
            await search_by_id(message, message_text)
        else:
            # Broadcast xabar (admin uchun)
            if TelegramBot.is_admin(user_id):
                await broadcast_message(message, message_text)
            else:
                await message.answer(
                    "❌ Noto'g'ri format!\n\n"
                    "📋 Iltimos, 6 xonali ID raqamini yuboring\n"
                    "yoki tugmalardan foydalaning.",
                    parse_mode=ParseMode.MARKDOWN
                )
                
    except Exception as e:
        logger.error(f"Xabarni qayta ishlashda xatolik: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring.",
            parse_mode=ParseMode.MARKDOWN
        )

async def search_by_id(message: Message, user_id: str):
    """ID bo'yicha qidiruv"""
    try:
        # Excel fayllarida qidirish
        result = excel_handler.search_by_id(user_id)
        
        # Qidiruv statistikasini yangilash
        db.increment_search_count(message.from_user.id)
        
        if result:
            # Hafta kunini va sanasini olish
            today = datetime.now()
            week_days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
            week_day = week_days[today.weekday()]
            date_str = today.strftime('%d.%m.%Y')
            
            # Natijani formatlash
            response_text = f"📅 **HAFTA KUNI:** {week_day.upper()}\n"
            response_text += f"🗓 **SANASI:** {date_str}\n"
            response_text += f"🔢 **ID:** {result['ID']}\n\n"
            response_text += f"👤 **ISM:** {result['Ism']}\n"
            response_text += f"👥 **FAMILIYA:** {result['Familiya']}\n"
            response_text += f"📚 **FAN:** {result['Fan']}\n"
            response_text += f"📅 **SANA:** {result['Sana']}\n"
            response_text += f"🏫 **XONA:** {result['Xona']}\n"
            response_text += f"📄 **MANBA:** {result['source_file']}"
            
            await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.answer(
                f"❌ **ID: {user_id}** bo'yicha ma'lumot topilmadi.\n\n"
                "🔍 Boshqa ID bilan urinib ko'ring.",
                parse_mode=ParseMode.MARKDOWN
            )
            
    except Exception as e:
        logger.error(f"Qidiruvda xatolik: {e}")
        await message.answer(
            "❌ Qidiruvda xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring.",
            parse_mode=ParseMode.MARKDOWN
        )

async def list_files(message: Message):
    """Admin fayllar ro'yxatini ko'rsatish"""
    if not TelegramBot.is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    files = excel_handler.get_file_list()
    
    if not files:
        await message.answer("📭 Excel fayllari yo'q.")
        return
    
    response_text = "📁 **Excel fayllari:**\n\n"
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(EXCEL_FILES_DIR, filename)
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        response_text += f"{i}. 📄 {filename}\n"
        response_text += f"   📊 Hajmi: {file_size_mb:.2f} MB\n\n"
    
    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)

async def show_stats(message: Message):
    """Statistikani ko'rsatish"""
    if not TelegramBot.is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    # Statistikani olish
    stats = db.get_stats()
    excel_stats = excel_handler.get_stats()
    daily_stats = db.get_daily_stats(7)
    
    stats_text = f"""
📊 **Bot statistikasi:**

👥 **Umumiy foydalanuvchilar:** {stats['total_users']} ta
🔍 **Jami qidiruvlar:** {stats['total_searches']} ta
📁 **Excel fayllar:** {excel_stats['files_count']} ta
📊 **Jami yozuvlar:** {excel_stats['total_records']} ta

📈 **Oxirgi 7 kun:**
"""
    
    for date, count in daily_stats.items():
        stats_text += f"• {date}: {count} ta qidiruv\n"
    
    await message.answer(stats_text, parse_mode=ParseMode.MARKDOWN)

async def broadcast_message(message: Message, text: str):
    """Barcha foydalanuvchilarga xabar yuborish"""
    if not TelegramBot.is_admin(message.from_user.id):
        return
    
    users = db.get_all_users()
    success_count = 0
    error_count = 0
    
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
            success_count += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik (user {user_id}): {e}")
            error_count += 1
    
    await message.answer(
        f"📢 **Xabar yuborish natijalari:**\n\n"
        f"✅ Muvaffaqiyatli: {success_count} ta\n"
        f"❌ Xatolik: {error_count} ta\n"
        f"📊 Jami: {len(users)} ta foydalanuvchi",
        parse_mode=ParseMode.MARKDOWN
    )

async def main():
    """Botni ishga tushirish"""
    print("🤖 Excel qidiruv boti ishga tushmoqda...")
    print(f"👨‍💻 Admin ID: {ADMIN_ID}")
    print(f"📁 Excel fayllar papkasi: {EXCEL_FILES_DIR}")
    
    # Excel fayllarini yuklash
    excel_handler.load_existing_files()
    print(f"📊 Yuklangan Excel fayllar: {len(excel_handler.get_file_list())} ta")
    
    # Botni ishga tushurish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
