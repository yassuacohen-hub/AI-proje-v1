# UI-ADMIN-SAHTE-EXEC-02 — Brief (utku)

**Başlık:** [UI] Sahte gelir kartlarını düzelt → admin_executive.py rozetli boş kart (2s)
**Öncelik:** P0 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_executive.py`

## Neden

`packages` ve `company_packages` tablolarının **ikisi de** DB'de yok (SSOT §8.4 EK BULGU-10). MRR / ARR / ARPA / Churn kartlarının tamamının gerçek veri kaynağı sıfır. SSOT §7 bunları yanlışlıkla "Var" saymıştı.

## Adımlar

1. `load_executive_ozet()` **satır 74** — `company_packages ⋈ packages` sorgusu.
2. UI-ADMIN-SAHTE-KPI-01'in `tablo_var_mi()` yardımcısını kullan (önce o görev bitmeli ya da yardımcıyı ilk kim yazarsa o paylaşır).
3. Eksik tabloda 4 kartı da `"veri kaynağı yok"` rozetiyle çiz.
4. Bu görev **tablo oluşturmaz** — faturalama P3'te ertelendi (SSOT §13).

## Kabul kriteri

- [ ] Executive sekmesi hata vermiyor, 4 kart rozetli.
- [ ] SSOT §7'de MRR/ARR/ARPA/Churn satırları `Var` → gerçek duruma düzeltildi.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
