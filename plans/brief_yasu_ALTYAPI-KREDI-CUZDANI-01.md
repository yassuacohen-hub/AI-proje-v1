# ALTYAPI-KREDI-CUZDANI-01 — Brief (yasu)

**Başlık:** [ALTYAPI] F3 kredi cüzdanı: kullanim_log + kredi_hareket şeması ve yazma kapısı → 0050_kredi_cuzdani.sql + kredi.py (4s)
**Öncelik:** P1 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `migrations/0050_kredi_cuzdani.sql`, `src/company_master/kredi.py`, `tests/test_kredi.py`
**Bağımlılık:** yok (F2 ile paralel; `arac_dongusu.py`'ye dokunmaz)
**Hub:** `hubs/MUSTERI_PANELI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.
**Son tarih:** 2026-10-06 18:00

## Neden
- `docs/BORC_DEFTERI.md:69` `BORC-KREDI-PAKET-01` — "PREMIUM internete çıkış için kredi/paket/kota tablosu yok (F0 ölçümü); F3 öncesi şema + yazma kapısı gerekir."
- `docs/PAKET_KOTA_TASARIMI.md` §5 — en az şema: `kullanim_log(id, company_id, tur, kaynak_adi, maliyet_kredi, ts)` + `kredi_hareket(id, company_id, miktar, neden, ts)`. Tasarım var, kod yok.
- `docs/PAKET_KOTA_TASARIMI.md` §7 sıra 3-4: önce `kullanim_log` + kota, cüzdan + webhook **ilk ödeme talebi gelince**. Bu brief sıra 3 + cüzdanın yalnız şema/yazma kapısı; webhook kapsam dışı.

## Doğrulanacak varsayım
- Son migration numarası `0049_fit_*.sql` (VERI-SKOR-MOTORU-01). Farklıysa numarayı kaydır, çakışma yaratma.
- `companies.id` birincil anahtar; `company_packages` tablosu 0 kayıt (`scripts/paket_olc.py`). 0 ise seed yazma, yalnız şema.
- `paketler.PAKET_KAYNAKLARI` dict var (commit `55b1dcbf`); kota sayacı bu dict'ten kaynak adını okur.
- Ürün sahibi matrisi (`PAKET_KOTA_TASARIMI.md` §3) **öneri**; sayısal eşikler koda sabitlenmez, `packages.features` JSON'dan okunur. Kolon yoksa **dur**, chat'e yaz.

## Adımlar
1. `migrations/0050_kredi_cuzdani.sql`: iki tablo + `company_id` FK + `ts` index. Idempotent (`IF NOT EXISTS`).
2. `src/company_master/kredi.py`: `kullanim_yaz(company_id, tur, kaynak_adi, maliyet_kredi)`, `bakiye(company_id) -> int` (SUM kredi_hareket − SUM kullanim_log), `dusebilir_mi(company_id, maliyet) -> bool`. Üç fonksiyon, sınıf yok.
3. Yazma kapısı: `dusebilir_mi` False ise `kullanim_yaz` `KrediYetersiz` fırlatır. Mimir'de çağrı noktası **bu görevde eklenmez** (salih `mimir_servis.py` kilidi); yalnız fonksiyon hazır olur.
4. `tests/test_kredi.py`: sqlite/in-memory veya mevcut test DB fixture'ı ile 4 test: boş bakiye 0; yükleme sonrası bakiye; düşme; yetersizde hata.
5. `BORC_DEFTERI.md` `BORC-KREDI-PAKET-01` satırını "KISMEN — şema+kapı var, Mimir çağrısı + webhook açık" yap.

## Kabul kriteri
- [ ] Migration uygulanır, iki tablo `\d` ile görünür (çıktı brief'e yapıştırılır).
- [ ] `tests/test_kredi.py` 4/4 yeşil.
- [ ] `kredi.py` ≤ 80 satır; yeni bağımlılık yok.
- [ ] Webhook/ödeme sağlayıcı kodu YOK (YAGNI — ilk ödeme talebi gelince).

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut DB bağlantı yardımcısı ile çöz.
- `git add -A` yasak; `--no-verify` yasak.
- **Teslimden önce** `hubs/MUSTERI_PANELI_HUB.md` "Kapanan işler" bölümüne `ALTYAPI-KREDI-CUZDANI-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
```bash
python scripts/ajan_chat.py ac ihsan ALTYAPI-KREDI-CUZDANI-01 "<sorun>" --cozum "<oneri>" --kimden yasu
python scripts/ajan_chat.py oku --task-id ALTYAPI-KREDI-CUZDANI-01
```

## Teslim
```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-KREDI-CUZDANI-01 --ozet "<özet>"
python scripts/gorev_kutusu.py bak --ajan yasu
python scripts/ajan_chat.py oku --son 10
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/docs/PAKET_KOTA_TASARIMI]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]
- [[plans/_brief_sablon]]
