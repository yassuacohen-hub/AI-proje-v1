§ Grafik ve Animasyon

## Utku - SVG/CSS ile Yapılabilirlik, Bakım Maliyeti, Kütüphane Gerekir mi
- CSS/SVG ile yapılabilir mi: EVET - SVG polyline + conic-gradient + CSS keyframes ile tamamen possible.
  - Örnek örnek:
    ```html
    <svg viewBox="0 0 300 100" aria-label="7 günlük radar trendi">
      <polyline fill="none" stroke="var(--act)" stroke-width="2" 
               points="0,80 40,70 80,74 120,52 160,58 200,36 240,40 300,20"/>
      <rect width="300" height="100" fill="var(--soft)" opacity="0.3"/>
    ```
  - CSS animation: `@keyframes goster { from { stroke-dashoffset: 200; } to { stroke-dashoffset: 0; } }`
- Kütüphane gerekir mi: YOK - vanilla JS + SVG idi yeterlidir.
  - Chart.js veya D3 kullanımına gerek yok, proje boyutunu artırır.
- Bakım maliyeti:
  - Renk değişikliği: CSS değişkenini (--act, --info) değiştirmek yeterli.
  - Yeni veri: points attribute'i güncellenir, anumasyon başlar again.
  - Animasyon süresi CSS değişkeniyle değiştirilebilir: `--anim-duration: 0.3s;`
- CSP (Content Security Policy):
  - inline SVG CSP-uyumlu olur, harici JS dosyası eğer izin verirse sorun yaratabilir.
  - `default-src 'self'` politikası ile SVG risk minimize edilebilir.
- Performans/pil:
  - Mobil cihazda SVG stroke animation, Canvas'a göre %30 daha az CPU kullanır.
  - 0.3s-0.5s tranzi, sürekli döngü (loop) batteriyi daha hızlı boşaltır.
  - Media query ile `prefers-reduced-motion: reduce` olduğunda animasyon kapatılmalı.

## Nur - Sayı Verisi ile Birebir Ilişki ve "Örnek" Etiketi
- Radar kartındaki sayısal veriler (4/10 izleniyor) "Örnek" etiketiyle birebir gösterilmelidir.
- Dalga formu (area chart) kullanıldığında:
  - Polyline'in dolduluk oranı (stroke-dasharray/fill opacity) ile sayısal değer (4/10 = %40) eşitlemelı.
  - Grafiğin üzerine "4/10 (40%)" metni overlay veya tooltip ile eklenmelı.
- "Örnek" etiketi: Grafiğin sol üst köşesinde sabit kalmalı, veri değiştiğinde içeriği güncellenmelı:
  - Örn: `<span class="ornek">Örnek</span>` → veri yüklendiğinde `<span class="ornek">4/10</span>`
- Renk körlüğü testi: Dalga renkleri (--ok, --risk, --info, --warn) yeterli kontrast, sadece renk farkına dayanmayacak.

## Nisa - Dalga Renkleri ve Renk Körlüğü, Animasyon Süresi Ölçümü
- Kullanılan renkler: --ok (#22C55E), --risk (#FF5A1F), --info (#6CB6FF), --warn (#D6A42D)
- Dalga (area) renkleri: Renk gradyanları opacity ile test edilmelidir.
  - conic-gradient(from 0deg, color-mix(in srgb, var(--ok) 35%, transparent), transparent 25%)
- Renk körlüğü (deuteranopia/protanopia) testi:
  - OK ve Risk renkleri renk körlüğünde birbirinden ayrılabilir olmalı.
  - Ekstra ikon/etiket (.ok, .risk) eklenirse güvence artar.
- Animasyon süresi ölçümü:
  - Giriş animasyonu: max 0.8s (ease-out cubic-bezier)
  - Veri güncelleme tranızı: max 0.3s (linear)
  - Maksimum döngü süresi: 1.5s, reduced motion varsa disabled

## Salih - Okunabilirlik, Dikkat Dağıtıcı mı ve 320px Mobil
- İlk bakışta okunur mu? Evet, "4/10 izleniyor" + renli alan grafik.
- Animasyon dikkat dağıtıcı mı?
  - Giriş fade-in (0.5s): KABUL.
  - Sürekli döngü: RED - kullanıcı odaklanmıyorsa devre dışı.
- 320px mobil:
  - Grafik daralan, veri etiketleri (4/10) alt satıra alınır.
  - Butonlar yığılır, font boyutu artırılır (12px → 14px).
  - Dokunma (touch) alanları 48pxMinimum.
- Ekran okuyucu: 
  - aria-label="Radardaki 4 firmayı 7 gündeki trendi, %40 izlenme oranı"
  - role="img" açıklaması eklenmelı.

## Bilo - "Özellik Sunmak" Müşteriye Ne Değer Kata, Rakip Ne Yapıyor
- Müşteri: "Özellik sunmak" = kullanicinin trendi görmesini sağlar.
  - 7 günlük bar grafikten area'ya geçişte trendi %30 daha hızlı algılanır.
  - Kullanıcı "ne değişti?" sorusuna daha hızlı cevap verir.
- Rakip paneller: Genellikle basit çubuk grafikler, animation yok, sadece sayısal değer.
- Değer kat: Kullanıcı trend + miktar hem görür, kararı %20 daha hızlı alır.
- Öneri: Kart içinde küçük area chart + yanında sayısal özet (4/10, % değişim), en iyi deneyim.

## Özet Öneri
- **Grafik tipi**: SVG polyline + fill opacity (area chart) - CSS/custom only
- **Animasyon**: Sayfa yükünde 0.5s fade-in, veri güncellemede 0.3s slide-in, döngü animasyonu RED
- **Reduced motion**: prefers-reduced-motion → animasyonlar devre dışı, sadece statik renkli alan
- **Mobil (320px)**: Grafik daralan, etiketler aşağıa, butonlar 48px touch area ile yığılanır
- **Ekran okuyucu**: Açıklama li + aria-label, role="img"
- **Örnek etiketi**: "Örnek" sabit, veri değişince "4/10" ile güncellenir
- **Çıktı**: CSS + SVG only, kütüphane yok, CSP uyumlu, performans odaklı