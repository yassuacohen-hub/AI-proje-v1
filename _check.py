import os
base = r"C:\Huginn Data Projesi\Huginn Data Insights"

# Check specific Turkish strings in ANA_KURALLAR.md
p1 = os.path.join(base, "ANA_KURALLAR.md")
text1 = open(p1, encoding="utf-8").read()

# Find 'müteri' in the text
idx = text1.find("müteri")
print(f"ANA_KURALLAR.md - find 'müteri': index={idx}")
if idx >= 0:
    print(f"  Context: ...{text1[max(0,idx-10):idx+20]}...")

idx2 = text1.find("Görsel")
print(f"ANA_KURALLAR.md - find 'Görsel': index={idx2}")
if idx2 >= 0:
    print(f"  Context: ...{text1[max(0,idx2-10):idx2+20]}...")

idx3 = text1.find("Kural 7")
print(f"ANA_KURALLAR.md - find 'Kural 7': index={idx3}")

# Check specific Turkish strings in AGENTS.md
p2 = os.path.join(base, "AGENTS.md")
text2 = open(p2, encoding="utf-8").read()
idx4 = text2.find("müteri")
print(f"AGENTS.md - find 'müteri': index={idx4}")
if idx4 >= 0:
    print(f"  Context: ...{text2[max(0,idx4-10):idx4+20]}...")

idx5 = text2.find("Koyu yeşil")
print(f"AGENTS.md - find 'Koyu yeşil': index={idx5}")
if idx5 >= 0:
    print(f"  Context: ...{text2[max(0,idx5-10):idx5+25]}...")

# Check byte-level correctness for Turkish chars
# In UTF-8: ü = C3 BC, ç = C3 A7, ğ = C4 9F, ş = C5 9F, ö = C3 B6, ı = C4 B1, İ = C4 B0, İ = C4 B0
print()
print("Byte-level check for 'müteri' in ANA_KURALLAR.md:")
b = text1.encode("utf-8")
expected = "müteri".encode("utf-8")
print(f"  'müteri' in bytes: {expected in b}")
