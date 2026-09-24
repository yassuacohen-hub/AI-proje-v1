# UI-ADMIN-MALIYET-ANOMALI-11 — Brief (utku)

**Başlık:** [UI] AI maliyet anomali bloğunu yaz → admin_cost.py z-skor (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_cost.py`

## Neden

SSOT §9 K5 — AI maliyet anomalisi panelde yok. Kural tabanlı, ML gerekmez.

## Adımlar

1. `admin_cost.py:507` içine robust z-skor bloğu.
2. Formül (SSOT §9 K5): `z = 0.6745 * (bugün - medyan) / MAD`, alarm eşiği `|z| > 3.5`.
3. MAD sıfırsa bölme hatası verme — o durumda anomali yok say.
4. 30 günlük maliyet serisi girdi.

## Kabul kriteri

- [ ] z-skor hesabı için assert tabanlı 1 test (MAD=0 kenar durumu dahil).
- [ ] Anomali listesi panelde görünüyor.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
