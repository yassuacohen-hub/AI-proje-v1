#!/usr/bin/env python
import base64
baslik = '[ORKESTRA] Ajan arasi protokol yaz → ajan_chat_koordinasyon.py (3s)'
b64 = base64.b64encode(baslik.encode('utf-8')).decode('ascii')
print(b64)
