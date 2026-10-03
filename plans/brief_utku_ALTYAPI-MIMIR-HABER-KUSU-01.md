# ALTYAPI-MIMIR-HABER-KUSU-01 — Brief (utku)

**Başlık:** [ALTYAPI] F2 haber kuşu: KAYNAK_HARITASI'nı paket kaynaklarıyla genişlet → arac_dongusu.py + test (3s)
**Öncelik:** P1 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/odin_ai/arac_dongusu.py`, `tests/test_arac_dongusu_kaynak.py`
**Bağımlılık:** yok (salih'in kilidi yalnız `mimir_servis.py`; bu dosyaya dokunmaz)
**Hub:** `hubs/TOOLS_SCRIPTS_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.
**Son tarih:** 2026-10-05 18:00

## Neden
- `src/company_master/odin_ai/arac_dongusu.py:58` — `ponytail: 3 adres; F2 haber kuşu aynı haritayı genişletir`. F2 bu satırı kapatır.
- `docs/BORC_DEFTERI.md:67` `BORC-EKAP-CLOUDFLARE-01` — "haber kuşu EKAP'sız başlar". EKAP bu görevin **kapsamı dışı**.
- `docs/PAKET_KOTA_TASARIMI.md` §4 — paket başına kaynak listesi `paketler.PAKET_KAYNAKLARI` / `firma_haber_kaynaklari()` (commit `55b1dcbf`). Haber kuşu bu listeden beslenmeli; ikinci bir kaynak listesi açılmaz.

## Doğrulanacak varsayım
- `arac_dongusu.py:59` `KAYNAK_HARITASI: dict[str, str]` 3 kayıt. Farklıysa **dur**, chat'e yaz.
- `paketler.py` içinde `PAKET_KAYNAKLARI` dict ve `firma_haber_kaynaklari(company_id)` var varsayıldı (commit `55b1dcbf`). İmza farklıysa **dur**.
- `docs/SAGLAYICI_OLCUMU_2026-10-03.md` §3: DMO liste düz HTTP 200, Resmî Gazete jina ile okunuyor. Yeni adresler **önce `web_fetch` ile ölçülür**, 200 dönmeyen harita'ya girmez.
- EKAP (Cloudflare) ve Apify kapsam dışı; `VERI-APIFY-BUTCE-01` ayrı görev.

## Adımlar
1. Aday kaynakları ölç: DMO e-Satış, Resmî Gazete ihale ilanları, KAP bildirim listesi, TOBB haber. Her biri için `fetch-combo` ile tek çağrı; sonuç `docs/HABER_KUSU_KAYNAK_OLCUMU.md` tablosuna (adres, HTTP, süre, karakter).
2. 200 dönenleri `KAYNAK_HARITASI`'na ekle; `ponytail` satırını güncelle (kaç adres, ne zaman genişler).
3. `firma_haber_kaynaklari()` ile harita arasında köprü: haritadaki her anahtar `PAKET_KAYNAKLARI` içinde geçen bir kaynak adıyla eşleşsin; eşleşmeyen varsa chat'e yaz, uydurma.
4. `tests/test_arac_dongusu_kaynak.py`: (a) haritadaki her URL `getir_izinli_mi` → `None`; (b) her URL `https://`; (c) harita anahtarları paket kaynak adlarıyla kesişiyor. 3 test, ağ yok.
5. `python -m pytest tests/test_arac_dongusu_kaynak.py -q` yeşil → teslim.

## Kabul kriteri
- [ ] `KAYNAK_HARITASI` ≥ 6 adres, hepsi ölçüm dokümanında 200 satırıyla kanıtlı.
- [ ] `tests/test_arac_dongusu_kaynak.py` 3/3 yeşil.
- [ ] `docs/HABER_KUSU_KAYNAK_OLCUMU.md` tablo + `## Ilgili Nodlar`.
- [ ] EKAP/Apify dokunulmadı; `BORC_DEFTERI.md` `BORC-EKAP-CLOUDFLARE-01` ACIK kaldı.

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; `WebIstemcisi` + mevcut `fetch-combo` ile çöz.
- `git add -A` yasak; `--no-verify` yasak.
- **Teslimden önce** `hubs/TOOLS_SCRIPTS_HUB.md` "Kapanan işler" bölümüne `ALTYAPI-MIMIR-HABER-KUSU-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
```bash
python scripts/ajan_chat.py ac ihsan ALTYAPI-MIMIR-HABER-KUSU-01 "<sorun>" --cozum "<oneri>" --kimden utku
python scripts/ajan_chat.py oku --task-id ALTYAPI-MIMIR-HABER-KUSU-01
```

## Teslim
```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-MIMIR-HABER-KUSU-01 --ozet "<özet>"
python scripts/gorev_kutusu.py bak --ajan utku
python scripts/ajan_chat.py oku --son 10
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/docs/SAGLAYICI_OLCUMU_2026-10-03]]
- [[Huginn Data Insights/docs/PAKET_KOTA_TASARIMI]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]
- [[plans/_brief_sablon]]
