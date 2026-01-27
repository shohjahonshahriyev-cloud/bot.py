#!/bin/bash

# Telegram botni serverga joylash skripti

echo "Telegram botni serverga joylash boshlanmoqda..."

# Papkalarni yaratish
echo "Papkalarni yaratish..."
mkdir -p data/excel_files
mkdir -p logs
mkdir -p admin_files
mkdir -p user_files

# Huquqlarni berish
echo "Papkalarga huquqlar berish..."
chmod 755 data logs admin_files user_files
chmod 644 data/*.json 2>/dev/null || true

# Docker Compose orqali botni ishga tushurish
echo "Botni Docker orqali ishga tushurish..."
docker-compose down
docker-compose build
docker-compose up -d

# Loglarni ko'rish
echo "Bot loglari:"
docker-compose logs -f --tail=20
