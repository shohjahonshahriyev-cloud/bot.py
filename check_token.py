import requests

# Tokenni tekshirish
BOT_TOKEN = '8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/getMe'

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data.get('ok'):
        bot_info = data['result']
        print('✅ Token to\'g\'ri!')
        print(f'🤖 Bot nomi: {bot_info["username"]}')
        print(f'📝 Bot nomi: {bot_info["first_name"]}')
        print(f'🆔 Bot ID: {bot_info["id"]}')
        print(f'📊 Is bot: {bot_info["is_bot"]}')
    else:
        print(f'❌ Token xato: {data.get("description", "Noma\'lum xatolik")}')
        
except requests.exceptions.RequestException as e:
    print(f'❌ Internet xatoligi: {e}')
except Exception as e:
    print(f'❌ Boshqa xatolik: {e}')
