# Hakem V12 — Üretim/Hacim UTKU

Esas dosya: `Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` (1165 satır, ölçüldü). Kod yok (D-420) — yalnız değerlendirme. Körleme: diğer hakem dosyalarına bakılmadı.

## § Grafik ve Animasyon

Uzmanlık gözü: SVG/CSS ile yapılabilirlik, bakım maliyeti, kütüphane gerekliliği.

### 0. Teşhis — PO'nun 2. isteği yapısal olarak doğru, kanıtlı

"Radardaki Şirket" kartının "Son 7 gün" grafiği ile Fırsatlar'ın "Günlük fırsat sayısı" grafiği **aynı görünmüyor, aynı bileşen**:

| Kanıt | Dosya:satır |
|---|---|
| KPI detay şeridi "Son 7 gün" → `div.gcub` (height:44px) basar | `MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html:1064` |
| Fırsatlar `#fg` → aynı `div.gcub genis` | `:464` |
| İkisi de aynı CSS'i paylaşır: `.gcub i{...animation:grow .7s}`, `:nth-child(2n)` info, `:last-child` ok | `:183-186` |

Yani "her kartın kendi karakteri" talebi CSS katmanında karşılanamaz durumda — bileşen sınıfları bile ortak. Çözüm: ikinci bir grafik bileşen sınıfı (`galan`/alan grafiği) gerekir, kütüphane değil.

Veri türü ayrımı PO'nun kendi kuralını destekliyor:
- Radar serisi `s:[2,3,3,4,4,4,4]` (`:1054`) — **stok/birikim** (yuva doluluğu, monoton artan seviye). Seviye → alan/eğri doğru gösterim.
- Fırsat serisi `FB` (`:1027`) — **günlük akış sayımı**. Kesikli gün → çubuk doğru gösterim.
- Sonuç: "farklı veri = farklı grafik" kuralı gereği dalga radar'a geçer, çubuk Fırsatlar'da kalır. Çelişki yok.

### 1. Radardaki Şirket — 3 grafik adayı (A/B/C + gerekçe)

| Aday | SVG/CSS maliyeti | Risk / bakım | Hüküm |
|---|---|---|---|
| **A. Dalga / alan (monoton yumuşatılmış eğri + altta degrade dolgu)** | Tek `<path>` + tek keyframe; yumuşatma için monotone cubic (Fritsch–Carlson) yardımcı ~25-35 satır JS | Naif catmull-rom 0–4 tam sayı veride verinin altına/üstüne taşar (yanıltıcı); monotone interpolatör zorunlu, ~20 satır | **A — önerim** |
| **B. Çizgi + nokta (polyline + circle)** | ~15 satır, interpolasyon riski yok; noktalar mevcut "güne tıkla → özet" etkileşimini aynen taşır (`:1029` tabindex+aria-label sözleşmesi) | Düz çizgi "genel kütüphane görünümü"ne en yakın seçenek — PO istek 5 ile gerilim | **B — yedek** |
| **C. Halka-ilerleme (donut, stroke-dasharray)** | ~10 satır, en ucuzu | 7 günlük seyri **hiç gösteremez**; tek değer (4/10) gösterir. Detay şeridindeki "Son 7 gün" grafiğinin yerine geçemez; ancak kart göbeğindeki `.cubuk` çubuğunun (`:510`) yerine **kart içinde** anlamlı | C yalnız kart içi aday, şerit adayı değil |

Gerekçe (A): PO'nun 5. isteği (ürüne ait görsel dil) en iyi degrade alan + `stroke-dashoffset` çizim animasyonuyla karşılanır; B sade kalır, C zaman serisini kaybeder. Ek bulgu: `.gcub i:nth-child(2n)` info + `:last-child` ok renk rotasyonu (`:185-186`) günlük seride **anlamsız** — tek/çift gün kategori değil; dekoratif renk değişimi hem "genel kütüphane" hissi verir hem yanlış kodlar. Fırsatlar çubukları tek renk + "bugün" vurgu rengi olmalı; kart karakteri kütüphanesiz böyle ayrışır.

Lazy ladder (yeni kütüphane önermeden önce): **CSS** (çubuk/büyüme zaten CSS) → **SVG** (alan/çizgi/halka: viewBox'lu inline `<path>`/`<polyline>`/`<circle>`, degrade `<linearGradient>`, keyframe dashoffset) → kütüphane **gerekmez**. Chart.js ~205 KB, ECharts ~1 MB+; 7 noktalık seri için ölçüsüz, PO'nun reddettiği "genel kütüphane görünümü"nü bizzat kütüphane üretir. CSP/CDN duruşu bozulmaz, sıfır yeni bağımlılık. Bakım maliyeti: ~30 satır path üretici + 1 keyframe + 1 easing token; kütüphane sürüm kırılmaları ve API değişimi bakım yükü sıfıra iner. Not: gerçek panel ilerleyen planda Streamlit+ECharts'a geçse de (kayıtlı görselleştirme stacki kararı) "veri türü → grafik türü" kuralı aynı kalır; wireframe aşamasında karar SVG/CSS'tir.

### 2. Yükleme animasyonu — hangi widget'lar almalı, hangisi sabit

Zaten var ve korunur (tek seferlik): sayı sayma `data-say` 900ms (`:1193-1195`), menü girişi `navGir` .45s + 20-270ms kademe (`:74-85`), `#fg` çubuk büyümesi (`:1029`).

Öneri — animasyon alsın (en fazla 4 + sayma):
1. **KPI kartları girişi**: opacity + translateY(12px→0), 240ms, kartlar arası 60ms kademe, 4 kart = en geç ~420ms'de biter. (Yeni, ucuz.)
2. **Fırsatlar `#fg` çubukları**: süreyi kısalt (aşağıda madde 3).
3. **Radarım `.radar` taraması** (`:140-142`): `don ... infinite` sonsuz döndürme pil/dikkat maliyeti → **2 tur tek seferlik** yap; sonsuz döndürme kaldıysa yalnız hover'da dönsün. (Sonsuzluk kararı **PO'YA BIRAK** — pil/dikkat ödünleşimi ürün kararı.)
4. **Alan grafiği çizimi**: dashoffset çizim + dolgu soluklaşması (yeni bileşen, tek seferlik).

Sabit kalsın: **metin/liste widget'ları** — Son Sinyaller, Son İşlemler, Fırsatlar listesi, tablolar. Okunacak metin hareket etmez; animasyon okumayı geciktirir. KPI detay şeridi talep üzerine açılır: 150ms opacity yeter, ölçek/yumuşama animasyonu **olmasın** (tıklama tepkisi 200ms'yi geçmemeli).

Bakım bulgusu: `#fg` aralık değişiminde innerHTML yeniden yazılır (`:1029`, `animation:...both`) → 7/14/30 her tıklamada animasyon **baştan oynar**; 30 günde ~520ms kademe + 700ms = tıklama başına ~1,2 sn tekrar. Kural: animasyon yalnız sayfa yüklemesinde; talep-üzeri yeniden çizim ya animasyonsuz ya ≤200ms hızlı varyant olmalı.

### 3. Süre ve tür — ölçülebilir öneri (ms)

| Öğe | Şimdi | Öneri | Easing |
|---|---|---|---|
| Kart girişi | yok | opacity+translateY **240ms**, kademe **60ms**, tavan 800ms | `cubic-bezier(.2,.7,.2,1)` (mevcut `navGir` eğrisiyle aynı) |
| Sayı sayma | 900ms (`:1195`) | **900ms kalır** (en uzun öğe, koreografi sonu bu) | ease-out kübik (zaten `1-(1-p)^3`) |
| Çubuk büyüme | 700ms + 18ms×n (`:184,1029`) → 30 günde ~1220ms | **450ms + 12ms kademe**, toplam tavan **800ms** | ease-out |
| Alan çizimi | yok | dashoffset **600ms** + dolgu opacity **300ms** (200ms'de başlar) | ease-out |
| Menü (var) | .45s + kademeler | dokunma | — |
| Radar taraması | 4s×sonsuz (`:140`) | 4s × 2 tur, tek seferlik (veya hover) | linear |

Tek kural: **yükleme koreografisi toplam ≤1200ms**; iki easing tokeni (`--ease-giris: cubic-bezier(.2,.7,.2,1)`, sayısal öğelerde `ease-out`); `popin` (`:182`) yalnız mevcut rozetlerde kalır, yayılmaz. Token'ların kendisi "ürüne ait görsel dil" talebinin kütüphanesiz cevabıdır.

### 4. Sınırlar (benim gözüm — üretim/erişilebilirlik/maliyet)

| Sınır | Değerlendirme | Kanıt / tarif |
|---|---|---|
| prefers-reduced-motion | Dosyada **6 ayrı** azaltılmış-hareket bloğu var (`:86,143,157,210,211,1193`). Yeni animasyonlar bu mevcut bloklara eklenir; **7. ayrı media query yasak** (ikiz yapı). Alan çizimi reduce modunda: `stroke-dashoffset:none` + opacity:1 → grafik son halinde anında belirir. | mevcut desen |
| 320px mobil | Detay şeridi grafiği **sabit 220px** (`:1064`) — SVG `viewBox` + `width:100%` olmalı; `preserveAspectRatio="none"` stroke kalınlığını bozar → `vector-effect="non-scaling-stroke"` şart. Çubuk gap:4px 320px'te sorunsuz. | `:1064` |
| Düşük cihaz | Yalnız `opacity`/`transform` (compositor); `stroke-dashoffset` tek seferlik **CSS** animasyonla oynatılır, JS rAF döngüsü kurulmaz (tek rAF döngüsü zaten sayma için var, `:1194`). Sonsuz conic-gradient tarama küçük alanda ucuzdur ama viewport dışındayken `animation-play-state:paused` (IntersectionObserver ~5 satır) eklenebilir. | `:1193-1195` |
| Ekran okuyucu | Konteyner `role="img"` + `aria-label` deseni mevcut (`:464`); SVG'de `<title>` + gün başına görünmez `<rect tabindex="0" aria-label="...">` — `.gcub i` erişilebilirlik sözleşmesi (`:1029` tabindex+aria-label) aynen kopyalanır. "Son 7 gün" + **Örnek rozeti** (`:1064`, `:463`) SVG geçişinde korunur; rozetsiz sayı = etiketsiz sayı. | `:464,1029` |
| KVKK / dış bağımlılık | Sıfır yeni bağımlılık: satır içi SVG/CSS, CDN yok, yazı tipi yok, veri istemcide — KVKK yüzeyi değişmez, CSP duruşu aynen kalır. Kütüphane (Chart.js/ECharts) CSP'ye `script-src` ekleri ve tedarik zinciri riski getirirdi; gerek yok. | lazy ladder madde 1 |

### 5. Hüküm özeti

| Soru | Hüküm |
|---|---|
| Hangi grafik? | **A: monoton yumuşatılmış dalga/alan** (SVG, ~30 satır yardımcısız kütüphanesiz). Yedek B: çizgi+nokta. C halka yalnız kart içi `.cubuk` alternatifi. |
| Hangi widget'lar animasyon alsın? | KPI kartları girişi, `#fg` çubukları, radar taraması (tek seferlik), alan çizimi. Sabit: tüm metin/liste widget'ları + KPI detay şeridi (yalnız 150ms opacity). |
| Süre | Giriş 240/60ms, çubuk 450ms+12ms, alan 600+300ms, sayma 900ms; toplam ≤1200ms; iki easing tokeni. |
| Kütüphane? | **Gerekmez** — CSS/SVG yeter (lazy ladder 2. basamak). Kütüphane PO'nun istemediği "genel görünüm"ü kendisi taşır. |
| PO'YA BIRAK | Radar taraması sonsuz mu kalsın (canlılık hissi) yoksa 2 tur mu olsun (pil/dikkat)? Önerim 2 tur. |

## Rapor (D-407)

1. **Ne oldu:** V11B_TURUNCU grafik/animasyon katmanı satır satır ölçüldü; iki "farklı" grafiğin aynı `.gcub` bileşeni olduğu kanıtlandı (`:464` vs `:1064`); 3 aday + animasyon seti + ms bazlı süre/easing + 5 sınır maddesi `data/orchestrator/hakem_v12/utku.md`'ye yazıldı. Kod değiştirilmedi (D-420).
2. **Takılan yer ve neden:** Yok. Tek belirsizlik: radar taramasının sonsuz/tek-seferlikliği ürün kararı — PO'YA BIRAK işaretlendi.
3. **Sıradaki adım:** Diğer hakemler kapanınca orkestratör çapraz sentez yapar; A kararı onaylanırsa wireframe'e `galan` bileşeni + easing tokenleri uygulama görevi (kod onayı sonrası) açılır.

**Öz-eleştiri:** (1) Dosya ilk aramada `docs/` kökünde sanıldı, glob ile vault altında bulundu — hub-önce okuma yerine doğrudan dosya araması 1 tur kaybettirdi. (2) Yumuşatma taşma riskini (interpolasyon overshoot) ilk okumada değil yazım aşamasında düşündüm; aday tablolarına veri-yanıltma riski sütunu standart eklenmeli.
