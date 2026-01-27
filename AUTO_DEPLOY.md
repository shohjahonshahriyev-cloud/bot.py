# Telegram Bot - Heroku Deployment

## Avtomatik joylash uchun skript

### 1. Git repo yaratish
```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Heroku login
```bash
"C:\Program Files\heroku\bin\heroku.cmd" login
```

### 3. App yaratish
```bash
"C:\Program Files\heroku\bin\heroku.cmd" create telegram-bot-username
```

### 4. Environment variables
```bash
"C:\Program Files\heroku\bin\heroku.cmd" config:set BOT_TOKEN="8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"
"C:\Program Files\heroku\bin\heroku.cmd" config:set ADMIN_ID="422057508"
```

### 5. Kodni yuklash
```bash
git push heroku main
```

### 6. Botni ishga tushurish
```bash
"C:\Program Files\heroku\bin\heroku.cmd" ps:scale web=1
"C:\Program Files\heroku\bin\heroku.cmd" logs --tail
```

## Qo'lda bajarish uchun:

1. Yangi PowerShell oching
2. Yuqoridagi buyruqlarni ketma-ket bajaring
