# Brif — ALTYAPI-IMPORT-TEKLES-01 (yasu)

## Görev Özeti
`trigger.py` kök-mutlak import yolu kullanıyor; modül repo dışından veya
farklı çalışma dizininden çağrılınca kırılıyor. Import yolunu tekleştir.

## Sorun (kanıt)
- `src/company_master/orchestrator/trigger.py:24` — kök-mutlak import.
- `pano_denetim.py` `ithalat_kontrol()` bunu uyarı olarak raporluyor.
- Aynı desen `gorev_at.py` / `gorev_kutusu.py` içinde `sys.path.insert` ile maskeleniyor.

## Yapılacak
1. `trigger.py:24` importunu paket-göreli (`from . import ...`) veya tam paket
   yoluna (`from src.company_master.orchestrator import ...`) sabitle — repoda
   hangisi baskınsa onu seç, ikisini karıştırma.
2. `python -c "from src.company_master.orchestrator import trigger"` repo kökünden çalışmalı.
3. `scripts/` altındaki `sys.path.insert` kancalarının hâlâ gerekli olup olmadığını
   kontrol et; gereksizse kaldırma, sadece raporla (kaldırma kararı D-77 orkestratörde).

## Çıktı
- `src/company_master/orchestrator/trigger.py` (tek satır import düzeltmesi)
- `tests/test_trigger_import.py` — modülün hem kökten hem `scripts/` bağlamından
  import edilebildiğini doğrulayan tek test.

## Doğrulama
```
python -m pytest tests/test_trigger_import.py -q
python scripts/pano_denetim.py
```
`pano_denetim.py` çıktısında import uyarısı kaybolmalı.

## Kurallar
- D-48: minimum diff. Import refactor'u fırsat bilip modülü yeniden yazma.
- Kilit al: `python scripts/gorev_kutusu.py al --ajan yasu --task-id ALTYAPI-IMPORT-TEKLES-01`

## Süre Tahmini
1s

## İlgili Nodlar
- [[AGENTS]]
