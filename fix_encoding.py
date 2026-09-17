import sys
path = 'web_dashboard/tabs/admin_quality.py'
with open(path, 'rb') as f:
    raw = f.read()
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
    print('BOM stripped')
else:
    print('No BOM found')
text = raw.decode('utf-8')
fixed_text = []
i = 0
while i < len(text):
    c = text[i]
    if ord(c) == 0xC3 and i + 1 < len(text):
        nxt = text[i+1]
        pair = c + nxt
        mapping = {
            chr(0xC3) + chr(0xB6): chr(0xF6),
            chr(0xC3) + chr(0xA7): chr(0xE7),
            chr(0xC3) + chr(0xBC): chr(0xFC),
            chr(0xC3) + chr(0xB1): chr(0xF1),
            chr(0xC3) + chr(0xAA): chr(0xEA),
            chr(0xC3) + chr(0xA9): chr(0xE9),
            chr(0xC3) + chr(0xAD): chr(0xED),
            chr(0xC3) + chr(0xA1): chr(0xE1),
            chr(0xC3) + chr(0xA0): chr(0xE0),
            chr(0xC3) + chr(0xAF): chr(0xFF),
            chr(0xC3) + chr(0xBE): chr(0xFE),
            chr(0xC3) + chr(0xB9): chr(0xFD),
            chr(0xC3) + chr(0xA8): chr(0xE8),
            chr(0xC3) + chr(0xAB): chr(0xEB),
            chr(0xC3) + chr(0xAC): chr(0xEC),
            chr(0xC3) + chr(0xA5): chr(0xE5),
            chr(0xC3) + chr(0xB8): chr(0xF8),
            chr(0xC3) + chr(0xB4): chr(0xF4),
            chr(0xC3) + chr(0xA6): chr(0xE6),
            chr(0xC3) + chr(0x99): chr(0x99),
            chr(0xC3) + chr(0xA2): chr(0xE2),
            chr(0xC3) + chr(0xB7): chr(0xB7),
        }
        if pair in mapping:
            fixed_text.append(mapping[pair])
            i += 2
            continue
    if c == chr(0xE2) and i + 2 < len(text) and text[i+1] == chr(0x20AC) and text[i+2] == chr(0x201C):
        fixed_text.append(chr(0x2014))
        i += 3
        continue
    if c == chr(0xE2) and i + 1 < len(text) and text[i+1] == chr(0x20AC):
        fixed_text.append(chr(0x2014))
        i += 2
        continue
    fixed_text.append(c)
    i += 1
fixed = ''.join(fixed_text)
with open(path, 'wb') as f:
    f.write(fixed.encode('utf-8'))
print('Fixed encoding')
print('Original length:', len(text), 'Fixed length:', len(fixed))
verify = fixed.encode('utf-8').decode('utf-8')
mojibake_chars = [chr(0xC3), chr(0xE2)+chr(0x20AC), chr(0xC5), chr(0xC3)+chr(0x2030), chr(0xC3)+chr(0xBC), chr(0xC3)+chr(0xB6), chr(0x11F)+chr(0x178), chr(0x11F)+chr(0x178)+chr(0x15F)]
found = [c for c in mojibake_chars if c in verify]
print('Mojibake remaining:', found)
print('First 300 chars:', verify[:300])
