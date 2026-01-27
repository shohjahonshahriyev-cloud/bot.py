# Konfiguratsiya fayli
import os

# Bot tokeni (BotFather'dan olingan)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Bu yerga o'zingizning bot tokeningizni kiriting

# Admin ID (o'zingizning Telegram ID'ingiz)
ADMIN_ID = 123456789  # Bu yerga o'zingizning Telegram ID'ingizni kiriting

# Papka yo'llari
EXCEL_FILES_DIR = "data/excel_files"
LOGS_DIR = "logs"

# Fayl nomlari
USERS_DB = "data/users.json"
STATS_FILE = "data/stats.json"

# Bot sozlamalari
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_FILE_TYPES = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]  # .xlsx

# Xabarlarni saqlash muddati (kun)
MESSAGE_RETENTION_DAYS = 30

# Excel ustun nomlari
EXCEL_COLUMNS = ["ID", "Ism", "Familiya", "Fan", "Sana", "Xona"]
