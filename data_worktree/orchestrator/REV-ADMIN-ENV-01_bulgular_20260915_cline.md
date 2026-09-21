[[Huginn Data Insights/data/orchestrator/REV-ADMIN-ENV-01_bulgular_20260915_cline.md]]

# REV-ADMIN-ENV-01 — İnceleme Bulguları (2026-09-15, cline)

Kapsam: `scripts/admin_sifre_sifirla.py`, `tests/test_admin_sifre_sifirla.py`,
`web_dashboard/tabs/admin_auth.py` (`_env_kimlik` ile `.env` ADMIN_EMAIL /
ADMIN_PASSWORD ön-dolumu). Yöntem: salt-okunur; kapsam-dışı bug DÜZELTİLMEDİ.

Teslim komiti: `7494051` (roo) — "app.py bozuk çalışma kopyası geri alındı".

## Karar: ONAY (2 koşulla)

Koşul-1 (yüksek): prod ortamında `.env` ön-dolumu kapatılmalı (B-1).
Koşul-2 (yüksek): `.pre-commit-config.yaml` UTF-16 LE BOM'lu commitlenmiş (B-5);
GUARD-ENC-01 kapsamında düzeltilecek (kilit bende).

## Test kanıtı

- `tests/test_admin_sifre_sifirla.py`: **6 passed** (hash uyumu, gerçek
  `web_app._verify_password` çapraz doğrulaması, env_upsert BOM'suzluk + yorum
  satırı koruma, kısa-şifre reddi, admin-yok hatası, başarı+env yazımı).
- `python scripts/kodlama_denetim.py`: kapsam dosyaları temiz; tek ihlal
  `tests/test_kariyernet.py` BOM (kapsam-dışı, kilo'nun aktif dosyası —
  dokunulmadı).

## Soru cevapları

### (1) `.env`'de düz şifre — risk ve prod kapatma

**Risk GERÇEK, kanıtlı.** `_env_kimlik()` (`admin_auth.py:9-23`) koşulsuz
`os.getenv("ADMIN_PASSWORD")` okuyup `st.text_input(..., type="password",
value=env_sifre)` ile forma gömüyor. `HUGINN_ENV`/prod kapısı **yok**
(`Select-String HUGINN_ENV` üç dosyada da sonuçsuz). `.env` gitignore'da
(`.gitignore:1,11-12`) ama koruma yalnızca depoya girişi engeller; riski
kapatmaz: yedek/screenshot/log sızıntısında düz şifre açığa çıkar, prod'da
açık kalırsa kalıcı arka kapı olur. `--env-yaz` bayrağı da düz şifreyi
`.env`'e yazar (`admin_sifre_sifirla.py:102`).

Öneri (takip görev): `HUGINN_ENV=prod` ise ön-dolum yok (e-posta dahil),
prod'da `ADMIN_PASSWORD` set edildiyse başlangıçta uyarı bas, `.env.example`'a
"yalnızca yerel geliştirme" notu ekle. **B-1 (yüksek).**

### (2) Hash formatı `web_app._hash_password` ile birebir mi?

**EVET — satır-satır aynı.** İkisi de: `os.urandom(16)` salt,
`hashlib.pbkdf2_hmac("sha256", ..., iter)`, format `pbkdf2$iter$salt$hash`;
doğrulamada `split("$")` + `hmac.compare_digest`. Sabitler eşit:
`web_app._PBKDF2_ITER = 120_000` == script `PBKDF2_ITER = 120_000`
(kaynak metinden regex ile doğrulandı; ilk okumada `120` görünmesi regex'in
`120_000` içindeki alt-çizgide durmasıydı — tam satır `120_000`).
Çapraz kanıt: `test_web_app_verify_ile_dogrulanir` gerçek
`web_app._verify_password` ile script hash'ini doğruluyor. **Bulgu yok.**

### (3) `env_upsert` BOM/CRLF davranışı

**BOM: doğru.** `utf-8-sig` ile okur (BOM varsa yutar), `utf-8` ile yazar
(BOM yazmaz); test BOM'suzluğu bayt düzeyinde assert ediyor
(`test_env_upsert_gunceller_ve_ekler`). Yorum satırları ve diğer anahtarlar
korunuyor, anahtar tekrar yazımında satır-içi replace (dosya sırası bozulmaz).

**CRLF: LF'ye normalize eder.** `splitlines()` + `"\n".join(...)` CRLF'yi
düşürür; git `autocrlf` uyarıları zaten LF yönünde. Zararsız.

**Küçük eksik (B-3, düşük):** değer quoting yok — şifrede `=`, `#`, ön/arka
boşluk veya satırsonu varsa `.env` parse'ı bozulur/kesilir. `python-dotenv`
tırnaksız `A=B#C` değerini olduğu gibi alır; `#` ayraç sayılmaz ama `=` içeren
değer ilk `=`'ten bölündüğü için SOL taraf korunur, yine de boşluklu/özel
değerler için tırnaklama önerilir.

### (4) app.py'ye BOM+mojibake+yanlış girintili 'Huginn Blog' — kim, tekrar önlemi

**Araştırma sonucu:**

- HEAD komitinde `app.py`'ye **dokunulmadı**: `git show HEAD --stat`'ta
  `app.py` yok (7 dosya: script + test + admin_auth + pano/senkron). "Geri
  alındı" ifadesi = commitlenmemiş çalışma-kopyası kirlenmesinin restore'u.
- Mevcut `app.py`: `Blog` stringi **yok**, BOM yok, `ast.parse` **OK**.
- `git log -- app.py`: son değişiklik `9265d8b` (UI-WIDE-01) — HEAD'den eski.
  `git reflog -- app.py` komutu asıldı (tamamlanamadı); log kanıtı yeterli:
  bozulma **hiç commitlenmedi**, fail forensic iz yok.
- UI-SIDEBAR-02 (kilo, review) ile **ilişki kanıtı yok** (kilo'nun kilitli
  dosyası `app.py`'de HEAD-dışı değişiklik yok, `git diff HEAD --stat`'ta
  `app.py` görünmüyor; güncel `git status` çıktısında da yok).

**Yorum:** IDE/araç kaynaklı çalışma-kopyası kirlenmesi (PowerShell
`Out-File` UTF-16 + yapıştırma girinti kayması profiliyle uyumlu) en olası
açıklama; faile dair git kanıtı yok. Tekrar önlemi = GUARD-ENC-01'in ta
kendisi: `kodlama_denetim.py`'ye `ast.parse` + BOM/NUL taraması + pre-commit
hook (kilidi bende, bu oturumda implemente ediliyor). Ek öneri: hook'a
`.yaml` dosyaları için `check-yaml` + NUL taraması ekle (B-5'in dersi).
**B-4 (orta, süreç).**

## Bulgu listesi

| # | Seviye | Dosya:satır | Bulgu |
|---|--------|-------------|-------|
| B-1 | Yüksek | `admin_auth.py:9-23` | Prod kapısı yok: `.env` düz şifresi her ortamda forma gömülür. `HUGINN_ENV=prod` ise ön-dolum yok + uyarı + `.env.example` notu (takip görev). |
| B-2 | Yüksek | `.pre-commit-config.yaml` | Çalışma kopyası **ve HEAD blob'u** UTF-16 LE BOM'lu (`FF FE`, NUL var, 536 bayt; `hash-object == ls-files` ile doğrulandı — bozukluk commitli). pre-commit/PyYAML bu dosyayı okuyamaz. GUARD-ENC-01'de düzeltilecek. |
| B-3 | Düşük | `admin_sifre_sifirla.py:57-59` | `env_upsert` değer quoting yapmıyor (`=`/`#`/boşluk içeren şifre riski). |
| B-4 | Orta (süreç) | — | app.py kirlenmesi commitlenmeden restore edildi; fail izi yok. Önlem: GUARD-ENC-01 hook'u + yaml NUL kontrolü. |
| B-5 | Bilgi | `tests/test_kariyernet.py` | Kapsam-dışı BOM ihlali (kilo aktif). Denetim exit 1 — CI kırmızısı kilo teslimine bağlı; dokunulmadı. |

## Notlar

- Konsol çıktıları bilinçli ASCII (`admin_sifre_sifirla.py:98`) — cp1254
  çökmesine karşı doğru karar; şifre/hash ekrana basılmıyor.
- `MIN_UZUNLUK = 8` + getpass çift-giriş + `verify` self-check'i yerinde.
- `db_sifre_guncelle` yalnızca `role='admin'` satırını günceller, `status`
  normalizasyonu yapar — yetki yükseltme vektörü yok.
- `.env.example`'da ADMIN_* anahtarı yok — ön-dolumun keşfedilebilirliği için
  örnek satırlar (değersiz) eklenebilir (takip).
