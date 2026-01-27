import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from pathlib import Path
from file_reader import FileReader

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DocumentBot:
    def __init__(self, token: str, admin_id: int, admin_username: str = None):
        self.token = token
        self.admin_id = admin_id
        self.admin_username = admin_username
        self.file_reader = FileReader()
        self.admin_files = {'files': []}  # Admin tomonidan yuklangan fayllar
        self.user_requests = {}  # Foydalanuvchi so'rovlarini saqlash
        self.files_loaded = False  # Fayllar yuklanganligini belgilash
        
        # Admin papkasidagi fayllarni avtomatik yuklash
        self.load_existing_files()
        
        # Qo'shimcha tekshiruv - fayllar yuklanganligini ko'rsatish
        print(f"🚀 Bot ishga tushdi. Admin fayllari: {len(self.admin_files.get('files', []))} ta")
        if self.admin_files.get('files'):
            print(f"📁 Fayl: {self.admin_files['files'][0]}")
        else:
            print("📭 Fayllar yo'q")
    
    def is_admin(self, user_id: int, username: str = None):
        """Foydalanuvchi admin ekanligini tekshirish"""
        # ID orqali tekshirish
        if user_id == self.admin_id:
            return True
        
        # Username orqali tekshirish
        if self.admin_username and username:
            return username.lower() == self.admin_username.lower()
        
        return False
    
    def load_existing_files(self):
        """Admin papkasidagi mavjud fayllarni yuklash"""
        if self.files_loaded:  # Agar fayllar avval yuklangan bo'lsa, qayta yuklamaslik
            return
            
        import glob
        admin_dir = "admin_files"
        
        if os.path.exists(admin_dir):
            # Qo'llab-quvvatlanadigan formatlardagi fayllarni topish
            supported_extensions = ['*.xlsx', '*.xls', '*.docx', '*.pdf']
            found_files = []
            
            for ext in supported_extensions:
                files = glob.glob(os.path.join(admin_dir, ext))
                found_files.extend(files)
            
            if found_files:
                # Faqat oxirgi faylni olish (eng yangisi)
                latest_file = max(found_files, key=os.path.getctime)
                self.admin_files['files'] = [latest_file]
                print(f"📁 Avtomatik yuklandi: {latest_file}")
                print(f"📊 Fayllar ro'yxati: {self.admin_files['files']}")
            else:
                print("📭 Admin papkasida fayllar yo'q")
                self.admin_files['files'] = []
        else:
            print("📭 Admin papkasi mavjud emas")
            self.admin_files['files'] = []
        
        self.files_loaded = True  # Fayllar yuklandi deb belgilash
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Botni ishga tushurish komandasi"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if self.is_admin(user_id, username):
            welcome_text = """
👨‍💻 **Admin paneliga xush kelibsiz!**

🤖 Hujjat qidiruv boti admin interfeysi

📋 Admin komandalari:
• /help - Yordam olish
• /files - Yuklangan fayllarni ko'rish
• /clear - Barcha fayllarni o'chirish
• /stats - Statistika

📄 Fayl yuklash uchun faylni to'g'ridan-to'g'ri yuboring!
            """
        else:
            welcome_text = """
🤖 SAMDAQU qidiruv botiga xush kelibsiz!

ADMIN @shohjahon_o5

Men Excel, Word va PDF fayllaridan ID orqali ma'lumotlarni topishim mumkin.

📋 Qo'llanma:
• ID raqamni adashnasdan yuboring
• ID raqamini yuboring - qidirishni boshlash

🔍


Qidirish uchun ID raqamini kiriting!
            """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam komandasi"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if self.is_admin(user_id, username):
            help_text = """
📚 **Admin qo'llanmasi:**

1️⃣ **Fayl yuklash:**
   - Excel, Word yoki PDF faylni yuboring
   - Fayllar bazaga saqlanadi

2️⃣ **Fayllarni boshqarish:**
   - /files - Barcha fayllarni ko'rish
   - /clear - Barcha fayllarni o'chirish
   - /stats - Statistika

3️⃣ **Foydalanuvchi so'rovlari:**
   - Foydalanuvchilar ID orqali qidiradi
   - Siz yuklagan fayllarda qidiriladi

4️⃣ **Xavfsizlik:**
   - Faqat admin fayl yuklay oladi
   - Foydalanuvchilar faqat qidirishi mumkin

👨‍💻 Admin: @shohjahon_o5
            """
        else:
            help_text = """
📚 **Botdan foydalanish qo'llanmasi:**

1️⃣ **ID bilan qidirish:**
   - Qidirish uchun ID raqamini yuboring
   - Bot admin yuklagan fayllarda qidiradi

2️⃣ **Natijalar:**
   - Topilgan ma'lumotlar matn shaklida ko'rsatiladi
   - Fayl turi va mosliklar soni ko'rsatiladi

3️⃣ **Qo'llab-quvvatlanadigan formatlar:**
   • Excel (.xlsx, .xls)
   • Word (.docx)
   • PDF (.pdf)

❓ Savollaringiz bo'lsa, admin (@shohjahon_o5) ga murojaat qiling!
            """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Faylni qabul qilish va saqlash (faqat admin uchun)"""
        try:
            user_id = update.effective_user.id
            username = update.effective_user.username
            
            # Faqat admin fayl yuklay oladi
            if not self.is_admin(user_id, username):
                await update.message.reply_text(
                    "❌ Siz fayl yuklay olmaysiz!\n"
                    "📋 Faqat admin fayl yuklay oladi.\n"
                    "👨‍💻 Admin: @shohjahon_o5\n"
                    "🔍 ID orqali qidirish uchun raqam yuboring."
                )
                return
            
            document = update.message.document
            if not document:
                await update.message.reply_text("❌ Fayl topilmadi!")
                return
            
            # Faylni yuklab olish
            file_info = await context.bot.get_file(document.file_id)
            
            # Fayl nomini olish
            file_name = document.file_name
            if not file_name:
                file_name = f"document_{document.file_id}.bin"
            file_ext = Path(file_name).suffix.lower()
            
            # Formatni tekshirish
            if file_ext not in self.file_reader.supported_formats:
                await update.message.reply_text(
                    f"❌ Qo'llab-quvvatlanmaydigan format: {file_ext}\n"
                    "📋 Iltimos, Excel (.xlsx, .xls), Word (.docx) yoki PDF fayl yuboring."
                )
                return
            
            # Faylni saqlash
            download_dir = "admin_files"
            os.makedirs(download_dir, exist_ok=True)
            file_path = f"{download_dir}/{file_name}"
            
            await file_info.download_to_drive(file_path)
            
            # Eski fayllarni o'chirib, faqat yangi faylni saqlash
            self.admin_files['files'] = [file_path]
            
            await update.message.reply_text(
                f"✅ Fayl muvaffaqiyatli yuklandi: {file_name}\n"
                f"📁 Saqlangan: {file_path}\n"
                f"🔍 Endi barcha foydalanuvchilar qidirishi mumkin!\n"
                f"📊 Eski fayllar o'chirildi, faqat bu fayl ishlatiladi."
            )
            
        except Exception as e:
            logger.error(f"Faylni yuklashda xatolik: {e}")
            await update.message.reply_text(
                f"❌ Faylni yuklashda xatolik yuz berdi: {str(e)}\n"
                "🔄 Qaytadan urinib ko'ring."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabarlarni qabul qilish (ID qidirish)"""
        try:
            user_id = update.effective_user.id
            username = update.effective_user.username
            message_text = update.message.text.strip()
            
            # Input validation
            if not message_text:
                await update.message.reply_text("❌ Iltimos, ID raqamini kiriting!")
                return
            
            # Admin uchun maxsus komandalarni tekshirish
            if self.is_admin(user_id, username):
                if message_text.startswith('/admin_'):
                    await self.handle_admin_command(update, message_text)
                    return
            
            # Debug ma'lumotlari olib tashlandi - fayllar to'g'ri yuklanishi kerak
            
            # Agar admin fayllari bo'lmasa
            if 'files' not in self.admin_files or not self.admin_files['files']:
                await update.message.reply_text(
                    "❗ Hozircha hech qanday fayl yuklanmagan.\n"
                    "📄 Admin faylni yuklagach, qidirish mumkin bo'ladi.\n"
                    "👨‍💻 Admin: @shohjahon_o5"
                )
                return
            
            # ID qidirish
            search_id = message_text
            results = []
            
            # Faylni yuklash va qidirish
            if self.admin_files['files']:
                file_path = self.admin_files['files'][-1]  # Oxirgi yuklangan fayl
                
                # Fayl mavjudligini tekshirish
                if not os.path.exists(file_path):
                    await update.message.reply_text(
                        "❌ Fayl topilmadi!\n"
                        "📄 Admin faylni qayta yuklashi kerak."
                    )
                    return
                
                result = self.file_reader.search_by_id(file_path, search_id)
                
                if 'error' in result:
                    await update.message.reply_text(
                        f"❌ Faylni o'qishda xatolik: {result['error']}\n"
                        "📄 Boshqa fayl yuklangan bo'lishi mumkin."
                    )
                    return
                
                if 'matches' in result and result['matches']:
                    results = [{
                        'file_name': Path(file_path).name,
                        'file_type': result['file_type'],
                        'matches': result['matches'],
                        'matches_count': result['matches_count']
                    }]
            
            # So'rovni statistikaga qo'shish
            if user_id not in self.user_requests:
                self.user_requests[user_id] = {'count': 0, 'last_search': None}
            self.user_requests[user_id]['count'] += 1
            self.user_requests[user_id]['last_search'] = search_id
            
            # Natijalarni yuborish
            if results:
                # Hafta kunini va sanasini olish
                import datetime
                today = datetime.datetime.now()
                week_days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
                week_day = week_days[today.weekday()]
                date_str = today.strftime('%d.%m.%Y')
                
                # Jami fanlar soni
                total_matches = sum(result['matches_count'] for result in results)
                
                # Bosh xabar - yangi format
                response_text = f"📅 HAFTA KUNI: {week_day.upper()}\n"
                response_text += f"🗓 SANASI: {date_str}\n"
                response_text += f"🔢 TOPILGAN FANLAR SONI: {total_matches} TA\n\n"
                
                # Har bir natijani alohida formatlash
                match_count = 1
                for result in results:
                    if result['file_type'] == 'excel':
                        for match in result['matches']:
                            fan_nomi = match.get('Fan nomi', 'Noma\'lum')
                            fan_kodi = match.get('Fan kodi', 'Noma\'lum')
                            boshlanish = match.get('Nazorat boshlanish vaqti', 'Noma\'lum')
                            auditoriya = match.get('Nazorat xonasi', 'Noma\'lum')
                            
                            response_text += f"«{match_count}).» 📚 FAN NOMI: {fan_nomi}\n"
                            response_text += f"🔠 FAN KODI: {fan_kodi}\n"
                            response_text += f"🕓 BOSHLANISH VAQTI: {boshlanish}\n"
                            response_text += f"🏫 AUDITORIYA: {auditoriya}\n"
                            response_text += f"📄 SAVOL: varaqangiz {match_count} - Navbatda sizga beriladi.\n\n"
                            
                            match_count += 1
                            
                            # Faqat 5 ta natijani ko'rsatish
                            if match_count > 5:
                                response_text += f"... va yana {total_matches - 5} ta fan\n\n"
                                break
                    
                    elif result['file_type'] in ['word', 'pdf']:
                        for match in result['matches'][:5]:
                            text = match.get('text', str(match))
                            if result['file_type'] == 'word':
                                page_info = f"Paragraf {match.get('paragraph_index', match_count)}"
                            else:
                                page_info = f"Sahifa {match.get('page', match_count)}"
                            
                            # Matnni tozalash
                            if len(text) > 200:
                                text = text[:200] + "..."
                            
                            response_text += f"«{match_count}).» 📄 {page_info}\n"
                            response_text += f"📝 MATN: {text}\n\n"
                            
                            match_count += 1
                
                # Faqat yangi formatdagi natijani yuborish
                await update.message.reply_text(response_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    f"❌ **ID: {search_id}** hech qanday faylda topilmadi.\n"
                    "🔍 Boshqa ID bilan urinib ko'ring."
                )
                
        except Exception as e:
            logger.error(f"Xabarni qayta ishlashda xatolik: {e}")
            await update.message.reply_text(
                "❌ Xatolik yuz berdi!\\n"
                "� Qaytadan urinib ko'ring."
            )
    
    async def list_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin fayllar ro'yxatini ko'rsatish"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if not self.is_admin(user_id, username):
            await update.message.reply_text("❌ Bu komanda faqat admin uchun!\n👨‍💻 Admin: @shohjahon_o5")
            return
        
        if 'files' not in self.admin_files or not self.admin_files['files']:
            await update.message.reply_text("📭 Admin fayllari yo'q.")
            return
        
        response_text = "📁 **Admin fayllari:**\n\n"
        
        for i, file_path in enumerate(self.admin_files['files'], 1):
            file_name = Path(file_path).name
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            response_text += f"{i}. 📄 {file_name}\n"
            response_text += f"   📊 Hajmi: {file_size_mb:.2f} MB\n"
            response_text += f"   📍 Yo'l: {file_path}\n\n"
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def clear_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Barcha admin fayllarini o'chirish"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if not self.is_admin(user_id, username):
            await update.message.reply_text("❌ Bu komanda faqat admin uchun!\n👨‍💻 Admin: @shohjahon_o5")
            return
        
        if 'files' not in self.admin_files or not self.admin_files['files']:
            await update.message.reply_text("📭 O'chirish uchun fayllar yo'q.")
            return
        
        # Fayllarni o'chirish
        import shutil
        download_dir = "admin_files"
        
        try:
            if os.path.exists(download_dir):
                shutil.rmtree(download_dir)
            
            self.admin_files['files'] = []
            await update.message.reply_text("✅ Barcha admin fayllari muvaffaqiyatli o'chirildi.")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}")
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Statistikani ko'rsatish"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if not self.is_admin(user_id, username):
            await update.message.reply_text("❌ Bu komanda faqat admin uchun!\n👨‍💻 Admin: @shohjahon_o5")
            return
        
        total_files = len(self.admin_files.get('files', []))
        total_users = len(self.user_requests)
        total_requests = sum(user_data['count'] for user_data in self.user_requests.values())
        
        stats_text = f"""
📊 **Bot statistikasi:**

📁 Yuklangan fayllar: {total_files} ta
👥 Foydalanuvchilar: {total_users} ta
🔍 Jami so'rovlar: {total_requests} ta

📋 Oxirgi so'rovlar:
"""
        
        # Oxirgi 5 ta so'rovni ko'rsatish
        recent_requests = sorted(
            [(user_id, data) for user_id, data in self.user_requests.items()],
            key=lambda x: x[1]['last_search'] or '',
            reverse=True
        )[:5]
        
        for user_id, data in recent_requests:
            stats_text += f"• User {user_id}: {data['count']} ta so'rov\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def handle_admin_command(self, update: Update, command: str):
        """Admin komandalarini qayta ishlash"""
        if command == '/admin_stats':
            await self.show_stats(update, None)
        elif command == '/admin_broadcast':
            await update.message.reply_text("📢 Broadcast xususiyati tez orada qo'shiladi!")
        else:
            await update.message.reply_text("❌ Noto'g'ri admin komandasi!")
    
    def run(self):
        """Botni ishga tushirish"""
        application = Application.builder().token(self.token).build()
        
        # Handlerlarni qo'shish
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("files", self.list_files))
        application.add_handler(CommandHandler("clear", self.clear_files))
        application.add_handler(CommandHandler("stats", self.show_stats))
        
        # Fayl va xabar handlerlari
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Botni ishga tushurish
        print("🤖 Bot ishga tushdi...")
        application.run_polling()

def main():
    # Token va admin ID - environment variables dan olish
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "422057508"))  # Admin ID
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "shohjahon_o5")  # Admin username
    
    bot = DocumentBot(BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME)
    bot.run()

if __name__ == "__main__":
    main()
