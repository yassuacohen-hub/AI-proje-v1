# Hakem v12 — nur (ölçüm ve bağımsız doğrulama)

> **Skill beyanı (D-401):** okunan skill: `verification-before-completion` (+ `doubt-driven-development` deseni).
> Uygulanan madde: *"NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"* — her oy satırı bu
> oturumda koşulmuş komut çıktısına dayanır; koşulmayanlar `[B]` yazıldı, tahmin yazılmadı.
> Ayrıca *"Agent reports success → verify independently"*: ihsan'ın PO onaylı kararlarını beyan
> olarak kabul etmeyip dosyada uygulanıp uygulanmadığını ölçtüm (3 uyuşmazlık çıktı).

> Ajan: **nur** · Rol: ölçüm/doğrulama · Son söz ihsan/PO (D-71).
> Körleme: diğer hakemlerin dosyaları okunmadı; `data/orchestrator/hakem_v12/` bu yazım anında yalnız bu dosyayı içeriyor.
> Kod değişikliği yok (D-420). Esas dosya salt okunur incelendi: `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` (1199 satır).
> **Ölçüm aracı:** statik ayrıştırma (Python stdlib) + **gerçek tarayıcı (Playwright 1.5x / Chromium 156.0.8078.4)**. Ölçüm scripti: `data/_tmp/olc_v12_nur.py`, ham çıktı `data/_tmp/olc_v12_sonuc.json` (geçici, ürün ağacında değil).
> Uzmanlık odağım: **grafikte gösterilen sayı veriyle birebir mi, "Örnek" etiketi kayboluyor mu.**

---

## § Grafik ve Animasyon

### 0. Önce bulgular — PO'nun sorduğu grafiği değiştirmeden önce düzelmesi gerekenler

Ölçüm komutu: `python -I -c` ile dosya ayrıştırıldı; `KD` sabiti (satır 1052–1057) ve KPI kart kodu (satır 509–512) karşılaştırıldı.

#### B1 — Kart sayısı ile "Son 7 gün" grafiği aynı şeyi anlatmıyor `[A]` · **ACİL**

Kanıt (ölçülen çıktı):

| KPI | Kart sayısı | `KD.s` serisi | Serinin son günü | Seri toplamı | Kart = son gün? | Kart = toplam? |
|---|---|---|---|---|---|---|
| kredi | 42 | `[1,0,2,0,1,2,0]` | 0 | 6 | hayır | hayır |
| radar | 4 | `[2,3,3,4,4,4,4]` | 4 | 24 | **evet** | hayır |
| esles | 3 | `[1,0,2,1,2,2,3]` | 3 | 11 | **evet** | hayır |
| uyari | 7 | `[0,1,1,2,0,2,1]` | 1 | 7 | hayır | **evet** |

Dört kart, aynı görünen çubuk grafiği **üç farklı anlamla** kullanıyor: `radar`/`esles` son gün = kart, `uyari` toplam = kart, `kredi` ikisi de değil (kart 42 = bakiye, seri = harcama). Müşteri aynı şekli görüp aynı okumayı yapar; okuması üç kartta yanlış çıkar. Bu, grafiği dalgaya çevirmekle düzelmez — dalga da aynı belirsizliği taşır.

**Öneri:** her mini grafiğin üstüne ne ölçtüğünü yazan tek kelimelik etiket (`bakiye` · `günlük` · `toplam`) + grafik türü veri türüne bağlansın (§1 kuralı). `[A]` ölçülebilir, `[C]` etiket metni PO tercihi.

#### B2 — Sıfır değerli gün, dolu çubuk gibi çiziliyor `[A]`

Satır 1064: `height:${Math.max(6,x/mx*100)}%`. Ölçülen yükseklikler:

| KPI | Çubuk yükseklikleri (%) | `0` değerli günler |
|---|---|---|
| kredi | `[50,6,100,6,50,100,6]` | 3 gün → %6 yükseklikte görünür |
| esles | `[33,6,67,33,67,67,100]` | 1 gün |
| uyari | `[6,50,50,100,6,100,50]` | 2 gün |

`0` ile `0` olmayan küçük değer aynı görünüyor. Veriyi birebir göstermiyor. **Öneri:** sıfır için çubuk değil, taban çizgisinde 2px nokta/boşluk; `aria-label` içinde "0" açıkça yazılsın.

#### B3 — "Radardaki Şirket" kartında **"Örnek" rozeti YOK** `[A]` · **ACİL**

Ölçülen rozet sayısı: `k-kredi`=1, `k-radar`=**0**, `k-esles`=1, `k-uyari`=1 (satır 509–512). PO'nun grafiğini değiştirmek istediği kart, örnek veri uyarısı taşımayan tek KPI kartı. Diğer üç kart rozeti `delta` satırında taşıyor; `k-radar`'da `delta` satırı yerine `.cubuk` doluluk şeridi var (satır 510) ve rozet onunla birlikte düşmüş.

**Tarayıcıda doğrulandı** — Chromium'da `#k-radar` kartının render edilmiş hali:

```
k-radar "Örnek" rozeti sayısı: 0
k-radar kart metni           : "Radardaki Şirket 4 /10 6 yuva boş"
```

Müşteri kartta `4 /10` görüyor, hiçbir yerde "Örnek" yazmıyor. Kart açılınca detayda rozet beliriyor (`"Radardaki Şirket Örnek 10 yuvanın 4'ü dolu..."`), ama **kapalı haldeki KPI şeridi örnek veriyi gerçek gibi gösteriyor.**

**Kural gereği (veri uydurma yok): yeni grafik eklenirken rozet de eklenmeli.** Aksi halde yeni animasyonlu grafik, "Örnek" demeden gerçek veri gibi görünür.

#### B4 — KPI detayındaki "Son 7 gün" grafiği ekran okuyucuya görünmüyor `[A]` · **tarayıcıda doğrulandı**

Satır 1064'teki `.gcub` bloğunda `role="img"` ve `aria-label` yok. Chromium'da `#k-radar` tıklanıp DOM okundu:

```
kpi-detay grafik var : True | role=None | aria-label=None
çubuk sayısı         : 7    | çubukların aria-label'ı hepsi None: True
kpi-detay aria-live  : polite
ekran okuyucunun duyduğu:
  "Radardaki Şirket Örnek 10 yuvanın 4'ü dolu. 3 yeni sinyal, 1 riskli firma var.
   Son 7 gün İzlenen Firmalar → Kapat"
```

Ekran okuyucu **"Son 7 gün" başlığını duyuyor ama ardından hiçbir sayı gelmiyor** — 7 çubuğun hiçbiri erişilebilirlik ağacında değil. CDP `Accessibility.getFullAXTree` çıktısında `role=image` olarak yalnız iki grafik var: Fırsatlar (`"Günlük fırsat sayısı, örnek..."`) ve sparkline (`"Örnek 7 günlük sinyal çizgisi"`). KPI detay grafiği ağaçta **yok**.

Aynı dosyada doğru desen zaten çalışıyor; KPI detayına uygulanmamış. Yeni dalga/alan grafiği de aynı boşluğa düşerse ekran okuyucu kullanıcısı hiçbir şey duymaz.

---

### 1. Radardaki Şirket kartı için üç aday — ölçülmüş değerlendirme

PO üç aday verdi: dalga (alan/eğri), çizgi+nokta, halka-ilerleme. Değerlendirme ölçütü **veri türü**:

`radar` verisi `[2,3,3,4,4,4,4]` → monoton artan, **durum/doluluk** (stok), günlük olay sayısı (akış) değil. Kart yüzü zaten `4 /10` + `%40` doluluk şeridi gösteriyor (satır 510).

| Aday | Veriye uygunluk | Ölçülen sorun | Hüküm |
|---|---|---|---|
| **Dalga (düz eğri alan)** | Orta | Bezier yumuşatma, **gün arasında ölçülmemiş ara değer uydurur**; 2→3 geçişi eğride 2,4 gibi okunur. Monoton seride dalga "dalgalanma" izlenimi verir, veri dalgalanmıyor. | Tek başına önerilmez |
| **Basamaklı alan (step-after + dolgu)** | **Yüksek** | Ara değer uydurmaz; her gün bir basamak. Dolgu PO'nun istediği "alan" görünümünü verir. | **Önerilen** `[A]` |
| **Çizgi + nokta** | Yüksek | Doğru ama Fırsatlar altındaki mevcut SVG `polyline` sparkline (satır 500) ile aynı dile düşer → PO'nun 2. maddesine (aynı görünmesin) takılır. | İkinci sıra |
| **Halka-ilerleme** | **Yüksek (kart yüzü için)** | `4/10` oranını birebir gösterir; ama 7 günlük seyri gösteremez. | **Kart yüzünde önerilen** `[A]` |

**Önerim `[A]+[C]`:** ikisi birlikte, iki farklı yerde —
- **Kart yüzü:** `.cubuk` doluluk şeridi yerine **halka-ilerleme** (`4/10`, oranı birebir).
- **Kart açılınca (`kpi-detay`):** **basamaklı alan grafiği** (7 gün doluluk seyri) + "doluluk" etiketi + "Örnek" rozeti + `aria-label`.

Bu, PO'nun "dalga formlu alan" isteğini karşılar (dolgulu alan kalır), ama ölçülmemiş ara değer uydurmaz. Düz dalga yine de istenirse bu **`[C]` PO tercihidir**; ölçüm "veri monoton, ara değer yok" der, estetik kararı vermez.

### 2. İki grafik neden birbirine benzemeyecek — ortak kural

PO'nun koyduğu kural ölçülebilir hale getirildi:

| Veri türü | Örnek | Grafik türü | Dosyadaki yeri |
|---|---|---|---|
| **Akış** (gün başına olay sayısı) | Günlük fırsat sayısı | **Dikey çubuk** | `#fg`, satır 464 — mevcut, değişmesin |
| **Durum/oran** (anlık doluluk) | Radardaki Şirket `4/10` | **Halka + basamaklı alan** | `k-radar`, satır 510 — değişecek |
| **Seyir** (trend, hedefsiz) | 7 günlük sinyal çizgisi | **İnce çizgi sparkline** | satır 500 — mevcut |

Üç tür birbirinden hem şekil hem renk rolüyle ayrılır: akış `--act`, durum `--info`, seyir `--t3`. Kural tek cümle: **akış = çubuk · durum = alan/halka · seyir = çizgi.**

### 3. Yüklenme animasyonu — hangi widget, neden

Mevcut durum ölçüldü: dosyada 7 keyframe tanımlı (`navGir`, `cubukGir`, `etiketGir`, `don`, `grow`, `growx`, `popin`) ve `[data-say]` sayaç animasyonu (satır 1193–1195). Yani **sayfa zaten animasyonlu**; soru "ekleyelim mi" değil, "hangisi kalsın".

| Widget | Animasyon alsın mı | Gerekçe `[A]`/`[C]` |
|---|---|---|
| **KPI şeridi (4 kart) — sayaç** | **Evet** (mevcut, 900ms) | `[A]` Sayı yukarı sayması değişimi işaret eder; zaten `matchMedia` ile reduced-motion'da kapanıyor (satır 1193). Ürünün imzası burada. |
| **Radar kartı — halka dolumu** | **Evet** (yeni) | `[A]` Doluluk oranı animasyonun anlattığı şeyin ta kendisi: `0→%40`. Hareket veriyi anlatıyor, süslemiyor. |
| **Fırsatlar — çubuk grafiği** | **Evet** (mevcut, kademeli) | `[A]` Soldan sağa zaman akışını gösteriyor; ama süresi düşmeli (§4, B5). |
| **Radar kartı detay — basamaklı alan** | **Evet** (yeni, çizgi çizilme) | `[A]` Yalnız kart açıldığında, sayfa yüklenince değil. |
| **Tablolar (Kredi hareketleri, Fırsat listesi)** | **Hayır** | `[A]` Satır satır beliren tablo okuma hızını düşürür; ayrıca uzun listede toplam süre kontrolsüz büyür. |
| **Sol menü (`navGir`, `etiketGir`)** | **Hayır** — kaldırılması önerilir | `[C]` Gezinme her sayfada aynı; her yüklemede 450ms hareket eden menü bilgi taşımıyor. PO kararı. |
| **Şirket Kartı / Son Sinyaller metin blokları** | **Hayır** | `[A]` Metin içeriği; hareket okumayı geciktirir. |

**Seçim kuralı:** animasyon yalnız **değişimi veya oranı anlatıyorsa** açılır. Dekoratif giriş animasyonu açılmaz.

### 4. Süre ve easing — ölçülmüş eşikler

Mevcut ölçüm (CSS'ten ayrıştırıldı):

| Animasyon | Süre | Nerede |
|---|---|---|
| `navGir` | 450 ms | sol menü |
| `cubukGir` / `etiketGir` | 300 ms | menü |
| `grow` | 700 ms | `.gcub i` çubuklar |
| `growx` | 800 ms | `.dag div i` dağılım |
| `popin` | 550 ms | `.ptop` rozet ikonları |
| `don` | 4000 ms (sonsuz) | `.radar::after` tarama |
| sayaç | 900 ms | `[data-say]`, cubic ease-out |

#### B5 — Fırsat grafiğinin toplam süresi eşiği aşıyor `[A]` · **tarayıcıda doğrulandı**

Satır 1029: `animation-delay:${i*18}ms`, `grow` 700ms. Hesaplanan toplam:
- 7 çubuk: `6×18 + 700` = **808 ms**
- 30 çubuk (aralık düğmesi `30` seçilince): `29×18 + 700` = **1222 ms**

Chromium'da `getAnimations()` ile ölçülen gerçek değerler:

| Ölçüm | Hesabım | Tarayıcı | Sonuç |
|---|---|---|---|
| 30 çubuk, en geç biten çubuk | 1222 ms | **1222 ms** | **birebir** |
| Sayfa yükleme, tüm sonlu animasyonlar (41 adet) | — | **934 ms** (`grow`) | eşik altı |
| `growx` / `navGir` / `popin` en geç | — | 800 / 720 / 550 ms | — |
| Sonsuz animasyon | 1 (`don`) | **1** | teyit |

Yani **sayfa ilk açılışta 934 ms'de duruluyor** (önerdiğim ≤1000 ms eşiğinin altında, sorun yok); asıl aşım kullanıcı `30` aralığını seçtiğinde oluyor: **1222 ms**.

**Önerilen eşikler `[A]`:**

| Ölçüt | Değer | Gerekçe |
|---|---|---|
| Tek öğe süresi | **≤ 400 ms** | Mevcut 700–800ms'nin yarısı; algıda "yavaş" eşiği. |
| Kademe (stagger) adımı | **≤ 25 ms** | Mevcut 18ms uygun; korunur. |
| Bir widget'ın toplam süresi | **≤ 600 ms** | 30 çubuklu halde `29×18+400` = 922ms → hâlâ aşıyor; **kademe 30 öğeden sonra kapanmalı** (`i>30 ? 0 : i*18`). |
| Sayfanın tüm giriş animasyonu | **≤ 1000 ms** | İlk ekran 1 saniyede durulmuş olmalı. |
| Easing | **`cubic-bezier(0.22, 1, 0.36, 1)`** (ease-out quint) | Hızlı başlar, yumuşak durur; mevcut `ease-out` ile uyumlu, daha kararlı bitiş. |
| Sonsuz döngü | **yalnız `don` (radar taraması)**, başka yok | Sürekli hareket pil ve dikkat maliyeti. |

### 5. Sınırlar ve kapılar

#### 5.1 `prefers-reduced-motion` — mevcut kapsam ölçüldü `[A]`

6 ayrı `@media (prefers-reduced-motion:reduce)` bloğu var (satır 86, 143, 157, 210, 211) + JS tarafında `matchMedia` kontrolü (satır 1193). Kapsam kontrolü:

| Seçici | Kapsanıyor mu |
|---|---|
| `.gcub i` (çubuklar) | ✅ satır 211 |
| `.ptop` (rozet) | ✅ satır 211 |
| `.dag div i` | ✅ satır 211 |
| `.yan` (menü) | ✅ satır 86 |
| `#hr`, `.etk`, `.radar::after` | ✅ satır 143/157/210 |
| `[data-say]` sayaç | ✅ JS, satır 1193 |

**Tarayıcıda doğrulandı** — Chromium `reduced_motion="reduce"` bağlamında aynı sayfa açıldı:

| Bağlam | Çalışan animasyon | Sonsuz animasyon |
|---|---|---|
| `no-preference` | **42** | 1 (`don`) |
| `reduce` | **0** | **0** |

`42 → 0`. Sonsuz radar taraması dahil her şey duruyor; `[data-say]` sayacı da JS tarafında kapanıyor. **Kapsam gerçekten tam, beyan değil ölçüm.**

Yeni eklenecek halka ve basamaklı alan animasyonu **aynı bloğa eklenmezse bu `0` bozulur** — bu, eklemenin kabul kapısıdır ve aynı komutla yeniden ölçülebilir.

#### 5.2 Diğer sınırlar

| Sınır | Durum `[A]`/`[B]` |
|---|---|
| **320px mobil** | `[A]` **B6 — gerçek tarayıcıda ölçüldü** (aşağıda): 320px'te 880px taşma, 1280px'te 0. |
| **Düşük cihaz** | `[A]` **Mevcut 7 keyframe'in tamamı yalnız `transform`+`opacity` değiştiriyor** (parantez dengeleyerek ayrıştırıldı): `navGir`, `cubukGir`, `etiketGir`, `don`, `grow`, `growx`, `popin`. Hiçbiri layout tetiklemiyor — compositor katmanında, ucuz. Yeni halka/alan animasyonu da `transform`/`stroke-dashoffset`/`opacity` ile kalmalı; `height`/`width` animasyonu açılmamalı. |
| **Ekran okuyucu** | `[A]` **B4 açık, erişilebilirlik ağacından doğrulandı.** Yeni grafik `role="img"` + tam `aria-label` ("Son 7 gün doluluk: pazartesi 2, … bugün 4. Örnek veri") almalı; `kpi-detay` zaten `aria-live="polite"` (satır 455) — kapsayıcı doğru, içerik eksik. |
| **KVKK / dış bağımlılık** | `[A]` Grafik için **yeni kütüphane gerekmiyor**, ama sayfa açılışında **5 gerçek dış istek gidiyor** — B7 (aşağıda, ağ yakalamasıyla kanıtlı). `canvas`=0, `Chart`=0, `svg`=221, `fetch(`=0, `XMLHttpRequest`=0, `eval`=0, `@font-face`=0. Basamaklı alan tek `<path>` + `<linearGradient>`; halka tek `<circle>` + `stroke-dasharray`. |

#### B6 — Taşma gerçek tarayıcıda ölçüldü `[A]`

Chromium'da dört viewport'ta `scrollWidth - clientWidth` ve taşan öğe sayımı:

| Viewport | Belge genişliği | Yatay taşma | Taşan öğe | İlk taşan |
|---|---|---|---|---|
| **320px** | 1200px | **880px** | 1205 | `.table`/`.th` (sağ=337) |
| **390px** | 1200px | **810px** | 1069 | `.kabuk.dar#kabuk` (gen=1180) |
| **768px** | 1200px | **432px** | 361 | `.kabuk.dar#kabuk` |
| **1280px** | 1280px | **0px** | **0** | — |

Statik taramamdaki `860px` tahmini gerçekte **880px** çıktı (20px fark: `.sayfa` kenar boşluğu). Sabit genişlikler: `.kabuk{min-width:1180px}` (satır 46), `.pop{width:330px}` (158), `.pop.genis{width:390px}` (232), `.ara{width:300px}`. Media query eşikleri yalnız **900px ve 1280px**; 320–900 arası kural yok (satır 196, 261 sadece iki `grid-template-columns:1fr`).

**Hüküm:** `.kabuk{min-width:1180px}` bilinçli bir seçim — bu dosya bir **masaüstü maketi**, duyarlı uygulama değil; `1280px`'te taşma sıfır. O yüzden "320px'te taşıyor" kusur değil, **kapsam bilgisi**. Ama `.pop` (330px) ve `.pop.genis` (390px) gerçek panele taşınırsa 320px'te taşar; `max-width:calc(100vw - 28px)` eklenmeden taşınmamalı. Gerçek panelin kendi ölçümü ayrı iştir.

#### B7 — Dosya Google Fonts'a bağlanıyor: KVKK/CSP riski `[A]` · **ACİL**

Satır 8–9:
- `<link rel="preconnect" href="https://fonts.googleapis.com">`
- `<link href="https://fonts.googleapis.com/css2?family=Inter...&family=JetBrains+Mono...">`

Maket açılır açılmaz kullanıcının IP'si ve User-Agent'ı Google'a gider; `@font-face`=0 olduğu için fontlar **yerel değil**, tamamen dış kaynaklı.

**Tarayıcıda doğrulandı** — sayfa açılışında giden gerçek ağ istekleri yakalandı, **5 dış istek, 2 ayrı Google alan adı**:

```
https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono...
https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2
https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwB...
https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2
https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwB...
```

Dosya `file://` üzerinden açıldığında bile bu beş istek gidiyor. Alman mahkemeleri Google Fonts'u bu gerekçeyle GDPR ihlali saydı; KVKK açısından da yurt dışına aktarım sayılır. CSP yazılacaksa `style-src` + `font-src` için `fonts.googleapis.com` ve `fonts.gstatic.com` açılması gerekir.

Ayrıca **5 adet inline `on...=` handler** var (`onclick`) → CSP `script-src 'unsafe-inline'` gerektirir, bu da CSP'nin değerini büyük ölçüde düşürür.

**Öneri `[A]`:** fontları `self-host` et (woff2, `@font-face`), `preconnect`/`<link>` satırlarını kaldır; 5 inline handler `addEventListener`'a taşınsın. İkisi de grafik işinden bağımsız, ayrı görev.

#### B8 — `localStorage` kullanımı ölçüldü, KVKK açısından temiz `[A]`

Satır 1093–1094: tek anahtar `huginn_v10_gizli`, içerik gizlenen widget id listesi (`OZ` dizisinden). Kişisel veri yok, `document.cookie`=0, tracker yok. **Bulgu değil, teyit.**

#### 5.3 Renk ve kontrast — dalga/alan için ölçüldü `[A]`

Dosyadaki token'larla (gece `--panel #2A2A2A`, gündüz `#FFFFFF`):

| Ölçüm | Gece | Gündüz | Kapı |
|---|---|---|---|
| Çizgi `--info` / panel | **6.68** ✅ | **6.05** ✅ | non-text 3:1 |
| Alan dolgusu %12 / panel | 1.26 | 1.19 | — dolgu **tek başına anlam taşıyamaz**, çizgi taşır |
| Alan dolgusu %25 / panel | 1.64 | 1.46 | aynı |
| `--t3` etiket / %25 dolgu üstü | **3.34** ❌ | **3.65** ❌ | normal metin 4.5:1 — **dolgu üstüne küçük metin yazılmaz** |
| `--t1` metin / %25 dolgu üstü | 7.45 ✅ | 11.91 ✅ | yazılacaksa `--t1` |
| Izgara çizgisi `--line` / panel | 1.50 | 1.39 | yalnız dekoratif; eksen değeri taşımaz |

**Hüküm:** alan dolgusu `%8–%25` arasında serbest (estetik, `[C]`); **anlamı taşıyan şey çizginin kendisi** olmalı. Dolgu üstüne `--t3` etiket konulmaz.

---

## Ölçtüm mü? **Evet**

Bu oturumda koşulan ölçümler: `KD` serisi ile kart sayılarının karşılaştırılması (4/4 kart), sıfır-çubuk yükseklik hesabı, `Örnek` rozeti sayımı (4 kart), `aria-label` varlık kontrolü, 7 keyframe süresinin ayrıştırılması, kademe toplam süre hesabı (7 ve 30 çubuk), `prefers-reduced-motion` seçici kapsamı (9 seçici), WCAG kontrast hesabı (iki tema × 12 çift), kütüphane varlığı sayımı (`canvas`=0, `Chart`=0, `svg`=221), **sabit genişlik taraması (4 seçici + media query eşikleri)**, **dış istek/CSP taraması (`fetch`=0, `eval`=0, dış `<link>`=2, inline handler=5)**, **`localStorage` içerik denetimi**, **7 keyframe'in değiştirdiği CSS özelliklerinin ayrıştırılması (layout mu compositor mu)**.

**İkinci tur — gerçek tarayıcı (Playwright + Chromium 156.0.8078.4), `data/_tmp/olc_v12_nur.py`:** 4 viewport'ta (320/390/768/1280) yatay taşma ve taşan öğe sayımı; sayfa açılışında giden tüm ağ istekleri; `getAnimations()` ile 42 animasyonun süre/gecikme/bitiş değerleri; `reduced_motion="reduce"` bağlamında aynı sayımın tekrarı; `#k-radar` kartının render edilmiş metni ve rozet sayısı; kart açıldıktan sonra `kpi-detay` grafiğinin `role`/`aria-label`/çubuk `aria-label` durumu; CDP `Accessibility.getFullAXTree` ile erişilebilirlik ağacındaki grafik düğümleri; 30 çubuk seçildiğinde gerçek bitiş süresi.

**Statik hesabım tarayıcıda doğrulandı:** 30 çubuk toplam süresi hesapta da ölçümde de **1222 ms**. Taşma tahminim `860px` idi, gerçek **880px** çıktı — 20px'lik fark `.sayfa` kenar boşluğundan; tahmin değil ölçüm yazıldı.

**Üçüncü tur — hakem oyu + yasu kapsamı:** `IDDIA_DEFTERI` kova sayımı (42 iddia), `MENU` dizisi ayrıştırması (19 öğe / 4 grup), T0↔V11B hex kümesi farkı (21 vs 31, 3 ortak), `docs/brand/` OSINT taraması (28 dosya), asset SHA-256 karşılaştırması (13 PNG → 4 benzersiz), `LOGO.md` hedef dosya varlık kontrolü (8/8 yok), K1–K5 kararlarının V11B'de uygulanma kontrolü, Lab ΔE + CVD matris simülasyonu (risk/kritik/mor çiftleri), tarayıcıda KPI-first/toggle/birincil buton doğrulaması, konsol hatası sayımı (0), font engelli/engelsiz iki koşullu dış istek ölçümü, Inter yerel kurulum testi (3 fallback), CSP envanteri, `localStorage`/`sessionStorage`/`cookie` denetimi, `getAnimations()` keyframe özellik ayrıştırması (42 ve 58 eleman).

**Hâlâ ölçmedim:** gerçek FPS / pil tüketimi (CPU throttling altında kare sayımı yapılmadı), gerçek ekran okuyucu yazılımının (NVDA/JAWS) seslendirmesi — erişilebilirlik ağacını okudum, ekran okuyucunun kendisini çalıştırmadım — ve gerçek kullanıcı testi (M1–M8, P1–P2, U1 oyları bu yüzden `[B]`). Bunlar `[B]` kalır.

### Kendi ölçümümü yanlışladım `[A]`

İlk keyframe taramamda `cubukGir`, `etiketGir`, `growx`, `popin` için **"LAYOUT TETİKLER (pahalı)"** yazdım. Regex'im keyframe gövdesini `\}\s*(?=@|\.|#)` ile kesiyordu ve **sonraki CSS kuralını da gövdeye katıyordu**; `height`/`margin`/`width` o komşu kuraldan geliyordu. Parantez dengeleyerek yeniden koştum: **7/7 keyframe yalnız `transform`+`opacity` kullanıyor, hepsi compositor katmanında, hiçbiri layout tetiklemiyor.** Yanlış bulgu rapordan çıkarıldı. Ders: ayrıştırıcı doğrulanmadan alınan sonuç yanlıştır — regex ile CSS bloğu kesilmez, parantez sayılır.

---

## D-407 Rapor

**Ne oldu.** `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` salt okunur ayrıştırıldı. PO'nun 5 maddesi için ölçülmüş cevap üretildi. Yanında, PO'nun sormadığı 8 bulgu çıktı: kart sayısı ile 7-gün grafiğinin üç farklı anlamı (B1), sıfır değerin dolu çubuk görünmesi (B2), **Radardaki Şirket kartında "Örnek" rozetinin olmaması (B3)**, KPI detay grafiğinin ekran okuyucuya kapalı olması (B4), 30 çubuklu halde giriş animasyonunun 1222ms'ye çıkması (B5), 320px'te 880px yatay taşma ve maketin zaten masaüstü olması (B6), **Google Fonts'a 5 dış istek + 5 inline handler (B7, KVKK/CSP)**, `localStorage` denetimi temiz (B8, teyit). Bulguların beşi ikinci turda gerçek tarayıcıyla doğrulandı.

**Takılan yer ve neden.** (1) İlk turda ölçüm aracı yoktu; `pip install` izin sınıflandırıcısı tarafından engellendi — engeli dolanmadım, komutu PO'ya verdim, PO kurdu. İkinci turda `.venv` içinden Chromium ile gerçek ölçüm koştum ve **B3/B4/B5/B6/B7'yi `[B]`'den `[A]`'ya taşıdım**. (2) PO "dalga olsun" dedi, ölçüm "veri monoton, dalga ara değer uydurur" dedi. İkisini çatıştırmadım: dolgulu alanı koruyan ama ara değer uydurmayan **basamaklı alan**'ı önerdim; düz dalga yine istenirse `[C]` PO tercihi, ölçüm karar vermiyor. (3) `data/orchestrator/hakem_v12/` dizini yoktu, oluşturuldu. (4) **Kendi ölçümüm bir kez yanlış çıktı** — keyframe gövdesini regex ile kestim, komşu CSS kuralını içeri aldım ve 4 animasyonu haksız yere "layout tetikliyor" diye işaretledim; parantez dengeleyerek yeniden koşup düzelttim. (5) `page.accessibility.snapshot()` bu Playwright sürümünde kaldırılmış (`AttributeError`); CDP `Accessibility.getFullAXTree` ile aldım.

**Üçüncü tur (hakem oyu + yasu kapsamı).** ihsan brifi (`plans/brief_nur_MUSTERI-PANEL-HAKEM-V12-nur-01.md`) ve V12B §7.1 PO son kararları okundu; 10 özel soru (N-1…N-10), ölçülebilir Çekirdek 12 kalemleri ve PO'nun nur'a devrettiği **yasu kapsamı (5 başlık)** cevaplandı. En ağır üç bulgu: **(i)** gündüz temasında `risk #C93A0A` ile `crit #B42318` ΔE **13.7** (<15), deuteranopide **11.2** — PO sarı/turuncu benzerliğinden şikâyet etti ama ölçüm oranın güvenli olduğunu (ΔE 47–54), asıl sorunun **denetlenmemiş turuncu/kırmızı çiftinde** olduğunu gösterdi; **(ii)** Inter **yerel kurulu değil**, Google engellenirse tipografi sessizce bozuluyor — PO-3 kararı dış servise bağımlı; **(iii)** PO onaylı K1 ve K3 kararları V11B'de **uygulanmamış** (marka SSOT hex 3/4 yok, OSINT 9 geçiş, "yakında" 26 geçiş).

**Sıradaki adım.** (a) ihsan/PO B3'ü kapatsın — kart kapalıyken "Örnek" rozeti yok, müşteri `4 /10`'u gerçek sanıyor; tarayıcı kanıtı yukarıda. (b) **B7 ayrı görev açılsın**: Google Fonts self-host + 5 inline handler `addEventListener`'a; 5 dış istek ağ yakalamasıyla kanıtlı, grafik işinden bağımsız KVKK/CSP konusu. (c) B1 için mini grafiklere veri türü etiketi kararı `[C]`. (d) Grafik çizildiğinde **aynı script yeniden koşulsun** (`data/_tmp/olc_v12_nur.py`): `reduce` bağlamında animasyon sayısı hâlâ `0` mı, `kpi-detay` grafiği erişilebilirlik ağacına girdi mi, 30 çubuk `1222 ms`'den indi mi, yeni animasyon `transform`/`opacity` dışına çıktı mı. Kabul kapısı bu dört sayıdır. (e) FPS/pil ve gerçek ekran okuyucu (NVDA) ölçümü hâlâ `[B]`.

**Öz-eleştiri.** (0) **İlk turda "ölçemem" deyip durdum, oysa ölçüm aracı kurulabilirdi.** Playwright yok diye beş bulguyu `[B]` bıraktım; PO "kendin kur" deyince kurulum engeli bile tek komuttu. Ölçüm ajanıyım — aracın yokluğunu bulgunun yokluğu gibi raporlamak benim hatam. Doğru davranış: ilk turda aracı isteyip beklemekti. (1) **Ayrıştırıcımı doğrulamadan bulgu yazdım.** 4 animasyonu "pahalı" diye işaretledim, yanlıştı; regex CSS bloğunu kesemez. Yayımlamadan önce yakaladım ama yakalamasaydım utku'ya yanlış iş çıkaracaktım — kendi aracımı doğrulama adımı eksikti. (2) PO'nun sorduğu üç adaydan birini seçmem beklenirken dördüncüyü (basamaklı alan) önerdim; gerekçeyle ve `[C]` etiketiyle ayırdım ama sorunun dışına çıktığımı kabul ediyorum. (3) Animasyon süresi eşiklerini (`≤400ms`, `≤600ms`, `≤1000ms`) **ölçmedim, algı eşiği olarak önerdim** — `[C]` tercihtir; ölçüm olan yalnız mevcut 808/1222ms. Tabloda yan yana durmaları karışıklık yaratabilir. (4) Renk ölçümünü yalnız `--info` için yaptım; ikinci seri gerekirse `--ok`/`--warn` yeniden ölçülmeli — tek seri varsayımı benim, PO'nun şartı değil. (5) B6'da "taşıyor" demek kolay olurdu; `.kabuk{min-width:1180px}` bilinçli masaüstü maketi kararı olduğu için kusur değil kapsam bilgisi diye yazdım — ama bu yorumdur, PO doğrulamalı. (6) **Üçüncü turda N-2'de iki farklı sayı buldum** (`MENU` dizisi 19, DOM'da `.yan a` 20) ve farkı "1 grup dışı bağlantı" diye açıkladım — ama hangisi olduğunu tek tek doğrulamadım; ihsan sayımı bu dosyadan alırsa 19'u kullanmalı, DOM sayısı değil. (7) **yasu kapsamını devraldım ama körleme bozuldu:** salih'in "0 dış istek" ve nisa/bilo'nun "1 istek" sonuçları PO mesajı üzerinden bana aktarıldı, yani o üç hakemin çıktısını dolaylı öğrendim. Kendi ölçümüm bağımsızdı (5 istek buldum, ikisinden de farklı) ama "hiç bakmadım" diyemem; bunu saklamıyorum. (8) M1–M8/P1–P2/U1 oylarını vermedim, `[B]` yazdım. Heyet eşiği 6/6 veya ≥5/6 ise benim çekimserliğim bu soruların eşiğe ulaşmasını zorlaştırır — ama kanıtsız oy §5'e göre zaten sayılmıyor; veri yokken oy vermektense sayımı eksik bırakmayı seçtim.

---

---

## § Hakem oyu — V12B §6.1 (nur'un 10 özel sorusu)

Esas sürüm: `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` (commit `50fc414a`, teyit edildi).
V12B §7.1 PO son kararları okundu, son durum sayıldı; aşağıda yalnız **kanıtlı itiraz** var.
Körleme: diğer hakem dosyaları açılmadı.

| Kod | Cevap | Kova | Kanıt (komut + çıktı) |
|---|---|---|---|
| **N-1** | Kova A = **32**, B = **6**, C = **4**, toplam **42** | `[A]` | `IDDIA_DEFTERI.md` §3.1 (`A1`–`A32`), §3.2 (`B1`–`B6`), §3.3 (`C1`–`C4`); satır bazlı regex sayımı |
| **N-2** | **19 menü öğesi, 4 grup** — V12B'nin "26" sayısı **yanlış** | `[A]` | `const MENU` bloğu ayrıştırıldı: `id:` 19 adet; gruplar `Genel · Araçlar · Pazar · Hesap ve Destek`. Tarayıcıda `.yan a` = **20** (1 fazlası grup dışı bağlantı) |
| **N-3** | T0 ile V11B arasında **18 hex düştü, 28 hex yeni**, yalnız **3 ortak** | `[A]` | T0: 21 benzersiz hex, V11B: 31. Ortak: `#22C55E`, `#2563FF`, `#6CB6FF`. "11–12 hex farkı" ifadesi ölçümle **eşleşmiyor** |
| **N-4** | `docs/brand/` içinde OSINT **10 geçiş / 9 dosya** — hepsi "ASLA OSINT" yasak kuralı bağlamında, ihlal **yok** | `[A]` | 28 dosya tarandı. `ai-rules.md:28` "OSINT Tool." (negatif cümlenin devamı), `company.md:20` "Not an OSINT investigator toolkit", `prompts/system.md:12` "Never describe... - OSINT tool" |
| **N-5** | **Hiçbir asset prompt'a bağlanamıyor.** `LOGO.md`'nin hedef dosyalarının **8/8'i YOK** | `[A]` | `logo-primary/dark/light.png`, `favicon.png`, `app-icon.png`, `logo-option-1/2/3.png` → hepsi yok. Var olanlar: `Muninn_logo_*.png`, `image.png`. SHA-256: **7 dosya aynı** (`d5916ea6…`), 2 dosya aynı (`9def74e2…`) → 13 PNG'nin **4'ü benzersiz** |
| **N-6** | D-420 (kod yok) ve D-253 (uydurma yok) V12'yi bağlıyor; **D-253 ihlali var** | `[A]` | V11B'de `yakında` **26 geçiş**, menüde `t:'yakinda'` **2 öğe**. `ORTAK_TASARIM` K3 kararı: *"'yakında' yok (D-253)"*. Karar onaylı ama **uygulanmamış** |
| **N-7** | §8 öz-eleştiri: ölçülebilir olanlar → dış istek, kontrast, taşma, animasyon süresi, menü sayısı. Ölçülemez → "estetik üstünlük", "müşteri sever mi" | `[A]`/`[B]` | Ölçülenler bu dosyada; ölçülemeyenler `[B]` kaldı |
| **N-8** | V11B'de **"Hugin Insight" de "Huginn Insight" de geçmiyor (0/0)**; yalnız `HUGİN` 3 kez | `[A]` | Regex sayımı. Tutarsızlık **bu dosyada yok**; marka adı kısaltılmış biçimde kullanılıyor |
| **N-9** | K1–K5 PO'da onaylı; **K1 ve K3 V11B'de uygulanmamış** | `[A]` | K1 marka SSOT hex: `#09111F` YOK, `#131C2F` YOK, `#22D3EE` YOK, yalnız `#2563FF` var. K1 "OSINT rozeti kalkar" → V11B'de OSINT **9 geçiş** (menü öğesi + widget + kanca seti). K3 "yakında yok" → 26 geçiş |
| **N-10** | Format sayılabilir; **ihsan'ın sayımını bozacak tek risk** kod sütunlarının serbest metin olması | `[A]` | Bu dosyada her oy satırı `\| kod \| cevap \| kova \| kanıt \|` düzeninde; `grep -c '^| N-'` ile sayılabilir |

### İhsan'ı yanlışlama araması (brif Faz B-3, zorunlu)

**Aranan:** V12B §7.1'de PO onaylı yazılan kararların V11B'de gerçekten uygulanıp uygulanmadığı.

**Bulunan — 3 uyuşmazlık:**

1. **`#FF5A1F` risk rengi (PO-2a) gündüz temasında kritik kırmızıdan ayırt edilemiyor.** PO "turuncu sarıya benziyor" dedi, ölçüm bunu **doğrulamadı** (risk/sarı ΔE gece 53.6, gündüz 47.1 — ikisi de güvenli). Ama kimsenin bakmadığı yerde gerçek sorun var: gündüz `risk #C93A0A` vs `crit #B42318` **ΔE 13.7 < 15 eşiği**. CVD'de daha kötü: deuteranopi **11.2**, tritanopi **8.3**. **Yanlış çift denetlenmiş.** `[A]` → itiraz Kova C'ye.
2. **K1 kararı uygulanmamış.** Marka SSOT hex'lerinin 3/4'ü dosyada yok; "OSINT rozeti kalkar" denmişken OSINT 9 yerde duruyor (`OSINT Dedektifi` menü öğesi, widget başlığı, kanca seti). `[A]`
3. **K3 "yakında yok (D-253)" kararı uygulanmamış** — 26 geçiş, 2 menü öğesi `t:'yakinda'`. `[A]`

**Ayrıca gündüz `mor #6F42C1` vs `act #1F4FD8`:** normal ΔE 18.1, **protanopi 9.9** — mor ile birincil mavi protanopide ayrışmıyor. Mor yalnız "analiz" rolünde ve ikon+etiketle kullanılırsa sorun değil; tek renk kanalı olursa değil. `[A]`

### Çekirdek 12 — ölçülebilir olanlar

| Kod | Konu | Cevap | Kanıt |
|---|---|---|---|
| C8 | KPI-first varsayılan (K4) | **Uygulanmış** | `#duzen button[data-d="kpi"]` → `aria-pressed="true"` (tarayıcı) |
| C9 | Toggle varsayılanı hepsi açık (K5) | **Uygulanmış** | `localStorage.huginn_v10_gizli = []`, görünür widget **22** |
| C10 | Birincil buton Yükselt kobalt (K9) | **Uygulanmış** | satır 397 `<button class="btn birincil" id="yukselt">` |
| M9 | Üst düzey satır sayısı hedefi | **19** (≤19 hedefi tutuyor, ≤15 tutmuyor) | `MENU` ayrıştırması |
| C6 | N-paketi | §6.1 tablosunda | yukarıda |

Oy gerektiren diğer çekirdek sorular (M1–M8, P1–P2, K1, U1) **kullanım verisi istiyor** → `[B]`. V12B'nin kendi notu da bunu söylüyor: *"Menü birleştirme dayanağı eksik: kullanım verisi yok."* Ölçüm yokken oy vermem; `[B]` yazdım, kanıtsız oy sayılmaz (§5).

---

## § Ek: yasu kapsamı (nur ölçümü)

> PO kararı (22.10): yasu işi geçersiz (şablon + uydurma), kapsam nur'a devredildi. Beş başlık, her biri komut + çıktı.

### 1. Dış istek sayısı — çelişki çözüldü `[A]`

Hakemler arasında uyuşmazlık vardı: salih **0** dış istek (file://), nisa/bilo/ben **1 Google Fonts**. Gerçek tarayıcıyla ölçtüm, **ikisi de eksik**:

| Koşul | Dış istek | Başarısız | Inter yüklendi mi |
|---|---|---|---|
| Font engelsiz | **5** | 0 | evet |
| Font engelli (route abort) | 1 | 1 | hayır (fallback) |

**5 istek, 2 alan adı:** `fonts.googleapis.com/css2?...` + **4×** `fonts.gstatic.com/.../*.woff2`. `file://` üzerinden bile gidiyor — salih'in "0" ölçümü yanlış; muhtemelen ağ panelini açmadan dosyayı inceledi. "1 istek" diyen ölçüm ise yalnız CSS isteğini saymış, 4 woff2'yi kaçırmış.

**Kritik ek bulgu:** Inter **yerel olarak kurulu değil.** Üç fallback testi (`Inter,monospace` = `monospace` genişliği 449px; `Inter,serif` = `serif` 373px; `document.fonts` listesi boş) → font bloklanınca sayfa **sessizce sistem fontuna düşüyor**, kimse fark etmiyor. PO-3 "Inter onaylı" kararı, **Google erişilemezse geçersiz**.

### 2. CSP önerisi `[A]`

Envanter: inline `<style>` **1**, inline `<script>` **1**, `on*=` handler **4** (`onclick="git('firsat')"`, `git('sirket')`, `git('${o.g[1]}')`, `kpiAc('${k}')`), `style=""` özniteliği **187**, `javascript:` URL **0**, `<iframe>/<object>` **0**.

Mevcut hâliyle uygulanabilir en sıkı CSP:

```
default-src 'self';
script-src 'self' 'unsafe-inline';     <- 4 onclick + 1 inline script yüzünden
style-src  'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src   'self' https://fonts.gstatic.com;
img-src    'self' data:;
connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'
```

`'unsafe-inline'` CSP'nin XSS değerini büyük ölçüde siler. **Önerilen hedef** (4 handler `addEventListener`'a taşınır, inline script nonce alır, fontlar self-host edilir):

```
default-src 'self'; script-src 'self' 'nonce-<rastgele>';
style-src 'self' 'unsafe-inline'; font-src 'self';
img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'
```

`style-src 'unsafe-inline'` 187 inline `style=""` yüzünden kalmak zorunda; bunlar maket artığı, gerçek panelde sınıfa dönerse o da kalkar.

### 3. KVKK: font self-host gerekir mi — **evet** `[A]`

Ağ yakalamasıyla kanıtlı: sayfa her açılışta kullanıcının **IP + User-Agent** bilgisini `fonts.googleapis.com` ve `fonts.gstatic.com`'a gönderiyor. `@font-face` sayısı **0**, yani yerel kopya yok. Alman mahkemesi (LG München I, 2022) Google Fonts'u bu gerekçeyle GDPR ihlali saydı; KVKK m.9 açısından da **yurt dışına aktarım**dır ve açık rıza ya da yeterlilik kararı gerektirir.

**Teknik gerekçe ikinci kez destekliyor:** Inter yerel kurulu olmadığı için istek engellenirse tipografi sessizce bozuluyor (madde 1). Yani self-host hem KVKK hem görsel tutarlılık için gerekli — tek işle iki sorun kapanıyor. `[A]` ölçüm; "yapılsın mı" `[C]` PO kararı değil, **mevzuat gereği** `[A]`.

### 4. localStorage anahtarları `[A]`

| Anahtar | İçerik | Kişisel veri |
|---|---|---|
| `huginn_v10_gizli` | `[]` → toggle sonrası `["k-kredi"]` | **yok** |

`localStorage` **1 anahtar**, `sessionStorage` **0**, `document.cookie` **boş**. İçerik yalnız gizlenen widget id listesi. İsim/e-posta/VKN/TC araması: **hiçbiri yok**. Tracker, analytics, fingerprint kodu yok (`fetch`=0, `XMLHttpRequest`=0, `eval`=0). **KVKK açısından temiz.**

### 5. Animasyon performansı `[A]`

Chromium `getAnimations()` + keyframe özellik ayrıştırması:

| Ölçüm | Değer | yasu eşiği (60 eleman) |
|---|---|---|
| Sayfa açılışı toplam animasyon | **42** | altında |
| 30 çubuk seçilince anlık | **58** | altında (sınıra 2 kala) |
| **Layout tetikleyen** | **0** | — |
| Compositor (`transform`/`opacity`) | 42: `navGir` 20, `grow` 14, `popin` 4, `growx` 3, `don` 1 | — |
| `prefers-reduced-motion: reduce` | **0 animasyon** | tam kapanıyor |

Hiçbir animasyon `height`/`width`/`top`/`left`/`margin` değiştirmiyor → hepsi GPU katmanında, layout/paint tetiklemiyor. **Pil ve düşük cihaz riski düşük.** Tek sürekli animasyon `don` (radar taraması, 4000 ms sonsuz) — `reduce`'ta duruyor.

**Uyarı:** 30 çubuk hâli **58/60**, eşiğe 2 kala. Yeni grafik (halka + basamaklı alan) eklenirse eşik aşılır. Önerilen kural: kademeli animasyon **30 öğeden sonra kapansın** (`i > 30 ? 0 : i*18`) — bu hem 1222 ms süreyi hem 60 eleman eşiğini aynı anda çözer.

**FPS ve gerçek pil tüketimi ölçülmedi** (CPU throttling altında kare sayımı yapılmadı) → `[B]`.

---

## Ilgili Nodlar

- [[Huginn Data Insights/docs/MUSTERI_PANEL_RENK_SISTEMI]] — ölçülmüş palet, iki tema, kontrast kapıları
- [[Huginn Data Insights/docs/MUSTERI_PANEL_IDDIA_DEFTERI]] — üç kova yöntemi ve kanıt hanesi
- [[Huginn Data Insights/docs/MUSTERI_PANEL_HAKEM_SORULARI_V12B]] — soru seti ve PO son kararları
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] — müşteri paneli hub
