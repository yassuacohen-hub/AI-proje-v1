# VERI-NACE-SOZLUK-DIL-01 — Brief (utku)

**Başlık:** [VERI] NACE sözlük başlıklarını düzelt → 572 TR karakter (4s)
**Öncelik:** P2 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/nace_sozluk_yukle.py, data/nace/sektor_meslek_nace_2026-05_resmi.xlsx`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden
`AGENTS.md:3851-3853` (D-268 §3): `nace_codes` tablosunda 3319 satırın 572'si
Türkçe karakter taşıyan başlıkta yarım-ASCII'leşmiş (mojibake değil — harf
düşmesi: "İmalatı" → "malat" gibi). Devir notu çözümü "TUIK listesi indirmeye
bağlı" diyordu — **ama bu önkoşul şüpheli**: SHA256 karşılaştırmasıyla
`data/nace/sektor_meslek_nace_2026-05_resmi.xlsx` (kodun okuduğu dosya) ile
kullanıcının elindeki "resmi kaynak" (`SektörMeslekNace_2026.01.01 güncel Mayıs
2026.xlsx`, workspace kökü) **birebir aynı dosya** (hash: `6a5b5ee9...fe0ab8`).
Yani resmi kaynak zaten yüklü — sorun muhtemelen kaynak dosyada değil,
`nace_sozluk_yukle.py` yükleme/encoding adımında.

## Doğrulanacak varsayım
- Kaynak xlsx (`data/nace/sektor_meslek_nace_2026-05_resmi.xlsx`) ile kullanıcının
  gösterdiği dosya aynı varsayıldı — **doğrulandı** (SHA256 eşleşti, 2026-10-01).
  Yani "TUIK indir" ön-adımı muhtemelen GEREKSİZ; önce xlsx içeriğini kontrol et.
- `nace_sozluk_yukle.py`'nin kaynak öncelik sırası `xlsx_resmi > xlsx_derived >
  turkiye_nace_json > ...` varsayıldı (dosyada arandı, satır no teyit edilmeli —
  bulamazsan **dur**, panoya sorun aç).
- 572 mojibake'li satırın hepsinin aynı kök sebepten (encoding) geldiği varsayıldı.
  Farklı kaynaklardan karışık geliyorsa **dur**, KAHİN'e sor.

## Adımlar
1. **Faz A — Kök neden teşhisi:** xlsx'te 2-3 bilinen bozuk NACE başlığını
   (ör. `nace_codes.title` yarım-ASCII olan bir satır) excel'de aç, kaynak
   hücre doğru Türkçe mi kontrol et. Doğruysa sorun yükleyicide; bozuksa
   sorun kaynakta (TUIK indirme gerçekten gerekli).
2. **Faz B — Düzeltme:** Faz A sonucuna göre ya `nace_sozluk_yukle.py`'deki
   encoding/okuma adımını düzelt ve yeniden yükle, ya da (xlsx bozuksa) gerçek
   TUIK indirmesini panoya ayrı iş olarak aç (bu brif'i genişletme).
3. **Doğrulama:** `SELECT count(*) FROM nace_codes WHERE title ~ '<bozukluk deseni>'`
   572'den 0'a indiğini ölç; canlı DB'de çalıştır (D-238).

## Kabul kriteri
- [ ] Faz A kök neden bulgusu `dosya:satır` ile raporlanmış.
- [ ] Faz B sonrası canlı DB ölçümü: bozuk başlık sayısı 572 → ölçülen yeni değer (hedef 0, mümkün değilse gerekçeyle).
- [ ] Kaynak dosya gerçekten "TUIK'ten yeniden indirilmesi gerekiyor" ise bu bulgu panoya ayrı not olarak düşülmüş (uydurma blokaj yasak, D-65).

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-NACE-SOZLUK-DIL-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak:
- Faz A bulgusu "kaynak da bozuk" çıkarsa → sorun aç, TUIK indirme gerçek engel mi netleştir, **durma**.
- Varsayım tutmuyorsa → `ac` ile sorun aç, uydurma.

```bash
python scripts/ajan_chat.py ac utku VERI-NACE-SOZLUK-DIL-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-NACE-SOZLUK-DIL-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-NACE-SOZLUK-DIL-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-NACE-SOZLUK-DIL-01 --ozet "<özet>"
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[plans/_brief_sablon]]
