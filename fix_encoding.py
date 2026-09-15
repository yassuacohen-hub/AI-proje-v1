with open('web_dashboard/tabs/admin_extras.py', 'rb') as f:
    data = f.read()
double_encoded = data.decode('utf-8')
single_encoded_bytes = double_encoded.encode('latin-1')
original_text = single_encoded_bytes.decode('utf-8')
with open('web_dashboard/tabs/admin_extras.py', 'w', encoding='utf-8') as f:
    f.write(original_text)
