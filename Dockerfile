# Python 3.11 asosida Telegram bot
FROM python:3.11-slim

# Ishchi papkani o'rnatish
WORKDIR /app

# Avval kerakli system paketlarni o'rnatish
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements faylini nusxalash
COPY requirements.txt .

# Python paketlarini o'rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni nusxalash
COPY . .

# Kerakli papkalarni yaratish
RUN mkdir -p data/excel_files logs admin_files user_files

# Portni ochish (agar kerak bo'lsa)
EXPOSE 8080

# Botni ishga tushirish
CMD ["python", "bot_complete.py"]
