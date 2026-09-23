# ORKESTRA-ONAY-BOSALT-01 — Onay kuyrugundaki 9 teslimi denetle

## Gorev Ozeti
Onay kuyrugunda **9 teslim** birikti; en eskisi 09-19'dan beri bekliyor. Kuyruk
tikandigi icin bitmis isler `done` olmuyor, dosya kilitleri dusmuyor, sprint
kapatilamiyor. Bu gorev kuyrugu bosaltir.

## Mevcut Durum (kanit: `python scripts/gorev_at.py pano`)

| Task | Ajan | Teslim | Yas |
|---|---|---|---|
| BRIK-00 | ihsan | 09-19 03:48 | ~4 gun |
| REVIEW-ONAY-KUYRUGU-01 | yasu | 09-20 23:45 | ~2 gun |
| DOC-SIRKET-MASTER-01 | utku | 09-22 06:09 | ~1 gun |
| ALTYAPI-KILIT-YOL-FIX-01 | utku | 09-22 06:55 | ~1 gun |
| ALTYAPI-PANO-ENCODING-FIX-01 | utku | 09-22 07:12 | ~1 gun |
| AGENTS-MERGE-UU | ihsan | 09-23 10:42 | bugun |
| ADMIN-UI-CACHE-OPT-01 | yasu | 09-23 10:49 | bugun |
| GRAPH-CANONICAL-SECER-02 | yasu | 09-23 10:49 | bugun |
| VAULT-CLEANUP-BATCH | ihsan | 09-23 10:50 | bugun |

## Is Maddeleri
1. `python scripts/gorev_kutusu.py onay-bekleyen` ile listeyi al (SSOT budur, ustteki tablo anlik kopyadir).
2. **Her teslim icin** sirayla:
   - Teslim ozetindeki cikti dosyalari diskte var mi?
   - Ilgili rapor dosyasi (`data/orchestrator/<TASK>_rapor_*.md`) var mi? (D-67)
   - Kod degistiyse ilgili test yesil mi? `python -m pytest <test> -q`
3. Karar:
   - Temizse: `python scripts/gorev_kutusu.py onayla --task-id <TASK> --ben salih`
   - Eksikse: `python scripts/gorev_kutusu.py reddet --task-id <TASK> --ben salih --neden "<tek cumle>"`
4. **Reddetme esigi dusuk tutulmayacak:** suphede birak, reddet + neden yaz. Sessiz onay yasak.
5. Rapor yaz: `data/orchestrator/ORKESTRA-ONAY-BOSALT-01_rapor_2026-09-23_salih.md`
   — her task icin tek satir: `TASK | onay/red | gerekce`.

## Kurallar
- D-78: SALIH otomatik onay yetkisine sahiptir; bu gorev o yetkinin kullanimidir.
- D-67: rapor zorunlu, bulgu cikarsa raporda ayri baslik.
- D-86: Windows cmd.exe — cok satirli `python -c` yasak.
- D-183: rapor dosya adi `_salih` son ekiyle biter.

## Teslim
```
python scripts/gorev_kutusu.py teslim --task-id ORKESTRA-ONAY-BOSALT-01 --ajan salih --ozet "<9 teslim denetlendi: N onay / M red>" --cikti data/orchestrator/ORKESTRA-ONAY-BOSALT-01_rapor_2026-09-23_salih.md
```

## Sure Tahmini
4s

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
