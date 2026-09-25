#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print(f'Token var: {bool(token)}')
print(f'Chat ID: {chat_id}')

if token and chat_id:
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': '🔬 Test: Hello World - Bot çalışıyor!'}
    try:
        r = requests.post(url, json=data, timeout=5)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            print('✓ Mesaj başarıyla gönderildi!')
        else:
            print(f'Error: {r.text}')
    except Exception as e:
        print(f'Exception: {e}')
else:
    print('Token veya Chat ID eksik!')
