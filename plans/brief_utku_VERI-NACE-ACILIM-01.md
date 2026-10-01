# VERI-NACE-ACILIM-01 — Brief (utku)

**Başlık:** [VERI] NACE açılımını yaz → sunum.acilim_getir + müşteri kartı (3s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/sunum.py, web_dashboard/tabs/admin_musteriler.py`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden
`AGENTS.md:3848-3850` (D-268 §3): `nace_codes` tablosunda 6387/8289 kodun
`title` (açılım) metni dolu — 1902 açılımsız olduğu da ölçüldü. Ama bu veriyi
okuyan `acilim_getir` fonksiyonu kodda **hiç yok** (D-266: önce çağıran kurulur,
sonra düzeltme yapılır). `nace_codes.title` kolonu `0002_relations.sql:64`'te
tanımlı. Mevcut tek kapı `src/company_master/sunum.py:128` (`nace_metni`) sadece
kodu+etiketini basıyor, açılım metnini basmıyor.

## Doğrulanacak varsayım
- `nace_codes.title` kolonu açılımı taşıyor varsayıldı (`0002_relations.sql:64`). Boşsa/başka anlam taşıyorsa **dur**, panoya sorun aç.
- `company_master/sunum.py` NACE sunumunun tek kapısı varsayıldı (D-252). Yeni fonksiyon buraya eklenir, başka dosyaya kopya yazılmaz.
- `web_dashboard/tabs/admin_musteriler.py` firma detay ekranının NACE kodunu gösterdiği yer varsayıldı. Farklıysa **dur**, gerçek çağıran dosyayı bul, panoya not düş.

## Adımlar
1. `sunum.py`'ye `acilim_getir(nace_code: str | None) -> str` yaz: `nace_codes.title`'ı DB'den okur, boşsa `BOS` döner (D-249 kuralı — "veri yok" 0/boş gibi gösterilmez ama farklı gösterilir), en az 1 doctest ekle.
2. `admin_musteriler.py` (ya da gerçek firma-detay bileşeni neyse) içine çağıran ekle: NACE kodu yanında açılım metni görünür hale gelsin.
3. Doğrulama: DB'den açılımı dolu bir örnek NACE kodu (`SELECT nace_code FROM nace_codes WHERE title IS NOT NULL LIMIT 1`) ile ekranda metni gerçekten çıktığını göster.

## Kabul kriteri
- [ ] `acilim_getir()` `sunum.py`'de var, en az 1 doctest çalışıyor.
- [ ] Bir ekranda açılım metni gerçekten görünüyor (manuel kontrol veya test).
- [ ] `pytest tests/test_panel_durustluk.py` yeşil kalıyor (regresyon yok).

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-NACE-ACILIM-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:
- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Gerçek çağıran dosya farklıysa → sorun aç, bulduğun dosyayı yaz.

```bash
python scripts/ajan_chat.py ac utku VERI-NACE-ACILIM-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-NACE-ACILIM-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-NACE-ACILIM-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-NACE-ACILIM-01 --ozet "<özet>"
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[plans/_brief_sablon]]
