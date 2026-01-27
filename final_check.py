print('🔍 Botni oxirgi marta tekshiramiz...')

# Tokenni tekshirish
import requests
BOT_TOKEN = '8548676063:AAFAQPcEAq8pHcVYB1BsPtJQbWuEhmlV95E'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/getMe'

try:
    response = requests.get(url, timeout=5)
    data = response.json()
    
    if data.get('ok'):
        print('✅ Token to\'g\'ri')
        print(f'🤖 Bot: @{data["result"]["username"]}')
        print('🚀 Bot ishga tayyor!')
    else:
        print(f'❌ Token xato: {data.get("description")}')
        
except Exception as e:
    print(f'❌ Internet xatoligi: {e}')
