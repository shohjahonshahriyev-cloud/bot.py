# Heroku uchun Telegram bot joylash qo'llanmasi

## 1. Heroku CLI o'rnatish
Windows uchun: https://devcenter.heroku.com/articles/heroku-cli

## 2. Herokuga kirish
```bash
heroku login
```

## 3. Git repo yaratish
```bash
git init
git add .
git commit -m "First commit"
```

## 4. Heroku app yaratish
```bash
heroku create your-app-name
```

## 5. Environment variables sozlash
```bash
heroku config:set BOT_TOKEN="8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"
heroku config:set ADMIN_ID="422057508"
```

## 6. Kodni yuklash
```bash
git push heroku main
```

## 7. Botni ishga tushurish
```bash
heroku ps:scale web=1
```

## 8. Loglarni ko'rish
```bash
heroku logs --tail
```

## 9. Botni to'xtatish
```bash
heroku ps:scale web=0
```

## Muhim eslatmalar
- Heroku bepul reja 550 soatiga cheklangan
- Bot har doim ishlashi uchun har oy $7 to'lash kerak
- Yoki har kuni qayta ishga tushirish mumkin

## Avtomatik qayta ishga tushirish (har kuni)
```bash
heroku scheduler:add --app your-app-name --plan "standard" --command "heroku ps:restart" --at "02:00"
```
