# Telegram Bot - GitHub orqali joylash

## 1. GitHub repo yaratish
1. GitHub.com ga kiring
2. "New repository" tugmasini bosing
3. "telegram-bot" nomi bilan repo yarating
4. Public qiling

## 2. Repo ga ulanish
```bash
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/username/telegram-bot.git
& "C:\Program Files\Git\bin\git.exe" branch -M main
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

## 3. Secrets sozlash
GitHub repo da:
1. Settings → Secrets and variables → Actions
2. New repository secret
3. BOT_TOKEN: "8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E"
4. ADMIN_ID: "422057508"

## 4. Botni ishga tushurish
1. Actions tabiga o'ting
2. "Deploy Telegram Bot" workflow ni tanlang
3. "Run workflow" tugmasini bosing

## 5. Loglarni ko'rish
Actions da workflow loglarini ko'rib bot ishlashini tekshiring

## Afzalliklari:
- ✅ Bepul
- ✅ 24/7 ishlaydi
- ✅ Avtomatik qayta ishga tushurish
