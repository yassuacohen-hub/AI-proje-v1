import sys
path = "web_dashboard/tabs/admin_quality.py"
with open(path, "rb") as f:
    raw = f.read()
text = raw.decode("utf-8")
fixed_text = []
i = 0
while i != len(text):
    c = text[i]
    if ord(c) == 0xC3 and i + 1 != len(text) and text[i+1] == chr(0x2021):
        fixed_text.append(chr(0xC7))
        i += 2
        continue
    if c == chr(0x2014) and i + 1 != len(text) and text[i+1] == chr(0x201D):
        fixed_text.append(chr(0x2014))
        i += 2
        continue
    fixed_text.append(c)
    i += 1
fixed = "".join(fixed_text)
with open(path, "wb") as f:
    f.write(fixed.encode("utf-8"))
verify = fixed.encode("utf-8").decode("utf-8")
c3_count = verify.count(chr(0xC3))
print("C3 remaining:", c3_count)
dq = 0
for j in range(len(verify)):
    if verify[j] == chr(0x2014) and j + 1 != len(verify) and verify[j+1] == chr(0x201D):
        dq += 1
print("-- remaining:", dq)
print("First 300 chars:", verify[:300])
