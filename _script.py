import os

base = r"C:\Huginn Data Projesi\Huginn Data Insights"

# ============ FILE 1: ANA_KURALLAR.md ============
path1 = os.path.join(base, "ANA_KURALLAR.md")
content1 = open(path1, encoding="utf-8").read()
marker = "Kural 7: Marka Terminolojisi"
if marker not in content1:
    lines = content1.split("\n")
    section = """## Kural 7: Marka Terminolojisi ve Görsel Kimlik — Huginn / Muninn / Odin

### Marka Kimliği

| Terim | Tanım | Kullanım Alanı |
|-------|-------|----------------|
| **Huginn** | Ana uygulama — müşteri yüzeyi | Web UI, mobil, API (müşteri portali) |
| **Muninn** | Admin / insider paneli | İç ekip yönetim paneli, analitik, denetim |
| **Odin** | Entegrasyon orchestrator | Backend entegrasyon motoru, ETL, otomasyon |

### Marka İllüstrasyonları (örnek metinler)

- Huginn: "Bilgi akışı seninle dans eder"
- Muninn: "Güç, kontrol ve derinlemesine analiz"
- Odin: "Veriyi zekâya dönüştür"

### Marka Renkleri

| Marka | Ana Renk | Kullanım |
|-------|----------|----------|
| Huginn | Lacivert (#1E3A5F) | Ana uygulama ana tonu, ana butonlar |
| Muninn | Koyu yeşil (#2D5F2D) | Admin paneli tonu, yönetim bileşenleri |
| Odin | Turuncu (#D97706) | Entegrasyon motoru, otomasyon bildirimleri |

### Logo Kullanım Kuralları
- Logo dosyaları `AI proje v1/V10/03_marka_konumlandirma_ve_kapsam.md` bölümünde tutulur
- Her marka için ayrı logo kullanılır; karıştırılmamalı
- Logo minimum boyutu korunmalıdır; stres altında veya küçültülmüş kullanım yasaktır
- Arka plan kontrastı okunabilirliğini karşılamalıdır

### Görsel Stil
- Minimalist, veri odaklı, kompozisyon basittir
- Fazla dekoratif öğe kullanılmaz; veri sunumu önceliklidir
- Simgeler ve ikonlar tutarlı bir ikonografikle oluşturulmalıdır

### Görsel Varlık Yönetimi
- Tüm görsel varlıklar (logo, banner, ikon, renk paleti) kaynak belgede kayıt altındadır
- Güncellemeler yalnızca yetkili kullanıcılar tarafından yapılabilir
- Versiyon kontrolü her güncelleme için zorunludur
"""
    target_line = None
    for i, line in enumerate(lines):
        if line.startswith("## Kural 6:"):
            target_line = i
            break
    if target_line is None:
        target_line = 66
    else:
        target_line = target_line - 1
    lines.insert(target_line + 1, section)
    new_content1 = "\n".join(lines)
    open(path1, "w", encoding="utf-8").write(new_content1)
    print(f"ANA_KURALLAR.md: inserted Kural 7, total lines now: {len(lines)}")
else:
    print("ANA_KURALLAR.md: Kural 7 already exists, skipped")

# ============ FILE 2: AGENTS.md ============
path2 = os.path.join(base, "AGENTS.md")
content2 = open(path2, encoding="utf-8").read()
section2 = """
---

## Marka Terminolojisi

- **Huginn** (Ana Uygulama): Müşteri yüzeyi, ana uygulama, API (müşteri portali). Lacivert (#1E3A5F).
- **Muninn** (Admin/Insider Panel): İç ekip yönetim paneli, analitik, denetim. Koyu yeşil (#2D5F2D).
- **Odin** (Entegrasyon Orchestrator): Backend entegrasyon motoru, ETL, otomasyon. Turuncu (#D97706).
- Kullanıcıla konuşurken bu terimleri karıştırma; her biri kendi bağlamı ve kapsamıdır.
- Detaylar için: `AI projet v1/V10/03_marka_konumlandirma_ve_kapsam.md`
"""
if "## Marka Terminolojisi" not in content2:
    content2 = content2.rstrip("\n") + section2
    open(path2, "w", encoding="utf-8").write(content2)
    print(f"AGENTS.md: appended Marka Terminolojisi, total lines: {content2.count(chr(10))+1}")
else:
    print("AGENTS.md: Marka Terminolojisi already exists, skipped")

# ============ FILE 3: .roorules ============
path3 = os.path.join(base, ".roorules")
content3 = open(path3, encoding="utf-8").read()
section3 = """
## Marka Terminolojisi (Huginn / Muninn / Odin)

- Huginn = ana uygulama (müşteri), Muninn = admin paneli (iç ekip), Odin = entegrasyon orchestrator (backend).
- Detaylar: `AI projet v1/V10/03_marka_konumlandirma_ve_kapsam.md`
"""
if "Marka Terminolojisi" not in content3:
    content3 = content3.rstrip("\n") + section3
    open(path3, "w", encoding="utf-8").write(content3)
    print(f".roorules: appended Marka Terminolojisi, total lines: {content3.count(chr(10))+1}")
else:
    print(".roorules: Marka Terminolojisi already exists, skipped")

# ============ FILE 4: .clinerules ============
path4 = os.path.join(base, ".clinerules")
content4 = open(path4, encoding="utf-8").read()
section4 = """
## Marka Terminolojisi (Huginn / Muninn / Odin)

- Huginn = ana uygulama (müşteri), Muninn = admin paneli (iç ekip), Odin = entegrasyon orchestrator (backend).
- Detaylar: `AI projet v1/V10/03_marka_konumlandirma_ve_kapsam.md`
"""
if "Marka Terminolojisi" not in content4:
    content4 = content4.rstrip("\n") + section4
    open(path4, "w", encoding="utf-8").write(content4)
    print(f".clinerules: appended Marka Terminolojisi, total lines: {content4.count(chr(10))+1}")
else:
    print(".clinerules: Marka Terminolojisi already exists, skipped")

# Verification — Turkish chars
for p in [path1, path2, path3, path4]:
    c = open(p, encoding="utf-8").read()
    has_turkish = any(ch in c for ch in "çğıöşüÇĞIÖŞÜ")
    print(f"{os.path.basename(p)}: {len(c)} chars, Turkish chars OK: {has_turkish}")
