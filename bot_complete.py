# TO'LIQ TELEGRAM BOT - BARCHA KOD BIR FAYLDA
import asyncio
import logging
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

# =================================================================
# KONFIGURATSIYA
# =================================================================

# Bot tokeni (BotFather'dan olingan)
BOT_TOKEN = "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"  # Bu yerga o'zingizning bot tokeningizni kiriting

# Admin ID (o'zingizning Telegram ID'ingiz)
ADMIN_ID = 422057508  # Bu yerga o'zingizning Telegram ID'ingizni kiriting

# Papka yo'llari
EXCEL_FILES_DIR = "data/excel_files"
LOGS_DIR = "logs"

# Fayl nomlari
USERS_DB = "data/users.json"
STATS_FILE = "data/stats.json"

# Bot sozlamalari
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_FILE_TYPES = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]  # .xlsx

# Excel ustun nomlari
EXCEL_COLUMNS = ["ID", "Ism", "Familiya", "Fan", "Sana", "Xona"]

# =================================================================
# LOGGING SOZLAMALARI
# =================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =================================================================
# EXCEL HANDLER KLASI
# =================================================================

class ExcelHandler:
    """Excel fayllar bilan ishlash uchun klass"""
    
    def __init__(self):
        self.excel_files = []
        self.cached_data = {}
        self.load_existing_files()
    
    def load_existing_files(self):
        """Mavjud Excel fayllarini yuklash"""
        if not os.path.exists(EXCEL_FILES_DIR):
            os.makedirs(EXCEL_FILES_DIR)
            return
        
        for file in os.listdir(EXCEL_FILES_DIR):
            if file.endswith('.xlsx'):
                self.excel_files.append(file)
                self.cache_excel_data(file)
    
    def cache_excel_data(self, filename: str):
        """Excel fayl ma'lumotlarini keshga yuklash"""
        try:
            file_path = os.path.join(EXCEL_FILES_DIR, filename)
            df = pd.read_excel(file_path)
            
            # ID ustunini string formatiga o'tkazish
            if 'Talaba ID' in df.columns:
                df['Talaba ID'] = df['Talaba ID'].astype(str)
            elif 'ID' in df.columns:
                df['ID'] = df['ID'].astype(str)
            
            self.cached_data[filename] = df
            print(f"✅ {filename} fayli keshlandi")
        except Exception as e:
            print(f"❌ {filename} faylini keshlashda xatolik: {e}")
    
    def add_excel_file(self, file_path: str) -> bool:
        """Yangi Excel fayl qo'shish"""
        try:
            filename = os.path.basename(file_path)
            
            # Faylni tekshirish
            if not filename.endswith('.xlsx'):
                return False
            
            # Fayl papkaga ko'chirish
            destination = os.path.join(EXCEL_FILES_DIR, filename)
            import shutil
            shutil.move(file_path, destination)
            
            # Fayl ro'yxatiga qo'shish
            if filename not in self.excel_files:
                self.excel_files.append(filename)
            
            # Keshlash
            self.cache_excel_data(filename)
            
            return True
        except Exception as e:
            print(f"❌ Excel faylni qo'shishda xatolik: {e}")
            return False
    
    def search_by_id(self, user_id: str) -> dict:
        """Barcha Excel fayllaridan ID bo'yicha qidiruv"""
        user_id = str(user_id).zfill(6)  # 6 xonali qilish
        
        for filename, df in self.cached_data.items():
            # Avval 'Talaba ID' ustunini qidiramiz
            if 'Talaba ID' in df.columns:
                result = df[df['Talaba ID'] == user_id]
                if not result.empty:
                    row = result.iloc[0]
                    return {
                        'ID': str(row.get('Talaba ID', '')),
                        'Ism': str(row.get('Talaba F.I', '')),
                        'Familiya': str(row.get('Talaba F.I.1', '')),
                        'Fan': str(row.get('Fan nomi', '')),
                        'Sana': str(row.get('Nazorat sanasi', '')) if pd.notna(row.get('Nazorat sanasi', '')) else 'Noma\'lum',
                        'Xona': str(row.get('Nazorat xonasi', '')),
                        'Nazorat kuni': str(row.get('Nazorat kuni', '')),
                        'Nazorat boshlanish vaqti': str(row.get('Nazorat boshlanish vaqti', '')),
                        'Nazorat tugash vaqti': str(row.get('Nazorat tugash vaqti', '')),
                        'Fan kodi': str(row.get('Fan kodi', '')),
                        'Bino nomi': str(row.get('Bino nomi', '')),
                        'source_file': filename
                    }
            # Keyin 'ID' ustunini qidiramiz
            elif 'ID' in df.columns:
                result = df[df['ID'] == user_id]
                if not result.empty:
                    row = result.iloc[0]
                    return {
                        'ID': str(row.get('ID', '')),
                        'Ism': str(row.get('Ism', '')),
                        'Familiya': str(row.get('Familiya', '')),
                        'Fan': str(row.get('Fan', '')),
                        'Sana': str(row.get('Sana', '')),
                        'Xona': str(row.get('Xona', '')),
                        'source_file': filename
                    }
        
        return None
    
    def get_file_list(self) -> list:
        """Excel fayllar ro'yxatini olish"""
        return self.excel_files.copy()
    
    def remove_file(self, filename: str) -> bool:
        """Excel faylni o'chirish"""
        try:
            if filename in self.excel_files:
                self.excel_files.remove(filename)
            
            if filename in self.cached_data:
                del self.cached_data[filename]
            
            file_path = os.path.join(EXCEL_FILES_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"❌ Faylni o'chirishda xatolik: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Statistika olish"""
        total_records = 0
        for df in self.cached_data.values():
            total_records += len(df)
        
        return {
            'files_count': len(self.excel_files),
            'total_records': total_records,
            'files': self.excel_files
        }

# =================================================================
# DATABASE KLASI
# =================================================================

class Database:
    """Foydalanuvchilar va statistika ma'lumotlarini saqlash uchun klass"""
    
    def __init__(self):
        self.users = {}
        self.stats = {
            'total_users': 0,
            'total_searches': 0,
            'total_files': 0,
            'daily_searches': {},
            'user_activity': {}
        }
        self.load_data()
    
    def load_data(self):
        """Ma'lumotlarni fayldan yuklash"""
        try:
            # Foydalanuvchilar ma'lumotlari
            if os.path.exists(USERS_DB):
                with open(USERS_DB, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            
            # Statistika ma'lumotlari
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
        except Exception as e:
            print(f"❌ Ma'lumotlarni yuklashda xatolik: {e}")
    
    def save_data(self):
        """Ma'lumotlarni faylga saqlash"""
        try:
            # Papkalar yaratish
            os.makedirs(os.path.dirname(USERS_DB), exist_ok=True)
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            
            # Foydalanuvchilar ma'lumotlari
            with open(USERS_DB, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            # Statistika ma'lumotlari
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ma'lumotlarni saqlashda xatolik: {e}")
    
    def add_user(self, user_id: int, username: str = None, full_name: str = None):
        """Yangi foydalanuvchi qo'shish"""
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                'username': username,
                'full_name': full_name,
                'joined_date': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'search_count': 0
            }
            self.stats['total_users'] = len(self.users)
            self.save_data()
    
    def update_user_activity(self, user_id: int):
        """Foydalanuvchi faoliyatini yangilash"""
        if str(user_id) in self.users:
            self.users[str(user_id)]['last_active'] = datetime.now().isoformat()
            self.save_data()
    
    def increment_search_count(self, user_id: int):
        """Qidiruv sonini oshirish"""
        if str(user_id) in self.users:
            self.users[str(user_id)]['search_count'] += 1
        
        # Umumiy statistikani yangilash
        self.stats['total_searches'] += 1
        
        # Kunlik statistika
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_searches']:
            self.stats['daily_searches'][today] = 0
        self.stats['daily_searches'][today] += 1
        
        self.save_data()
    
    def get_all_users(self) -> list:
        """Barcha foydalanuvchi IDlarini olish"""
        return [int(uid) for uid in self.users.keys()]
    
    def get_user_info(self, user_id: int) -> dict:
        """Foydalanuvchi ma'lumotlarini olish"""
        return self.users.get(str(user_id))
    
    def update_files_count(self, count: int):
        """Fayllar sonini yangilash"""
        self.stats['total_files'] = count
        self.save_data()
    
    def get_stats(self) -> dict:
        """Statistikani olish"""
        return self.stats.copy()
    
    def get_daily_stats(self, days: int = 7) -> dict:
        """Oxirgi kunlar statistikasi"""
        daily_stats = {}
        end_date = datetime.now()
        
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats[date] = self.stats['daily_searches'].get(date, 0)
        
        return daily_stats

# =================================================================
# BOT OBYEKTLARI VA KLAVIATURALAR
# =================================================================

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

# =================================================================
# BOT KLASI
# =================================================================

class TelegramBot:
    """Asosiy bot klassi"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Foydalanuvchi admin ekanligini tekshirish"""
        return user_id == ADMIN_ID

# =================================================================
# HANDLER FUNKSIYALARI
# =================================================================

@dp.message(Command("start"))
async def start_command(message: Message):
    """Botni ishga tushurish komandasi"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name
        
        # Foydalanuvchini bazaga qo'shish
        db.add_user(user_id, username, full_name)
        db.update_user_activity(user_id)
        
        if TelegramBot.is_admin(user_id):
            await message.answer(
                "👨‍💻 Admin paneliga xush kelibsiz!\n\n"
                "🤖 Excel qidiruv boti admin interfeysi\n\n"
                "📋 Admin imkoniyatlari:\n"
                "• 📊 Statistika ko'rish\n"
                "• 📁 Excel fayl yuklash\n"
                "• 📢 Foydalanuvchilarga xabar yuborish\n\n"
                "📄 Excel fayl yuklash uchun faylni to'g'ridan-to'g'ri yuboring!\n\n"
                "👨‍💻 Admin @shohjahon_o5",
                reply_markup=admin_keyboard
            )
        else:
            await message.answer(
                "🤖 SAMDAQU qidiruv botiga xush kelibsiz!\n\n"
                "Men Excel fayllaridan ID orqali ma'lumotlarni topishim mumkin.\n\n"
                "📋 Qo'llanma:\n"
                "• 6 xonali ID raqamini yuboring\n"
                "• Bot siz yuborgan ID bo'yicha ma'lumot topadi\n\n"
                "🔍 Iltimos, 6 xonali ID raqamingizni yuboring!\n\n"
                "👨‍💻 Admin @shohjahon_o5",
                reply_markup=main_keyboard
            )
            
    except Exception as e:
        logger.error(f"Start komandasida xatolik: {e}")
        await message.answer(
            "❌ Botni ishga tushirishda xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring.\n\n"
            "👨‍💻 Admin @shohjahon_o5",
            parse_mode=ParseMode.MARKDOWN
        )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Yordam komandasi"""
    try:
        user_id = message.from_user.id
        
        if TelegramBot.is_admin(user_id):
            help_text = (
                "📚 Admin qo'llanmasi:\n\n"
                "1️⃣ Fayl yuklash:\n"
                "   - Excel (.xlsx) faylni yuboring\n"
                "   - Fayllar bazaga saqlanadi\n\n"
                "2️⃣ Fayllarni boshqarish:\n"
                "   - 📁 Fayllar - Barcha fayllarni ko'rish\n"
                "   - 📊 Statistika - Bot statistikasi\n\n"
                "3️⃣ Foydalanuvchi so'rovlari:\n"
                "   - Foydalanuvchilar ID orqali qidiradi\n"
                "   - Siz yuklagan fayllarda qidiriladi\n\n"
                "4️⃣ Xavfsizlik:\n"
                "   - Faqat admin fayl yuklay oladi\n"
                "   - Foydalanuvchilar faqat qidirishi mumkin\n\n"
                "👨‍💻 Admin @shohjahon_o5"
            )
        else:
            help_text = (
                "📚 Botdan foydalanish qo'llanmasi:\n\n"
                "1️⃣ ID bilan qidirish:\n"
                "   - Qidirish uchun 6 xonali ID raqamini yuboring\n"
                "   - Bot admin yuklagan Excel fayllarda qidiradi\n\n"
                "2️⃣ Natijalar:\n"
                "   - Topilgan ma'lumotlar chiroyli formatda ko'rsatiladi\n"
                "   - Agar ma'lumot topilmasa, xabar beriladi\n\n"
                "3️⃣ Qo'llab-quvvatlanadigan format:\n"
                "   • Excel (.xlsx)\n\n"
                "❓ Savollaringiz bo'lsa, admin ga murojaat qiling!\n\n"
                "👨‍💻 Admin @shohjahon_o5"
            )
        
        await message.answer(help_text)
        
    except Exception as e:
        logger.error(f"Help command xatolik: {e}")
        await message.answer(
            "❌ Yordam ko'rsatishda xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring.\n\n"
            "👨‍💻 Admin @shohjahon_o5"
        )

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
                "🔍 ID orqali qidirish uchun raqam yuboring.\n\n"
                "👨‍💻 Admin @shohjahon_o5"
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

@dp.message(F.text & ~F.command)
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
                    "📢 Xabar yuborish\n\n"
                    "Yubormoqchi bo'lgan xabaringizni yozing.\n"
                    "Xabar barcha foydalanuvchilarga yuboriladi."
                )
                return
            elif message_text == "🔙 Orqaga":
                try:
                    await start_command(message)
                except Exception as e:
                    logger.error(f"Orqaga tugmasi xatolik: {e}")
                    await message.answer(
                        "❌ Asosiy menuga qaytishda xatolik!\n"
                        "🔄 Qaytadan urinib ko'ring.\n\n"
                        "👨‍💻 Admin @shohjahon_o5"
                    )
                return
        
        # Oddiy foydalanuvchi tugmalari
        if message_text == "🔍 ID bilan qidirish":
            await message.answer(
                "🔍 ID qidirish\n\n"
                "Iltimos, 6 xonali ID raqamingizni yuboring:\n"
                "Masalan: 123456"
            )
            return
        elif message_text == "ℹ️ Yordam":
            try:
                await help_command(message)
            except Exception as e:
                logger.error(f"Yordam komandasida xatolik: {e}")
                await message.answer(
                    "❌ Yordam ko'rsatishda xatolik yuz berdi!\n"
                    "🔄 Qaytadan urinib ko'ring.\n\n"
                    "👨‍💻 Admin @shohjahon_o5"
                )
            return
        
        # ID qidirish (faqat raqamlar uchun)
        if message_text.isdigit():
            # ID validation
            if len(message_text) != 6:
                await message.answer(
                    "❌ ID 6 xonali raqam bo'lishi kerak!\n\n"
                    "📋 Masalan: 123456\n"
                    "🔄 Qaytadan urinib ko'ring."
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
                    "yoki tugmalardan foydalaning."
                )
                
    except Exception as e:
        logger.error(f"Xabarni qayta ishlashda xatolik: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring."
        )

async def search_by_id(message: Message, user_id: str):
    """ID bo'yicha qidiruv"""
    try:
        # Excel fayllarida qidirish
        result = excel_handler.search_by_id(user_id)
        
        # Qidiruv statistikasini yangilash
        db.increment_search_count(message.from_user.id)
        
        if result:
            # Hafta kunini va sanasini Excel fayldan olish
            week_day = str(result.get('Nazorat kuni', 'Noma\'lum'))
            date_str = str(result.get('Nazorat sanasi', 'Noma\'lum'))
            
            # Sanani formatlash
            try:
                if date_str != 'Noma\'lum' and date_str != '':
                    # Excel sanani formatlash (YYYY-MM-DD -> DD.MM.YYYY)
                    if isinstance(date_str, str) and len(date_str) >= 10:
                        # Agar format YYYY-MM-DD bo'lsa
                        if '-' in date_str:
                            year, month, day = date_str.split('-')[:3]
                            formatted_date = f"{day}.{month}.{year}"
                        else:
                            # Boshqa formatlarni to'g'ridan-to'g'ri ishlatish
                            formatted_date = date_str
                    else:
                        formatted_date = str(date_str)
                else:
                    formatted_date = 'Noma\'lum'
            except Exception as e:
                print(f"Sana formatlash xatoligi: {e}")
                formatted_date = str(date_str) if date_str != 'Noma\'lum' else 'Noma\'lum'
            
            # Natijani formatlash
            response_text = f"📅 HAFTA KUNI: {week_day.upper()}\n"
            response_text += f"🗓 SANASI: {formatted_date}\n"
            response_text += f"🔢 ID: {result['ID']}\n\n"
            response_text += f"👤 ISM: {result['Ism']}\n"
            response_text += f"👥 FAMILIYA: {result['Familiya']}\n"
            response_text += f"📚 FAN: {result['Fan']}\n"
            response_text += f"🏫 XONA: {result['Xona']}\n"
            response_text += f"🕓 BOSHLANISH VAQTI: {str(result.get('Nazorat boshlanish vaqti', 'Noma\'lum'))}\n"
            response_text += f"🕔 TUGASH VAQTI: {str(result.get('Nazorat tugash vaqti', 'Noma\'lum'))}\n"
            response_text += f"📄 MANBA: {result['source_file']}"
            
            await message.answer(response_text)
        else:
            await message.answer(
                f"❌ ID: {user_id} bo'yicha ma'lumot topilmadi.\n\n"
                "🔍 Boshqa ID bilan urinib ko'ring."
            )
            
    except Exception as e:
        logger.error(f"Qidiruvda xatolik: {e}")
        await message.answer(
            "❌ Qidiruvda xatolik yuz berdi!\n"
            "🔄 Qaytadan urinib ko'ring."
        )

async def list_files(message: Message):
    """Admin fayllar ro'yxatini ko'rsatish"""
    if not TelegramBot.is_admin(message.from_user.id):
        await message.answer(
                "❌ Bu komanda faqat admin uchun!\n\n"
                "👨‍💻 Admin @shohjahon_o5")
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
        await message.answer(
                "❌ Bu komanda faqat admin uchun!\n\n"
                "👨‍💻 Admin @shohjahon_o5")
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

# =================================================================
# ASOSIY FUNKSIYA
# =================================================================

async def main():
    """Botni ishga tushurish"""
    try:
        print("🤖 Excel qidiruv boti ishga tushmoqda...")
        print(f"👨‍💻 Admin ID: {ADMIN_ID}")
        print(f"📁 Excel fayllar papkasi: {EXCEL_FILES_DIR}")
        
        # Papkalarni yaratish
        os.makedirs(EXCEL_FILES_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(USERS_DB), exist_ok=True)
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        
        # Excel fayllarini yuklash
        excel_handler.load_existing_files()
        print(f"📊 Yuklangan Excel fayllar: {len(excel_handler.get_file_list())} ta")
        
        # Botni ishga tushurish
        print("🚀 Bot polling boshlandi...")
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        print("⏹️ Bot to'xtatildi")
    except Exception as e:
        logger.error(f"Botni ishga tushurishda xatolik: {e}")
        print(f"❌ Xatolik: {e}")
    finally:
        # Sessionni yopish
        await bot.session.close()
        print("🔒 Bot session yopildi")

if __name__ == "__main__":
    asyncio.run(main())
