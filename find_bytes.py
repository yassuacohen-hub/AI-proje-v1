with open('web_app.py', 'rb') as f:
    content_bytes = f.read()

# Find the exact location
idx = content_bytes.find(b'search_event kayit hatasi')
print(f"Found at byte {idx}")
print(content_bytes[idx:idx+300])

# Find the section header
idx2 = content_bytes.find(b'X04:', idx)
print(f"\nX04 at byte {idx2}")
print(content_bytes[idx2:idx2+200])