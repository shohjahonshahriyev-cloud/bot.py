# Serverga joylash uchun qo'llanma

## Telegram botni serverga joylash

### 1. Serverga ulanish
```bash
# SSH orqali serverga ulaning
ssh username@server_ip
```

### 2. Git orqali kodni yuklash (agar Git repo bor bo'lsa)
```bash
git clone <repository_url>
cd telegram
```

### Yoki FTP/SCP orqali fayllarni yuklash
```bash
# SCP orqali
scp -r telegram/ username@server_ip:/path/to/project/
```

### 3. Docker o'rnatish (agar o'rnatilmagan bo'lsa)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose o'rnatish
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. Botni ishga tushurish
```bash
# Papkaga o'tish
cd /path/to/telegram

# Docker orqali ishga tushurish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f
```

### 5. Botni to'xtatish
```bash
docker-compose down
```

### 6. Botni yangilash
```bash
# Kodni yangilash
git pull  # yoki fayllarni qayta yuklash

# Konteynerni qayta qurish va ishga tushurish
docker-compose down
docker-compose up -d --build
```

## Muhim eslatmalar

1. **Bot token** - `bot_complete.py` faylida tokeningizni to'g'ri kiriting
2. **Admin ID** - O'zingizning Telegram ID'ingizni kiriting
3. **Papka huquqlari** - Serverda papkalarga to'g'ri huquqlar bering
4. **Portlar** - Agar web server qo'shsangiz, portlarni oching

## Avtomatik ishga tushirish (systemd)

```bash
# Service faylini yaratish
sudo nano /etc/systemd/system/telegram-bot.service
```

Service fayli tarkibi:
```ini
[Unit]
Description=Telegram Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/telegram
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Serviceni yoqish:
```bash
sudo systemctl enable telegram-bot.service
sudo systemctl start telegram-bot.service
```
