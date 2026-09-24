# UI-ADMIN-GUNCELLIK-KOVA-10 — Brief (utku)

**Başlık:** [UI] Veri güncellik kovalarını yaz → admin_quality.py dağılımı (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_quality.py`

## Neden

SSOT §9 K3 — veri güncellik kovaları yok. Girdisi **mevcut** (`updated_at`), ek tablo gerekmiyor; etki/efor oranı yüksek.

## Adımlar

1. `admin_quality.py`'ye `updated_at` yaşına göre kova dağılımı sorgusu ekle.
2. Kovalar: 0-7g / 8-30g / 31-90g / 90g+ (SSOT §9 K3).
3. Görselleştirme **Plotly** veya `st.dataframe` — AgGrid reddedildi (SSOT §13).

## Kabul kriteri

- [ ] Kova dağılımı görünüyor, boş tabloda hata vermiyor.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
