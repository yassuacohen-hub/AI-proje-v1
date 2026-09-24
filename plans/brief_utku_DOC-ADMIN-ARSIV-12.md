# DOC-ADMIN-ARSIV-12 — Brief (utku)

**Başlık:** [DOC] Bayat analiz dökümanını taşı → arşiv + §0.1 güncel (1s)
**Öncelik:** P2 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

SSOT §11 KK-4 — `06_muninn_prd_vs_huginn_analiz.md` (2026-09-13) bu SSOT ile değiştirildi, bayatlığı §8.3 C4'te kanıtlı. Ortada durması ajanları yanlış yönlendiriyor.

## Adımlar

1. `AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz.md` başına `> ⚠️ ARŞİV — geçersiz. Güncel SSOT: ADMIN-KİT` uyarısı yaz.
2. SSOT §0.1'deki 'Eski analiz' satırını arşiv durumuyla güncelle.
3. Dosyayı **silme** — geçmiş kanıt; yalnız işaretle (D-186 bağlantılar kırılmasın).

## Kabul kriteri

- [ ] Bayat dosya arşiv uyarısı taşıyor.
- [ ] SSOT §0.1 ve §11 KK-4 güncellendi.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
