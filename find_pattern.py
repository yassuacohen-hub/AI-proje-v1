with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact location
idx = content.find('search_event kayit hatasi')
print(f"Found at {idx}")
print(repr(content[idx:idx+300]))

# Now let's find the exact pattern to replace
# Looking for the section after the except block
start = content.find('\n\n# ', idx)
print(f"Next section at {start}")
print(repr(content[start:start+100]))