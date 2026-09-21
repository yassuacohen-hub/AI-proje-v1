# Özeleştiri Şablonu — Haftalık (D-67)

Her **Cuma sonu** / **Pazartesi sabahı** yazılır. `<rol>`: `orkestrator` · `uretim` · `denetim` · `test`.

Dosya adı: `data/orchestrator/ozelestiri/<YYYY-AA-GG>_degerlendirme_<rol>.md`

Örnek: `2026-09-26_degerlendirme_uretim.md`

---

# Haftalık Özeleştiri — <YYYY-AA-GG> / <rol>

## Ne iyi gitti?
- (maksimum 3 madde)
- Örnek: Zincir otomasyonu çalıştı, testler yeşil
- Örnek: Bulgu takibi disiplini sağlandı

## Ne kötü gitti?
- (maksimum 3 madde, spesifik sorunlar)
- Sistem mi (VPN, Docker timeout, API yanıt yavaş)?
- Tasarım mı (kural belirsizliği, brief eksik)?
- Zaman mı (tahmin tutmadı, scope creep)?
- Rehberlik mi (hangi step yapılacağı netleşti)?

Örnek: "VPN düşüşü 2 saat iş saati kaybetti"

## Zamanı ne yedi?
- (maksimum 3 madde, yapılmış işlerin saati)
- Örnek: "Raporlar yazımı 6 saat (4 görev × 1.5 saat)"
- Örnek: "Guard kodu yazımı 2 saat"
- Toplam saat + oranı yazınız

## Yarın neyi değiştireceğim?
- (maksimum 3 madde, aksiyon)
- Örnek: "Brief denetim şablonunu hazırla"
- Örnek: "VPN kapalı dev ortamında test et"

---

**Not:** Rapor dosyaları içinde `## Özeleştiri` başlığı yazılırsa (günlük), bu haftalık denetim raporu yalnız **yığın ve analiz** için (aksiyonları çıkarmak için) yazılır.
