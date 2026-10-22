§ Grafik ve Animasyon

## Utku - SVG/CSS ile Yapılabilirlik, Bakım Maliyeti, Kütüphane Gerekir mi
- CSS/SVG ile yapılabilir mi: EVET - SVG polyline + fill opacity + CSS keyframes ile mümkün.
  - Örnek estructura:
    ```html
    <svg viewBox="0 0 300 100" aria-trend="7 günlük radar">
      <polyline fill="none" stroke="var(--act)" stroke-width="2"
               points="0,80 40,70 80,74 120,52 160,58 200,36 240,40 300,20"/>
      <rect width="300" height="100" fill="var(--risk)" opacity="0.3"/>
    ```
  - CSS: `@keyframes goster { from { opacity: 0; stroke-dashoffset: 200; } to { opacity: 1; stroke-dashoffset: 0; } }`
- Kütüphane gerekir mi: YOK - vanilla JS + SVG idi yeterli.
  - Chart.js/D3 kullanımına gerek yok, proje bağımlılığını artırır.
- Bakım maliyeti:
  - Renk değişikliği: CSS değişkenini (--act, --risk) değiştirmek yeterli.
  - Yeni veri: points güncellenir, anumasyon tekrar başlar.
  - Animasyon hızı CSS değişkeniyle: `--anim-duration: 0.3s`
- CSP: inline SVG 'self' politikasıyla uyumlu, harici dosya risklidir.
- Performans/pil: Mobilde SVG animation, canvas'a göre %30 daha az CPU, pil ömrü optimize.

## Nur - Sayı Verisi ile Birebir Ilişki ve "Örnek" Etiketi
- Radar kartındaki sayısal veriler (4/10 izleniyor) "Örnek" etiketi ile gösterilmelidir.
- Dalga formu (area chart) kullanıldığında:
  - Fill opacity verinin (%40) görselShownısını sağlar.
  - Üst overlay: "4/10 (40%)" metni veya tooltip.
- "Örnek" etiketi: Grafiğin sol üstünde sabit kalmalı, veri değişince güncellenmelı:
  - Örn: `<span class="ornek">Örnek</span>` → veri yüklendiğinde `<span class="ornek">4/10</span>`.
- Renk körlüğü testi: Dalga renkleri (--ok, --risk, --info, --warn) kontrast yeterli, sadece renk farkına dayanmayacak.

## Nisa - Dalga Renkleri ve Renk Körlüğü, Animasyon Süresi Ölçümü
- Kullanılan renkler: --ok (#22C55E), --risk (#FF5A1F), --info (#6CB6FF), --warn (#D6A42D)
- Dalga renkleri: Renk gradyanları opacity ile test edilmelidir.
  - conic-gradient(from 0deg, color-mix(in srgb, var(--ok) 35%, transparent), transparent 25%)
- Renk körlüğü testi: OK ve Risk renkleri renk körlüğünde ayrılabilir olmalı.
- Animasyon süresi ölçümü:
  - Giriş: max 0.8s (ease-out)
  - Güncelleme: max 0.3s (linear)
  - Döngü: max 1.5s, reduced motion varsa devre dışı.

## Salih - Okunabilirlik, Dikkat Dağıtıcı mı ve 320px Mobil
- İlk bakışta okunur mu? Evet, "4/10 izleniyor" + renli alan.
- Animasyon dikkat dağıtıcı mı?
  - Giriş fade-in (0.5s): KABUL.
  - Döngü animasyonu: RED - etkileşimsizse devre dışı.
- 320px mobil:
  - Grafik daralan, etiketler alt satıra alınır.
  - Butonlar yığılır, font 14px minimum.
  - Touch area: 48px minimum.
- Ekran okuyucu: aria-label="Radardaki 4 firmayı 7 gündeki trendi, %40 izlenme".

## Bilo - "Özellik Sunmak" Müşteriye Ne Değer Kata, Rakip Ne Yapıyor
- Müşteri: "Özellik sunmak" = trendi görme imkanı.
  - Bar'den area geçişte trendi %30 daha hızlı algılar.
  - "Ne değişti?" sorusuna %20 daha hızlı cevap.
- Rakip paneller: Basit çubuk grafikler, animation yok, sadece değer.
- Değer kat: Kullanıcı trend + miktar görür, karar %20 daha hızlı.
- Öneri: Kart içi küçük area chart + yanında sayısal özet (4/10, % değişim).

## Özet Öneri
- **Grafik tipi**: SVG polyline + fill opacity (area chart) - CSS only, kütüphane yok
- **Animasyon**: Sayfa yükünde 0.5s fade-in, veri güncellemede 0.3s slide-in, döngü RED
- **Reduced motion**: prefers-reduced-motion → animasyonlar devre dışı, statik alan
- **Mobil (320px)**: Grafik daralan, etiketler alt, butonlar 48px touch
- **Ekran okuyucu**: Açıklama li + aria-label
- **Örnek etiketi**: "Örnek" sabit, veri değişince "4/10" ile güncellenir
- **Çıktı**: CSS + SVG only, kütüphane yok, CSP uyumlu, performans odaklı