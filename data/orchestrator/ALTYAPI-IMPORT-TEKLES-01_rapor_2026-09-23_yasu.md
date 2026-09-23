# ALTYAPI-IMPORT-TEKLES-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı

## Değişiklik — `src/company_master/orchestrator/trigger.py`

4 kök-mutlak import → **paket-göreli** yapıldı (D-48 minimum diff):

| Satır | Eski | Yeni |
|---|---|---|
| 24 | `from src.company_master.orchestrator import task_board as tb` | `from . import task_board as tb` |
| 274 | `from src.company_master.orchestrator import isbirligi` (lokal) | `from . import isbirligi` |
| 305 | `from src.company_master.orchestrator import duzen` (lokal) | `from . import duzen` |
| 386 | `from src.company_master.orchestrator import duzen` (lokal) | `from . import duzen` |

**Neden görel?** Brief iki seçenek sunuyordu (paket-göreli ya da `src.` tam yol).
Pakette `src.` öneki baskın olsa da **yalnız kök sys.path bağlamında çalışıyor**;
`sys.path=src` ile import edildiğinde kırılıyordu (pano_denetim'in `ithalat_kontrol`
uyarısının kök nedeni). Görel import her iki bağlamda da çalışır ve tek
task_board modül örneği garantiler (çift-modül kimlik sorunu yok).

## Test — `tests/test_trigger_import.py` (4 test, hepsi PASSED)

1. ✅ kök bağlamı: `from src.company_master.orchestrator import trigger` (scripts yolu)
2. ✅ paket bağlamı: `sys.path=src` + `from company_master.orchestrator import trigger`
3. ✅ uzak cwd + `sys.path=src` (kok-mutlak import artık yok)
4. ✅ `gorev_kutusu.py --help` scripts bağlamında çalışıyor (kritik çağıran regresyon)

**Sonuç: 4/4 PASSED (0.56s)**

## Doğrulama

```
python scripts/pano_denetim.py
→ [PANO-DENETIM] status=ok hata=0 uyari=8 (ithalat uyarisi YOK)
```
Önceki koşulda 11 uyarı vardı; ithalat + arşiv temizliğiyle 8'e indi.

## md.3 Raporu: scripts/ sys.path.insert kancaları

`gorev_at.py`, `gorev_kutusu.py`, `gorev_nobetci.py` vb. hâlâ
`sys.path.insert(0, repo_koku)` kullanıyor — **hâlâ gerekli** (bunlar script
değil modül; kökten import için kanca şart). trigger.py görel olduktan sonra
kancalar zararsız; **kaldırma önerilmiyor** (D-77: kaldırma kararı orkestratörde,
bu görev kapsam dışı).

## Not

`__init__.py` docstring'inde örnek importlar `from src.company_master...`
kalıyor (sadece dokümantasyon). Paket genelinde `src.` deseni (duzen.py,
isbirligi.py, cli.py vb.) ayrı bir teknik borç — aynı tedavi ayrı görev olmalı
(bu görev D-48 kapsamını aştı).
