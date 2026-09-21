[[Huginn Data Insights/data/orchestrator/REPO-HIJYEN-01_envanter.md]]

# REPO-HIJYEN-01 — Kök dizin artık envanteri (2026-09-15, roo)

Silme **yapılmadı**; karar Ürün Sahibi'nde. Her satır kök dizinde durup projeye ait görünmeyen geçici/çöp dosyadır.

| Dosya | Bayt | mtime (epoch) |
|---|---:|---:|
| `5.18.0` | 574 | 1789313699 |
| `^null` | 0 | 1789226014 |
| `__patch_admin.py` | 1569 | 1789438383 |
| `__probe.py` | 529 | 1789438316 |
| `_chart.txt` | 340 | 1789432727 |
| `_check.py` | 1430 | 1789404136 |
| `_check_tasks.py` | 309 | 1789209062 |
| `_onay.txt` | 3828 | 1789432727 |
| `_script.py` | 5258 | 1789404085 |
| `ANA_KURALLAR.md.bak` | 3881 | 1788823580 |
| `analyze_websites.py` | 1031 | 1788906937 |
| `apply_admin_login.py` | 2400 | 1789246650 |
| `Başlıksız 1.base` | 39 | 1789266004 |
| `Başlıksız 2.base` | 39 | 1789266005 |
| `Başlıksız 3.base` | 39 | 1789266016 |
| `Başlıksız.base` | 39 | 1789266002 |
| `check_payload_quality.py` | 1923 | 1789071450 |
| `check_plan.py` | 374 | 1789429725 |
| `find_brief.py` | 439 | 1789440920 |
| `find_poback.py` | 1344 | 1789450669 |
| `find_t01.py` | 633 | 1789440915 |
| `fix_bom.py` | 238 | 1789071450 |
| `fix_destek.py` | 10912 | 1789459156 |
| `HATA` | 0 | 1789381618 |
| `hello.txt` | 7 | 1789171120 |
| `insert_sections.py` | 3499 | 1789438017 |
| `modify_task.py` | 753 | 1789434216 |
| `patch_career.py` | 827 | 1789070844 |
| `patch_career2.py` | 1873 | 1789070844 |
| `temp_task.json` | 1407 | 1789451094 |
| `test_import.py` | 196 | 1789458676 |
| `tmp_tb_src.txt` | 33606 | 1789240416 |
| `update_html.py` | 1946 | 1788765819 |
| `update_init.py` | 743 | 1789454735 |

Toplam: 34 dosya.

## Öneri
- Tek komutla `data/_arsiv_kok/` altına taşınsın (git'e girmesin), 7 gün sonra silinsin.
- `.gitignore`'a `/_*.py`, `/__*.py`, `/*.bak`, `/*.base` desenleri eklensin.
- Kök `test_import.py`, `run_tests.py` gerçekten kullanılıyorsa `scripts/` altına taşınsın.
  
## Uygulandi (2026-09-15, roo)  
- 35 kok dosya git mv ile data/_arsiv_kok/ altina; test_import.py scripts/ altina.  
- Dis dizinden 13 oge iceri tasindi (docs/po_notlari, data/demo, src/company_master/i18n, data/_arsiv_kok/dis). Disarida yalniz .pytest_cache kaldi.  
- Denetim: python scripts/proje_siniri_denetim.py -
