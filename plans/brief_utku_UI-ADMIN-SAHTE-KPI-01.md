# UI-ADMIN-SAHTE-KPI-01 — Brief (utku)

**Başlık:** [UI] Sahte API KPI kartını düzelt → admin_kpi.py rozetli boş kart (2s)
**Öncelik:** P0 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_kpi.py`

## Neden

`api_usage_daily` tablosu DB'de YOK (SSOT §8.4 EK BULGU-9). Kart bugün try/except içinde sessizce `0` dönüyor — kullanıcıya **sahte sayı** gösteriyoruz. Bu bir görsel hata değil, güven kaybı.

## Adımlar

1. `load_admin_kpi_summary()` **satır 41**, sorgu **satır 105** — `api_usage_daily` okunuyor.
2. Ortak yardımcı yaz: `tablo_var_mi(ad: str) -> bool` (sqlalchemy `inspect(engine).has_table`). Bu yardımcı UI-ADMIN-SAHTE-EXEC-02'de de kullanılacak — ortak bir yere koy (`web_dashboard/tabs/_db_yardim.py` gibi).
3. Tablo yoksa `0` dönme; kartı `"veri kaynağı yok"` rozetiyle çiz (gri/pasif stil).
4. Sıfır yeni tablo, sıfır yeni bağımlılık.

## Kabul kriteri

- [ ] `api_usage_daily` yokken kart `0` değil, rozet gösteriyor.
- [ ] `tablo_var_mi()` için assert tabanlı 1 test (var olan + olmayan tablo).
- [ ] SSOT §7'de ilgili satır kanıtla güncellendi.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
