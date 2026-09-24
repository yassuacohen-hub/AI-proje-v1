# Check exact bytes around the failure
with open('src/company_master/admin_audit.py', 'rb') as f:
    content = f.read()

idx = content.find(b'supheli_cok_ulkeli_ip(olaylar_none_ulke')
if idx >= 0:
    # Print 300 bytes from that position
    print(content[idx:idx+300])
    print("---")
    # Also check the exact expected line
    lines = content[idx:idx+300].split(b'\n')
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")