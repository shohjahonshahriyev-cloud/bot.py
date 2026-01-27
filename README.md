# Excel Qidiruv Telegram Boti

## 📋 Loyiha haqida
Bu bot Excel fayllaridan 6 xonali ID orqali ma'lumotlarni qidirish uchun yaratilgan. Faqat admin Excel fayllarini yuklay oladi, foydalanuvchilar esa faqat qidirish amalini bajarishi mumkin.

## 🏗️ Loyiha tuzilmasi
```
telegram/
<<<<<<< HEAD
├── bot_complete.py          # Asosiy bot fayli
├── config.py           # Konfiguratsiya
├── excel_handler.py    # Excel fayllar bilan ishlash
├── database.py         # Ma'lumotlar bazasi
├── requirements.txt    # Kerakli kutubxonalar
├── README.md          # Hujjatlar
├── data/
│   ├── excel_files/   # Excel fayllar saqlanadi
│   ├── users.json     # Foydalanuvchilar ma'lumoti
│   └── stats.json     # Statistika
└── logs/              # Log fayllari
```

## 🚀 O'rnatish va ishga tushurish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Konfiguratsiyani sozlash
`config.py` faylida quyidagilarni o'zgartiring:
- `BOT_TOKEN`: BotFather'dan olingan token
- `ADMIN_ID`: O'zingizning Telegram ID'ingiz

### 3. Botni ishga tushurish
```bash
<<<<<<< HEAD
python bot_new.py
=======
python bot_complete.py
>>>>>>> 8a39c474dcc8577a3802a7d995e819a5b5b176ac
```

## 📋 Bot imkoniyatlari

### 👤 Foydalanuvchi uchun:
- **6 xonali ID bilan qidirish**: Excel fayllaridan ma'lumot topish
- **Yordam**: Botdan foydalanish bo'yicha ko'rsatma

### 👨‍💻 Admin uchun:
- **📁 Excel fayl yuklash**: .xlsx formatdagi fayllarni yuklash
- **📊 Statistika ko'rish**: Foydalanuvchilar, qidiruvlar, fayllar soni
- **📢 Broadcast**: Barcha foydalanuvchilarga xabar yuborish
- **📋 Fayllar ro'yxati**: Yuklangan fayllarni ko'rish

## 📊 Excel fayl formati

Excel fayllarida quyidagi ustunlar bo'lishi kerak:
- **ID**: 6 xonali raqam
- **Ism**: Foydalanuvchi ismi
- **Familiya**: Foydalanuvchi familiyasi
- **Fan**: Fan nomi
- **Sana**: Sana
- **Xona**: Xona raqami

## 🔐 Xavfsizlik
- Faqat admin fayl yuklay oladi
- Foydalanuvchilar faqat qidirishi mumkin
- Admin ID oldindan belgilanadi

## 📱 Bot komandalari

### Umumiy komandalar:
- `/start`: Botni ishga tushurish
- `/help`: Yordam olish

### Admin komandalari (tugmalar orqali):
- 📊 Statistika: Bot statistikasini ko'rish
- 📁 Fayllar: Yuklangan fayllar ro'yxati
- 📢 Xabar yuborish: Broadcast xabar
- 🔙 Orqaga: Asosiy menuga qaytish

## 🛠️ Texnologiyalar
- **Python 3.8+**
- **aiogram 3.4.1**: Telegram bot framework
- **pandas**: Excel fayllar bilan ishlash
- **openpyxl**: Excel fayllar o'qish
- **python-dotenv**: Environment variables

## 📝 Qo'shimcha eslatmalar
- Bot avtomatik ravishda `data/excel_files` papkasidagi barcha .xlsx fayllarni yuklaydi
- Ma'lumotlar `data` papkasida JSON formatida saqlanadi
- Log fayllari `logs` papkasiga yoziladi
- Bot 24/7 ishlashi uchun serverda deploy qilish tavsiya etiladi

## 🤞 Qo'llab-quvvatlash
Agar savollaringiz bo'lsa yoki xatolik topsangiz, iltimos, admin bilan bog'laning.
