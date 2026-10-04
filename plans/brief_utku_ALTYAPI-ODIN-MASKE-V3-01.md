# ALTYAPI-ODIN-MASKE-V3-01 — Brief (utku)

**Başlık:** [ALTYAPI] maskeleme_odin() V1/V2/V3 kaynak ayrımı + V3 endpoint (2s)
**Öncelik:** P1 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/sunum.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14).

## Neden
[`sunum.py:281`](Huginn Data Insights/src/company_master/sunum.py:281) `maskeleme_odin(metin, hedef="musteri")`
yalnız `hedef` alır (`musteri`/`ic`); `kaynak`/versiyon parametresi yok. V1/V2/V3
ayrımı kodda uygulanmıyor — utku'nun ölçümü doğru, V3 endpoint bu parametre
eklenmeden yazılamaz (utku chat kaydı, 2026-10-04).

## Doğrulanacak varsayım
- `maskeleme_odin()` imzası şu an `(metin: str | None, hedef: str = "musteri")`.
  Farklıysa **dur**, panoya sorun aç.
- V1/V2/V3 ayrımının ne anlama geldiği (hangi alan/desen farklı maskelenir)
  utku'nun önceki ödin görevlerinde tanımlı değilse → KAHİN'e chat ile sor,
  uydurma.

## Adımlar
1. `maskeleme_odin()`'e `kaynak: str = "v1"` (veya tanımlı sürüm adları) parametresi ekle.
2. V1/V2/V3 için hangi `_ODIN_YASAK_DESENLER` alt kümesinin uygulanacağını netleştir (gerekirse KAHİN'e chat ile sor).
3. V3 endpoint + filtre ekle (mevcut sunum katmanına, yeni dosya açma — D-220).
4. Testleri güncelle (`tests/` altında `sunum.py` testleri).

## Kabul kriteri
- [ ] `maskeleme_odin()` `kaynak` parametresiyle çağrılabiliyor, testle kanıtlı.
- [ ] V3 endpoint çalışıyor, mevcut testler kırılmıyor (`pytest tests/ -q`).

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme.
- Teslimden önce `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne satır yaz.

## Ajan chat zorunlu (D-210 · D-217)
```bash
python scripts/ajan_chat.py ac utku ALTYAPI-ODIN-MASKE-V3-01 "<sorun>" --cozum "<oneri>"
```

## Teslim
```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-ODIN-MASKE-V3-01 --ozet "<özet>"
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/src/company_master/sunum.py]]
