# Check the exact bytes of the failing test
with open('src/company_master/admin_audit.py', 'rb') as f:
    content = f.read()

# Find the failing test
idx = content.find(b'supheli_cok_ulkeli_ip(olaylar_none_ulke')
if idx >= 0:
    print(f"Found at byte {idx}")
    print(content[idx:idx+200])