# MUSTERI_PANEL_ORTAK_TASARIM.md Ã¢ÂÂ Ortak Taslak ve GÃÂ¶rÃÂ¼ÃÂ Defteri

> Amaç: müşteri paneli iskeleti için TÜM ajanlar repoya/ürüne bakıp kendi taslağını ve geliştirme önerisini tek yere yazar.
> Sahip: ihsan (derler). Karar: PO. Bu belge karar DEĞİL, görüş toplama defteridir.
> Kural: uydurma rakam/etiket yok (D-253/D-395). Her öneri bir dosyaya/ölçüme dayanır (D-382). Tek belge, ikinci kopya yok (D-211).

## 1. Ä°skelet nerede? (dosya haritasÄ±)

| Ne | Dosya |
|---|---|
| Rota | [`page.tsx`](../frontend-web/app/panel-tasarim/page.tsx) → `/panel-tasarim` |
| Bileşen (üst bar, yan bar, KPI, grafik, tablo yeri) | [`panel-kabuk.tsx`](../frontend-web/app/panel-tasarim/panel-kabuk.tsx) |
| Stil / animasyon / palet | [`kabuk.css`](../frontend-web/app/panel-tasarim/kabuk.css) |
| Test (3 adet, gövdede rakam aramaz) | [`panel-kabuk.test.tsx`](../frontend-web/app/panel-tasarim/panel-kabuk.test.tsx) |
| Brif | [`brief_utku_MUSTERI-PANEL-TASARIM-01.md`](../plans/brief_utku_MUSTERI-PANEL-TASARIM-01.md) |
| Rapor | [`MUSTERI-PANEL-TASARIM-01_rapor_2026-10-19_uretim.md`](../data/orchestrator/MUSTERI-PANEL-TASARIM-01_rapor_2026-10-19_uretim.md) |
| AkÄ±Å haritasÄ± | [`MUSTERI-PANEL-TASARIM-01_akis_haritasi.md`](../data/orchestrator/MUSTERI-PANEL-TASARIM-01_akis_haritasi.md) |
| Ekran görüntüsü | `data/orchestrator/MUSTERI-PANEL-TASARIM-01_iskelet_masaustu_2026-10-19.png` |
| Hub | [`MUSTERI_PANELI_HUB.md`](../hubs/MUSTERI_PANELI_HUB.md) |
| CanlÄ± eski panel (karÅÄ±laÅtÄ±rma) | `frontend-web/app/panel` (bozulmadÄ±) |

Yerel önizleme: `http://localhost:3000/panel-tasarim`.

## 2. Mevcut iskelet (özet)

| Bölge | İçerik |
|---|---|
| Üst bar | Genel Bakış · Radarlar · Firmalar · Raporlar · Krediler |
| Yan bar | İZLEME (Canlı Akış, Sinyaller, Takip Listem) · ANALİZ (Firma Analizi, Sektör Radarı, Raporlarım) · HESAP (Kredi ve Paket, Ayarlar) |
| Gövde | 4 KPI yeri · 2 grafik yeri (Sinyal Yoğunluğu, Sektör Dağılımı) · "Son Hareketler" tablo yeri |
| Palet | #0D1B2A zemin · #10233A panel · #E6EDF3 metin · #8FA3B8 ikincil · #00FF66 / #0072FF vurgu |
| Bilinen eksik (ihsan öz-eleştirisi) | Sağ üst boş · yoğunluk düşük · Next dev rozeti görünüyor · canlı tarayıcıda denenmedi |

## 3. Referans havuzu (Open Design)

| Paket | Neden bak |
|---|---|
| `open-design/design-systems/mission-control/DESIGN.md` | Lacivert + amber, bizim palete yakÄ±n |
| `open-design/design-systems/trading-terminal/DESIGN.md` | YoÄun, sinyal renkleri (Bloomberg tarzÄ±) |
| `open-design/design-templates/dashboard`, `trading-analysis-dashboard-template`, `wireframe-greybox` | YerleÅim fikri |

Kullanım: yalnız referans (kod kopyalanmaz). Kopyalanırsa lisans notu `design/LISENS.md`'ye yazılır. Bkz. §6.

## 4. Her ajan için görüş bölümü

Format (her ajan KENDİ bölümünü doldurur, başkasınınkini düzenlemez):

1. **Baktığım yer** (dosya/ölçüm, en az 2 kanıt)
2. **Sorun / eksik** (en çok 3 madde)
3. **TaslaÄÄ±m** (ASCII Åema veya liste; rakam uydurma yok)
4. **2 alternatif** (artÄ±/eksi)
5. **Öz-eleştiri** (kendi taslağımın zayıf yanı)

| Ajan | Rol | Odak sorusu | Durum |
|---|---|---|---|
| utku | Frontend | Ä°skelet kodu nasÄ±l bileÅenleÅir? `/panel`e taÅÄ±ma riski? | bekliyor |
| yasu | Backend/KVKK | Hangi kutu hangi API/tabloya bağlanır? Müşteriye gösterilmeyecek veri ne? | **doldu (§4.4)** |
| bilo | Altyapı/dış ajan | Canlı yayın, imaj, performans, mobil yükleme? | **doldu (§4.8)** |
| salih | Test/UX denetçi | Hangi senaryo kırılır? Erişilebilirlik, mobil, boş durum? | bekliyor |
| mimir | Asistan (yalnız asistan, D-410) | Sağ üstte Mimir balonu nasıl durur? Soru-cevap girişi nerede? | araçsız; **ihsan notu (§4.5)** |
| ihsan | Orkestratör | Yol sırası, makespan, karar kapıları | **doldu (§4.6)** |
| ihsan (müşteri gözü) | Orkestratör | Öncelik, TR/EN, öğretici, Mimir balonu | **doldu (§4.10)** |
| Codex ajanı | Araştırma/tasarım sentezi | Marka, tek menü, karar odaklı dashboard, grafik ve müşteri güveni nasıl birleşir? | **doldu (§4.7)** |
| Claude | Dış ajan / veri-görselleştirme + ölçüm | Grafik paleti ölçülebilir mi? Marka kiti hangi SSOT? | **doldu (§4.8b)** |


### 4.2 yasu — Backend/KVKK

**Skill beyanı:** `api-and-interface-design` + `security-and-hardening`. Diğer ajanın alanıyla çakışma yok: utku (frontend bileşen/rota), salih (test/a11y/boş durum), bilo (altyapı/canlı yayın/performans), mimir (yalnız asistan, D-410). Yasu yalnız veri sınırı ve KVKK maskeleme konusuna odaklanır.

#### 1. Baktığım yer (≥2 kanıt)

- `panel-kabuk.tsx:14-45` — menü/kutu tanımları (Genel Bakış, Radarlar, Firmalar, Raporlar, Krediler; İZLEME/ANALİZ/HESAP grupları). İçerik: sadece "yer tutucu", API-ısketleme katmanı yok. [Kanıt: dosya okundu]
- `src/company_master/paketler.py:208-282` — `PAKET_V2`, `PAKET_MAX_USER`, `KREDI_TRY=50.0`, `RAPOR_KREDI=0.5`. Kredi/paket SSOT. [Kanıt: dosya okundu]
- `src/company_master/sinyal/kapasite_sinyal.py:1-16` — `signal_type="supply"`, 7.595 kapasite satırı, idempotent DELETE+INSERT. [Kanıt: SINYAL-3KAYNAK-TASARIM-01 brief'inde]
- `docs/strateji/STRATEJI_10_UC_BEDAVA_KAYNAK_SINYAL.md:180-191` — V2 paket fiyat çelişkisi, 499/2.999/7.999/19.999 ₺, radar etiketleri. [Kanıt: dosya okundu]
- `docs/MUSTERI_PANEL_BRANDING_V2_ONERI.md:22-33` — palet/ikon/grafik çakışması (`#0072FF` vs `#2563FF`, emoji vs lucide-react, CSS bar vs recharts). [Kanıt: dosya okundu]

#### 2. Sorun / eksik (en çok 3 madde)

1. **API-ısketleme sözleşmesi yok.** `panel-kabuk.tsx`'te her kutu "yer tutucu"; hangi kutu hangi API endpointine (`/api/firma/[vkn]`, `/api/sinyal`, `/api/rapor`, `/api/cuzdan`) bağlanıyor, hangi sütun müşteriye gösterilir, hangi sütun KVKK ile maskelenir — bu bölüm yok.
2. **Durum rozeti / KVKK maskeleme çakışması.** `#00FF66` / `#0072FF` vurgu renkleri, KVKK durum paleti (`#0ca30c` iyi, `#fab219` uyarı, `#e8743c` ciddi, `#d03b3b` kritik) ile karışabilir. `design-tokens.json` SSOT ama panel-kabuk'ta kullanılmıyor (bilo §4.8 ile örtüşmez, yasu sadece KVKK açısından uyarıyor).
3. **OSB koordinat verisi yok.** `osbs` tablosundaki koordinat kolonu doğrulanmadı; `companies.osb_parcel` %0,2 dolu ve "yeni açılacak parsel listesi" DEĞİL. Harita yuva boş kalıyor (Ankara 15 OSB, koordinat henüz ölçülmedi).

#### 3. TaslaÄÄ±m (ASCII Åema; rakam uydurma yok)

```
Müşteri Paneli — Veri Sınırı (yasu/KVKK)
┌ Üst bar: Genel Bakış · Radarlar · Firmalar · Raporlar · Krediler
│  └ API katmanı: /api/firma/[vkn] · /api/sinyal · /api/rapor · /api/cuzdan
│  └ MÜŞTERİYE GÖSTERİLEN: unvan, il/ilçe, sektör, kredi bakiyesi, paket, sinyal özeti
│  └ MÜŞTERİYE GÖSTERİLMEYEN (KVKK maskeleme): TC kimlik, tam vergi no, banka hesap, iç notlar
├ Yan bar: İZLEME · ANALİZ · HESAP
│  └ Kredi ve Paket → /api/cuzdan/{kullanici} → paketler.py PAKET_V2 + KREDI_TRY
│  └ Firma Analizi → /api/firma-analiz/{vkn} → company_signals + company_capabilities
├ Gövde: 4 KPI · 2 grafik · Son Hareketler
│  └ KPI: sadece agregasyon (toplam sayı), firma listesi YOK
│  └ Son Hareketler: eylem tipi + tarih + durum rozeti, firma VKN MASKELİ (***1234)
└ Harita yuva: OSB noktaları → osbs (Ankara 15 OSB), koordinat yok, parsel = ORNEK yuva
```

#### 4. 2 alternatif (artÄ±/eksi)

| | **A — KVKK maskeleme katmanı önce** (önerilen) | **B — Maskeleme dolgu sonrası** |
|---|---|---|
| Yöntem | Her API yanıtı önceden filtrelenir; müşteri görünümünde maskelenmiş alanlar `null` veya `***` ile dönülür | Önce tüm veri gösterilir, sonradan KVKK maskeli katman eklenir |
| Artı | Müşteriye asla hassas veri kaçmaz; `tests/test_api_*.py` ile test edilebilir | Görünüşte hızlı ilerleme, PO için kolay |
| Eksi | Her endpoint için ayrı serializer/DTO yazmak gerek; daha çok kod | Veri sızdırma riski yüksek; `/panel`'e taşınırken aynı hata tekrar eder; D-253 riski |
| Ölçüm | KVKK-11 madde hakları (erişim, silme, anonimleştirme) doğrudan desteklenir | Salih K-4 durum matrisi ve KVKK denetimi daha sonra kırılabilir |

#### 5. Öz-eleştiri

- Müşteri paneline yönelik API spec'i (OpenAPI/Swagger) henüz yok; "API katmanı" iddiam koddan değil, niyetten geliyor (D-382: ölçmediğimi gördüğüm saymıyorum).
- `osbs` tablosundaki koordinat kolonunu henüz kendim ölçmedim — "15 Ankara OSB" rakamı PO talebi, benim ölçümüm değil.
- Mimir balonu salt okunur (D-410) ama Mimir'in kota/paket sorgusu (D-395) yasu tarafÄ±nda mÄ± yoksa utku/backend mi, belirsiz.

**Skill atamasÄ± (PO 2026-10-21: "herkes aynÄ± skille yorum yapmasÄ±n").** Her ajan farklÄ± mercek kullanÄ±r; beyan zorunlu (D-383):

| Ajan | Mercek skill'i | Neye bakar |
|---|---|---|
| utku | `frontend-ui-engineering` + `source-driven-development` | BileÅenleÅme, Next.js doÄrulamasÄ±, `/panel`e taÅÄ±ma |
| salih | `browser-testing-with-devtools` + `frontend-ui-engineering` (a11y) | Gerçek tarayıcı: klavye, ekran okuyucu, mobil, boş durum |
| yasu | `api-and-interface-design` + `security-and-hardening` | Kutu↔API sözleşmesi, KVKK veri sınırı |
| bilo | `frontend-ui-engineering` (perf) + `browser-testing-with-devtools` | Yükleme bütçesi, imaj, mobil, canlı yayın |
| Claude | ölçüm betikleri + veri-görselleştirme | Grafik paleti ölçümü, marka SSOT çatışması (§4.8b) |
| mimir | `documentation-and-adrs` | Asistan balonu konumu, metin dili (D-410) |
| ihsan | `planning-and-task-breakdown` | Yol sÄ±rasÄ±, kapÄ±lar, derleme |
| Codex ajanı | `frontend-design` + `elite-product-ux-architect` + `better-*` + `interface-review` | IA, ürün deneyimi, marka sentezi, grafik sözleşmesi (§4.7) |

### 4.1 utku — iskeleti yazan ajanın kendi kodundan, ölçülmüş taşıma görüşü (2026-10-21)

**Kapsam:** görüş/öneri; PO onayı olmadan kod kararı değildir. Codex (§4.7) bilgi mimarisi ve marka dilini, Claude (§4.8) grafik paletini ölçtü. Ben **iskeleti yazan** olarak kendi kodumu gerçek panelle karşılaştırdım ve `/panel`e taşıma riskini ölçtüm. Ölçümler `data/_tmp/olcum_4_1.md` ve `olcum_rota.md` (betik: `_tmp/olcum_4_1.py`, `_tmp/olcum_rota.py`).

**Skill beyanı (D-401):** `frontend-ui-engineering` (tema tokeni, durum, erişilebilirlik) + `interface-review` (değişiklik kapsamı). `dataviz`/`frontend-design` kasıtlı kullanılmadı: palet/grafik formunu Claude, bilgi mimarisini Codex işledi; aynı mercekle aynı sonuca varmak değer üretmez (PO: "herkes aynı skillerle yorumlamasın").

#### 1. Baktığım yer (ölçüm)

| Kanıt | Ölçüm | Sonuç |
|---|---|---|
| `panel-kabuk.tsx` vs gerçek panel, renk kaynağı | iskelet: **33 sabit hex**, **0 tema tokeni**; gerçek panel (12 dosya): **0 sabit hex**, **21 tema tokeni** | İskelet gerçek panelin tema altyapısını (`ThemeProvider` + `responsive.css` `.dark`) **kullanmıyor**. `/panel`e olduğu gibi taşınırsa dark/light geçişi bozulur, 33 yer elle sökülür |
| `responsive.css` | token tanımı **24**, `.dark` bloğu **1** (`_tmp/dogrula_iddia.py` ile ölçüldü) | Tema tokeni zaten var; iskelet bunu atladı. Yeni renk eklemek için yeni token gerekir, hex değil |
| `panel-kabuk.tsx` gezinme | `next/link`/`usePathname`/`<Link>` = **0**; `useState` = **3** | Menü **sahte**: tıklamak yalnız başlığı değiştirir, rota değiştirmez. Gerçek sidebar **5** `Link` kullanıyor. İskelet yalnız "nasıl görünür"ü gösterir, "nasıl gezilir"i **göstermez** |
| `panel-sidebar.tsx` | **5** öğe: Panel, Radar, RaporLab, UBO Ağı, Cüzdan; **2'si `yakinda`** (Radar, UBO Ağı) | İskelet **8** öğe çiziyor, gerçek panel **5**. Aradaki 3 öğe (Sinyaller, Takip, Canlı Akış…) için ne rota ne veri var |
| `app/panel/**/page.tsx` | 4 sayfa: `panel`, `cuzdan`, `raporlab`, `sektor-radar` | **`sektor-radar` sayfası var ama sidebar'da yok** (ulaşılamaz sayfa). İskelet "Sektör Radarı"nı menüye koymuş ama `/panel/sektor` rotası yok → gerçek rota `/panel/sektor-radar` |
| `package.json` | `recharts` **VAR**, `lucide-react` **VAR**, `next-themes` **VAR**, `framer-motion` **YOK**; recharts import eden dosya **0** | Grafik kütüphanesi kurulu ama hiç kullanılmamış; bir bağımlılık ekleme kararı gerekmiyor. Animasyon için framer-motion **eklenmesin**, CSS yeterli |
| `panel-kabuk.tsx:66` | bar yükseklikleri `[38,62,46,78,55,88,64,72]` | **Kendi hatam:** farklı yükseklikler sahte trend okutuyor. §4.7 ve §4.8 bağımsız teyit etti. Eşit yükseklikli nötr skeleton olmalı |
| Kontrast (hesaplandı) | `#0072FF` mavi / zemin **4.02**, / kart **3.67**; `#8FA3B8` ikincil / kart **6.12**; beyaz / `#0072FF` dolgu **4.33** | **Mavi `#0072FF` metin olarak AA'yı geçmiyor** (4.02 < 4.5). Yalnız büyük metin/ikon/çizgi için uygun. Mavi dolgulu düğmede beyaz yazı da **4.33 < 4.5** (AA kalıyor) |

#### 2. Sorun / eksik (3 madde)

1. **Kabuk gerçek panelden kopuk yazıldı; taşıma "kopyala-yapıştır" değil "yeniden yaz".** Sabit hex 33, token 0; menü rota değiştirmiyor; 3 menü öğesinin hedef sayfası yok. Bu benim hatam: PO "boş iskelet" istedi, ben görsel olarak doğru ama **altyapıdan bağımsız** bir kabuk yazdım. Onay çıkarsa `/panel`e geçiş 224 satırın yeniden yazımıdır, taşıması değil.
2. **Mavi `#0072FF` erişilebilirlik sınırında.** Düğmede beyaz yazı 4.33:1 (AA için 4.5 gerekir). Kendi Faz A'mda (`kvkk-onay.tsx`) aynı `#0072FF` + beyaz yazıyı kullandım; **Faz A düğmem de AA'yı geçmiyor.** Claude'un önerdiği `#2563FF` primary için bu oranı ölçmem gerekiyor (aşağıda önerim).
3. **Sidebar'daki "yakında" öğeleri (Radar, UBO Ağı) ile iskeletteki 8 öğe çelişiyor.** Müşteri "çalışmayan" bir menü görüyor. Menü, **var olan 4 sayfa + kredi + yakında rozetli planlananlar** olarak başlamalı; hayali sayfa menüye girmemeli.

#### 3. Taslağım — taşıma planı ve menü düzeni (ölçüme dayalı)

**Menü: 5 öğe, 2 grup (gerçek panelle birebir başlar, sonra büyür)**

| Grup | Öğe | Rota | Durum bugün |
|---|---|---|---|
| ÇALIŞMA | Panel | `/panel` | var |
| ÇALIŞMA | Sektör Radarı | `/panel/sektor-radar` | **sayfa var, menüde YOK → ekle** |
| ÇALIŞMA | RaporLab | `/panel/raporlab` | var |
| ÇALIŞMA | Radar | `/panel/radar` | yakında (rozetli) |
| HESAP | Cüzdan | `/panel/cuzdan` | var |

UBO Ağı: `yakinda` kalır ama menüde **yalnız rozetli** durur; iskeletteki Sinyaller/Takip/Canlı Akış/Firma Analizi/Raporlarım menüden **çıkar** (rota yok, veri yok, D-253). Menü bir PO kararıyla büyür, iskeletle değil.

**TaÅÄ±ma sÄ±rasÄ± (hepsi PO onayÄ± sonrasÄ±)**

| Adım | İş | Ölçülebilir çıkış |
|---|---|---|
| T-1 | `panel-kabuk.tsx`'in 33 sabit hex'ini `responsive.css` tokenlarına çevir; yeni renk gerekirse **token** ekle | sabit hex = 0, `.dark` altında görsel bozulma yok (Playwright dark+light ekran) |
| T-2 | Sahte `useState` menüsünü `next/link` + `usePathname` yap | tıklama rota değiştirir, `aria-current` doğru öğede |
| T-3 | Menüyü 5 öğeye indir, `sektor-radar`ı ekle | `app/panel/**/page.tsx` sayısı = sidebar öğe sayısı (yakında hariç) |
| T-4 | Bar placeholder'ı eşit yükseklikli nötr skeleton yap | farklı yükseklik dizisi = 0 |
| T-5 | Mavi `#0072FF` metin kullanımını kaldır; düğme/seçili durum rengini AA'yı geçen tona çek | metin kontrastı ≥ 4.5 (hesapla, tahmin etme) |

**Marka kiti — bence ayrı üç şey karışıyor, ayrılmalı:**
- **Yüzey/metin/eylem** (Codex §3.7) ve **veri mürekkebi** (Claude §4.8) ayrı token ailesi. İkisi de gerçek panelin `responsive.css` tokenına yazılır; **ikinci bir `customerPanel` JSON'u açılmaz** (D-211): `design-tokens.json`'a `customerPanel` kapsamı eklenir **veya** `responsive.css` kanonik ilan edilir. İkisi birden olmaz.
- **Hangisi SSOT?** Tek ölçülmüş gerçek: gerçek panel **şu an `responsive.css` tokenını** kullanıyor (21 yer), `design-tokens.json`'ı **hiç** kullanmıyor. Önerim: `responsive.css` kanonik kalır, `design-tokens.json` o dosyaya **bağlanır** (tek yönlü senkron testi), tersine değil. Aksi halde çalışan 21 yeri sökmek gerekir.

#### 4. Ä°ki alternatif (PO kapÄ±sÄ±)

| | Alternatif A — Taşıma önce | Alternatif B — Marka kararı önce |
|---|---|---|
| Ne | T-1…T-5'i yap, mevcut `#0D1B2A`/`#0072FF` paletiyle | Önce palet kararı (SSOT çatışması: `#09111F`/`#2563FF` mi `#0D1B2A`/`#0072FF` mi), sonra T-1 |
| Artı | Hızlı, iskelet canlı panele oturur | Taşınan şey doğru renkle gelir, ikinci söküm olmaz |
| Eksi | Palet sonradan deÄiÅirse T-1 **yeniden** yapÄ±lÄ±r (33 yer) | PO kararÄ± gelene kadar iskelet bekler |
| Önerim | | **B** — token tabanlı T-1 palete bağımlı değil ama değerleri palete bağlı; sökümü ikiye bölmek en pahalı yol |

**Kendi önerim: B, ama T-2/T-3/T-4 palete bağımlı değil, onlar hemen yapılabilir.** Yani palet kararı gelene kadar menü rotalarını, sahte trendi ve ulaşılamaz sayfayı düzeltirim; sadece renk değerlerine dokunmam.

#### 5. DoÄrulanmamÄ±Å / bilmediÄim (uydurmuyorum)

- `#2563FF` primary için beyaz yazı kontrastını **ölçmedim**; Claude'un PASS'ı seri rengi içindi, düğme dolgusu için değil. Palet kararı sonrası hesaplarım.
- Gerçek panelin dark modda iskeletten daha iyi mi göründüğünü **görsel olarak** karşılaştırmadım (yalnız kod ölçtüm). T-1 sonrası Playwright dark+light ile doğrularım.
- Müşteri davranışı (hangi menü öğesini ilk arar) hakkında veri yok; menü sırası tahmindir, PO/analitik doğrular.

#### 6. Çakışma notu (Codex §4.7 / Claude §4.8 ile)

| Konu | Durum |
|---|---|
| Sahte bar yükseklikleri | **Üçümüz de bağımsız buldu** (güçlü teyit) |
| "OSINT" rozeti marka kuralÄ±nÄ± ihlal ediyor | Claude'a **katÄ±lÄ±yorum**; ben brife uydum, kural `ai-rules.md`'de. Rozet PO kararÄ±na kadar kaldÄ±rÄ±lmalÄ± |
| `#00FF66` seri rengi olamaz | Claude'a **katılıyorum**; ben onu KPI/aksan için kullandım, grafik serisi için değil |
| Sektör Dağılımı çizgi olmalı mı | Claude ve Codex "yatay bar" diyor; **katılıyorum** (kategori verisi) |
| Menü öğesi sayısı | **Ayrışıyoruz:** Codex tek menü + daha çok öğe öneriyor; ben **5 öğeyle başlayıp** yalnız var olan sayfayı göstermeyi savunuyorum (hayali menü D-253'e aykırı) |
| `design-tokens.json` mi `responsive.css` mi SSOT | **Ayrışıyoruz:** Claude marka JSON'unu SSOT sayıyor; ben çalışan 21 yerin `responsive.css`'e bağlı olduğunu ölçtüm, JSON'un panelde **0** kullanımı var → `responsive.css` kanonik, JSON ona bağlansın |

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
- [[Huginn Data Insights/data/orchestrator/MUSTERI-PANEL-TASARIM-01_akis_haritasi]]

### 4.2 yasu
_(bkz. üstte §4.2 — yasu görüşü belgenin başına taşındı)_

### 4.3 bilo
_(bkz. §4.8 — bilo görüşü oraya taşındı; PO 2026-10-21: bilo bölümü §4.8)_

### 4.4 salih — öğretici (madde 7) ve Mimir balonu (madde 8) kırılma senaryoları + TR/EN aksan mandalı (2026-10-21)

**Kapsam:** görüş/öneri. PO onayı olmadan kod kararı değildir. ihsan §4.10'da madde 7 ve 8'in *ne olacağını* yazdı; ben **nasıl kırılacağını** yazıyorum. Denetçi gözü: her satır bir kabul kapısı adayı.

**Skill beyanı (D-401):** `web-design-guidelines` (Vercel — §Accessibility / §Focus States / §Anti-patterns) + `browser-testing-with-devtools`. Aynı belgede §4.9'da kullandığım skill'in devamı, çünkü konu aynı ailede (erişilebilirlik + klavye). `dataviz`/`frontend-design` yine kullanılmadı (rotasyon).

**Kanıt tabanı:** §4.9 + §2.12'deki gerçek tarayıcı ölçümleri (5 viewport, 5 PNG) ve `docs/MUSTERI_PANEL_IDDIA_DEFTERI.md` §2.12. Yeni ölçüm yapmadım — bu bölüm **senaryo listesi**, ölçüm raporu değil.

---

#### 1. Madde 7 — Öğretici sistemi: 6 katmanın kırılma senaryoları

ihsan §4.10/7 altı katman tanımladı. Her katman için **kırılma + ölçüm + karar**:

| Katman | Kırılma senaryosu | Nasıl ölçülür | Karar |
|---|---|---|---|
| **1. Karşılama kontrol listesi** | Profil bayrağı yazılamazsa (ağ hatası) liste her girişte sıfırdan başlar → "3 adımı bitirdim, yine başladı" | Ağ kes → adım işaretle → yenile. Bayrak kalıcı mı? | **KALDI** kabul: bayrak yazımı başarısızsa kullanıcıya "kaydedilemedi" de, sessizce sıfırlama **yasak** |
| **2. Kısa tur (4-5 durak)** | "Atla" düğmesi tur bitince **geri gelmiyor**; kullanıcı turu bir daha açamıyor | Turu bitir → Yardım menüsünde "Turu yeniden başlat" var mı? | **KALDI** kabul: yeniden başlatma yolu her zaman erişilebilir olmalı (ihsan §4.10/7'de yazıyor, mandal yok) |
| **2b. Kısa tur — klavye** | Tur overlay'i açıkken `Tab` arkadaki panele kaçar; odak tuzağı yok | Overlay açıkken 20× `Tab` → odak overlay dışına çıkıyor mu? | **KALDI** kabul: `role="dialog"` + `aria-modal` + odak tuzağı. **Bu, madde 8 ile aynı mandal** |
| **3. Boş durum rehberi** | Boş kart "ne yapınca dolar" diyor ama **tek buton** yok → kullanıcı okur, yapamaz | Boş durumda tıklanabilir hedef say | **KALDI** kabul: boş durumda **tam 1** CTA (0 = rehber değil, 2+ = karar felci) |
| **4. Bağlamsal "?"** | "?" yalnız hover ile açılıyor → dokunmatikte erişilemez (§4.9 A27 ailesi) | Dokunmatik emülasyonda (320px) "?" açılıyor mu? + klavye `Enter` | **KALDI** kabul: hover-only tooltip **yasak**; `button` + `aria-expanded` + `Esc` |
| **4b. "?" içeriği** | "Ne ölçer / nasıl hesaplanır / nasıl yorumlanır" 3 satırı **veri yokken** uydurma sayı içeriyor | Metin grep: rakam var mı? (D-253) | **KALDI** kabul: açıklama metni rakamsız; örnek gerekiyorsa `[ORNEK]` etiketli |
| **5. Yardım merkezi** | Kılavuz TR var, EN yok → dil değişince boş sayfa | `en` sözlüğünde kılavuz anahtarları var mı? | **KALDI** kabul: ihsan §4.10/6 "her durum iki dilde yazılı olmadan sayfa bitti sayılmaz" — kılavuz da buna dahil |
| **6. Mimir** | Öğretici içinde Mimir'e "sor" bağlantısı var, ama Mimir **dil değişince eski dilde** yanıt veriyor | Dil değiştir → Mimir'e sor → yanıt dili? | **KALDI** kabul: ihsan §4.10/8 "bir sonraki yanıttan itibaren" — mandal: dil değişiminden **sonraki ilk** yanıt yeni dilde |

**Öğreticinin en ağır riski (kimse yazmadı):** 6 katmanın hepsi **ilk girişte aynı anda** tetiklenirse kullanıcı 4 overlay üst üste görür (karşılama listesi + tur + Mimir karşılaması + dil ipucu). **Sıra sözleşmesi** gerekir:

```
1. giriş → yalnız ① karşılama listesi
① tamamlanınca → ② tur teklifi (tek sefer, atlanabilir)
② bitince/atlanınca → ⑥ Mimir ilk mesajı (yalnız kullanıcı balonu açarsa)
Dil ipucu → hiç gösterilmez (varsayılan TR zaten doğru)
```

Mandal: **aynı anda en fazla 1 öğretici katmanı görünür.** Test: ilk girişte `document.querySelectorAll('[data-ogretici]').length <= 1`.

---

#### 2. Madde 8 — Mimir balonu erişilebilirliği: kırılma senaryoları

ihsan §4.10/8'de `aria-label`, `role="dialog"`, `aria-live="polite"`, klavye istedi. Bunları **ölçülebilir mandala** çeviriyorum:

| # | Kırılma | Nasıl ölçülür | Eşik |
|---|---|---|---|
| **B1** | FAB düğmesinde `aria-label` yok → ekran okuyucu "button" der | axe `button-name` kuralı | **0 ihlal** |
| **B2** | Panel açılınca odak panele **girmiyor** (klavye kullanıcısı arkada kalır) | Aç → `document.activeElement` panel içinde mi? | Panel içinde |
| **B3** | `Esc` kapatmıyor | `Esc` bas → panel kapandı mı? | Kapanır |
| **B4** | Kapanınca odak **FAB'a dönmüyor** (odak `<body>`'ye düşer) | Kapat → `activeElement` FAB mı? | FAB |
| **B5** | `Tab` panelden kaçıyor (odak tuzağı yok) | Panel açık, 20× `Tab` → odak dışarı çıkıyor mu? | Çıkmaz |
| **B6** | Yeni mesaj ekran okuyucuya duyurulmuyor | `aria-live="polite"` canlı bölge var mı + `role="log"` | Var |
| **B7** | Mobilde panel tam ekran açılıyor ama **kapatma düğmesi güvenli alanda değil** (çentik altında) | 320px + `env(safe-area-inset-bottom)` | Kapatma erişilebilir |
| **B8** | Panel açıkken **arka plan kayıyor** (scroll lock yok) | Panel açık, tekerlek → `body` scroll ediyor mu? | Etmez (`overscroll-behavior: contain`) |
| **B9** | "Yazıyor…" göstergesi **yalnız görsel** → ekran okuyucu beklemiyor | `aria-live` + metin var mı | Var |
| **B10** | Kota/hata durumu **renk ile** anlatÄ±lÄ±yor, metin yok | Durum metni grep + ikon | Metin + ikon var |
| **B11** | FAB dokunma hedefi <24px | `getBoundingClientRect` | **≥24×24** (WCAG 2.5.8), konfor için ≥44 |
| **B12** | FAB, sayfa içeriğini kapatıyor (mobilde son satırı örtüyor) | 320px'te son öğe `elementFromPoint` | Örtmez |
| **B13** | `prefers-reduced-motion` altında açılma animasyonu sürmüyor | media query emülasyonu | Animasyon kapalı |
| **B14** | Dil değişince panel **açık kalıyor ama eski dilde** | Dil değiştir, panel açıkken | Bir sonraki yanıt yeni dilde |

**Yeni bulgu (ihsan §4.10/8'de yok):** B12 — FAB sağ altta sabit. §2.12'de ölçtüğüm **320px yatay taşma** (A28) hâlâ açıkken FAB, taşan içeriğin üstüne biner. Yani A28 düzeltilmeden FAB'ın mobil konumu **ölçülemez**. Sıra: **A28 → B12**.

**İkinci yeni bulgu:** Mimir paneli `role="dialog"` ise **`aria-modal="true"`** olmalı ve arka plan `inert` olmalı. Yoksa ekran okuyucu arka plandaki KPI'ları okumaya devam eder — kullanıcı "iki ekran aynı anda" duyar. `inert` desteği: Chrome 102+, Safari 15.5+, Firefox 112+; desteklenmeyen tarayıcı için `aria-hidden` fallback.

---

#### 3. TR/EN aksan mandalı — ölçülebilir hali

ihsan §4.10/6 "aksansız TR metin hata sayılır" diyor ama **mandal yok**. Somut öneri:

**M-1 Sözlük aksan testi (vitest):**

```
Yasaklı aksansız kelime listesi (TR sözlüğünde geçemez):
Canli, Henuz, Sirket, Kredi Karti, Iptal, Guncelle, Yukle, Ara, Cikis,
Bilgi, Dogrula, Kaydet, Sil, Ekle, Duzenle, Ayarlar, Rapor, Sektor, Analiz,
Ozet, Detay, Sonuç, Basarili, Basarisiz, Hata, Uyari, Bekliyor, Tamamlandi
```

Test: `tr` sözlüğünün tüm değerleri bu listeye karşı taranır → **0 eşleşme**. Eşleşme varsa test kırmızı, dosya:satır raporlanır.

**Neden bu liste:** §2.12'de gerçek tarayıcıda gördüğüm metinler doğru aksanlıydı (`Müşteri Paneli`, `Sektör Dağılımı`, `canlı veri bağlanacak`) — yani bu hata **henüz yok**. Mandal, sözlüğe geçiş sırasında **oluşmasını** engellemek için. Kapı olmadan, 200+ anahtar elle çevrilirken 3-5 tanesi mutlaka aksansız girer.

**M-2 Genişleme testi (EN):** `en` değerleri TR ile **aynı anahtar kümesinde** olmalı; eksik anahtar = test kırmızı. (ihsan §4.10/6 "her durum iki dilde" kuralının mekanik hali.)

**M-3 Uzunluk testi:** EN metni TR'den %40'tan fazla uzunsa uyarı (düğme taşması riski). Sert hata değil, rapor.

**M-4 `lang` özniteliği:** dil değişince `<html lang>` güncellenmeli. Test: dil değiştir → `document.documentElement.lang === 'en'`.

---

#### 4. Sayısal özet (bu bölümün çıktısı)

| Grup | Mandal sayÄ±sÄ± | En aÄÄ±r risk |
|---|---|---|
| Öğretici (madde 7) | **9** (6 katman + 2b klavye + 4b içerik + sıra sözleşmesi) | Aynı anda 4 overlay → **sıra sözleşmesi** |
| Mimir balonu (madde 8) | **14** (B1–B14) | `aria-modal` + `inert` eksikliği → ekran okuyucu iki ekran okur |
| TR/EN aksan | **4** (M-1…M-4) | Sözlük çevirisinde sessiz aksan kaybı |
| **Toplam** | **27 kabul mandalı** | — |

Bunlar **öneri**; PO hangilerini kabul ederse test dosyasına dönüşür. Ben kod yazmam (denetçi), utku'ya brif çıkar.

---

#### 5. Ä°ki alternatif

| | **A — Mandal önce** (önerilen) | **B — Öğreticiyi yaz, mandalı sonra** |
|---|---|---|
| Sıra | 27 mandal testi → öğretici/Balon kodu | Öğretici + balon yazılır, a11y en sonda |
| Artı | Odak tuzağı / `Esc` / `aria-live` gibi sınıflar **koda girmeden** yakalanır; `vitest-axe` zaten kurulu | Görünür ilerleme hızlı |
| Eksi | 1 tur gecikme, görünmez emek | Balon gibi **etkileşimli** bileşende a11y sonradan eklemek en pahalı iş; PO'nun 3 kaçağı bu sınıftandı |
| Risk | Testler UI değişince güncellenir (kabul edilebilir) | "Çalışıyor" denir, ekran okuyucu kullanıcısı kullanamaz |

**Önerim: A.** Gerekçe ölçüm: §2.12'de `aria-busy` 0, `a[href]` 0 çıktı; bu iskelette a11y **niyet** düzeyinde. Etkileşimli bir panel (Mimir) eklenince aynı boşluk **davranışsal** hataya dönüşür (odak kaybı, tuzağa düşmeme).

---

#### 6. Öz-eleştiri (D-382)

- **Bu bölümde yeni ölçüm yapmadım.** 27 mandal **öneri**; hiçbiri koşturulmadı. §2.12'deki 5 viewport ölçümü iskelet içindir — Mimir balonu **henüz kodda yok**, ölçemem. "Ölçtüm" demiyorum, "ölçülecek listeyi verdim" diyorum.
- **B12 (FAB taşma çakışması) hipotez.** A28 (320px taşma) doğrulandı, ama FAB henüz olmadığı için çakışma **öngörü**. Gerçek çakışma ölçülmedi.
- **Aksan listesi elle yazıldı.** 30 kelime, TR sözlüğünün tamamını kapsamıyor; sözlük yazılınca liste **veriden** üretilmeli (`tr` değerlerinde aksansız varyant arama), elle liste değil.
- **`inert` tarayıcı desteğini ölçmedim.** Sürüm bilgilerini (Chrome 102+/Safari 15.5+/Firefox 112+) hafızadan yazdım; caniuse ile doğrulanmadı. Yayın öncesi ölçülmeli.
- **Öğretici katman sayısı 6, mandal 9** — bazı katmanlara 2 mandal verdim, bazılarına 1. Bu dağılım keyfi değil ama tartışılabilir; PO sadeleştirmek isterse 2b ve 4b birleşebilir.

---

#### 7. Dış kaynaklar (belge içinde ilk kez)

| Kaynak | AlÄ±nan kural |
|---|---|
| [WAI-ARIA APG — Dialog (Modal) Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | `role="dialog"` + `aria-modal="true"` + odak tuzağı + `Esc` + kapanınca **tetikleyiciye odak dönüşü**. B2–B4'ün kaynağı |
| [WAI-ARIA APG — Alert Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/alert/) | `aria-live="polite"` + `role="log"` — sohbet akışı için canlı bölge. B6'nın kaynağı |
| [MDN — `inert`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/inert) | Modal açıkken arka planı erişilemez kılar; `aria-hidden` alternatifinden üstün (odak da engellenir) |
| [WCAG 2.2 — SC 2.1.2 No Keyboard Trap](https://www.w3.org/WAI/WCAG22/Understanding/no-keyboard-trap.html) | Odak tuzağı **modal içinde** serbest, ama `Esc` ile **çıkış zorunlu**. B3+B5 birlikte okunmalı |
| [WCAG 2.2 — SC 2.4.3 Focus Order](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html) | Kapanınca odak mantıklı yere döner (tetikleyici düğme). B4'ün kaynağı |

### 4.5 mimir — ihsan notu (mimir adına DEĞİL; 2026-10-21)

**Neden ihsan yazdı:** mimir oturumunda dosya okuma/komut/yazma aracı yok; görüş teslim edemedi ve kanıt uydurmadı (D-253/D-395). PO emri 21.10: "Mimir bölümünü ihsan kendi görüşüyle yazsın, mimir adına değil, 'ihsan notu' olarak". Bu bölüm **mimir görüşü değildir**, bağımsız girdi sayılmaz.

**Dayanak (yeni ölçüm YOK; yalnız belgede zaten geçen kaynaklar):** PO K-b (sağ alt balon, 21.10) · D-410 (Mimir yalnız asistan, salt okunur; KVKK yasu'da) · §3.5 Codex ("kaynak + siz karar verin") · §4.10 madde 8 ihsan · §4.4 madde 8 salih (B1–B14).

| Konu | ihsan notu | Kova |
|---|---|---|
| Yer | Sağ alt yüzen düğme (FAB). Sağ üst önerisi (§4.6) geçersiz, PO K-b ile kapandı | C (PO kararı) |
| Yetki | Salt okunur. Kredi düşürme, radar silme, ödeme YOK. Yalnız o müşterinin (tenant) verisi | C (D-410) |
| İlk açılış | Kısa karşılama + bağlama göre 3 öneri soru (öneriler PO K-b ile geçerli) | C |
| Cevap biçimi | Kaynak/sayfa bağlantısı zorunlu; emin değilse "bilmiyorum, destekle iletişime geç" | C |
| Karar | Mimir öneri verir, "siz karar verin" der (Codex §3.5) | C |
| Erişilebilirlik | salih B1–B14 kapı olarak alınır; en azından odak tuzağı + kapanınca odak tetikleyiciye döner (B4). B12 (FAB taşma çakışması) hipotez, ölçülmedi | A (salih listesi) |
| KVKK | Sorumlu yasu; Mimir tarafÄ±nda log/saklama kararÄ± yasu'ya | C |

**Açık soru (cevabım yok, uydurmuyorum):** Mimir'in kota/paket sorgusu (D-395) hangi katmanda yaşar, yasu API mı utku UI mı? yasu §4.2 aynı soruyu açık bırakmış. Ölçülmedi.

**Öz-eleştiri (D-406):** (1) Bu not kendi §4.10'umun yeniden yazımı; yeni bilgi yok, ikinci göz yok. (2) Mimir'in gerçek model davranışı (gecikme, halüsinasyon, bağlam penceresi) ölçülmedi. (3) Düzeltme yolu: mimir araçlı oturumda gelirse bu bölümü ezmeden altına kendi görüşünü ekler.

### 4.6 ihsan (taslak, kanÄ±tlÄ±)

**Baktığım yer:** `panel-kabuk.tsx` (225 satır), iskelet ekran görüntüsü, `open-design/design-systems/*`.

**Sorun:** (1) sağ üst boş: kredi bakiyesi / arama / Mimir yeri yok. (2) KPI ve tablo "ne işe yarar" demiyor; ilk açılışta müşteri ne yapacağını bilemez (boş durum metni yok). (3) tek ekran masaüstü odaklı; mobil ekran ayrı doğrulanmadı.

**Taslak:**

```
┌ HUGINN ─ sekmeler ───────────── [Ara] [Kredi: veri bağlanacak] [Mimir] ┐
├ yan bar ┬──────────────────────────────────────────────────────────────┤
│         │ Karşılama: "İlk firmanı takibe al" (boş durum, tek CTA)      │
│         │ [KPI][KPI][KPI][KPI]                                         │
│         │ [Sinyal Yoğunluğu ────────][Sektör Dağılımı ───────]         │
│         │ Son Hareketler (boşken: "henüz hareket yok" + yönlendirme)   │
└─────────┴──────────────────────────────────────────────────────────────┘
```

**Alternatifler:**

| | A: sade kurumsal (mevcut yön) | B: yoğun terminal (Bloomberg) |
|---|---|---|
| Artı | Yeni müşteri korkmaz, mobilde rahat | Güçlü kullanıcı hızlı tarar |
| Eksi | Uzman için seyrek | Yeni müşteri bunalır, mobil zor |

Öneri: A zemin, B yoğunluk "yoğun görünüm" anahtarı olarak sonra (Faz sonrası, ölçüm şartlı).

**Öz-eleştiri:** ekran görüntüsüne baktım, canlı tarayıcıda gezmedim; "sağ üst boş" yargısı bir resme dayanıyor. salih ölçmeden kesin sayılmaz.

### 4.7 Codex ajanı — araştırma, ürün deneyimi ve marka sentezi (2026-10-21)

**Kapsam:** Bu bölüm görüş/öneridir; PO onayı olmadan kod kararı değildir.

**Skill beyanÄ±:** `.agents/skills/frontend-design`, `.agents/skills/elite-product-ux-architect`, `.agents/skills/dashboard-layout`, `.agents/skills/frontend-ui-engineering`, `.agents/skills/huginn-mimir-dis`, `.agents/skills/venture-category-architect`, `.agents/skills/better-accessibility`, `.agents/skills/better-layout`, `.agents/skills/better-colors`, `.agents/skills/better-typography`, `.agents/skills/better-ui`, `.agents/skills/better-interface`, `.agents/skills/interface-review`.

#### 1. BaktÄ±ÄÄ±m yer

| Kanıt | Ölçüm | Tasarım sonucu |
|---|---|---|
| `frontend-web/app/panel-tasarim/panel-kabuk.tsx` | Üstte 5 sekme, yanda 3 grup/8 öğe var; öğeler `useState` ile değişiyor, rota değiştirmiyor | İki ayrı birincil gezinme yüzeyi oluşuyor; menü bilgi mimarisi tek ağaca inmeli |
| Aynı dosya | Üst/yan menü öğeleri `<button>`; `Link` yok | Geçerli URL, derin bağlantı, yeni sekmede açma ve geri/ileri gezinme zayıf; navigasyon `<Link>` olmalı |
| `frontend-web/app/panel/page.tsx`, `frontend-web/components/panel/panel-sidebar.tsx` | Gerçek panelde Panel, Radar, RaporLab, UBO Ağı, Cüzdan, Ayarlar var; bazıları `yakında` modalına gider | İskelet IA'sı gerçek IA'dan ayrışıyor; onay sonrası rota sözleşmesi tek dosyada kilitlenmeli |
| `frontend-web/package.json` | `lucide-react`, `recharts`, shadcn/Base UI mevcut | Yeni UI/chart bağımlılığı eklemek gereksiz; mevcut araçlar yeterli |
| `frontend-web/app/panel-tasarim/kabuk.css` | `transform`/`opacity` animasyonları ve `prefers-reduced-motion` koruması mevcut | Mevcut hareket dili korunabilir; canlı güncellemeye duraklatma ve statik anlam eklenmeli |
| İskelet ekranı + `panel-kabuk.tsx` | Grafik placeholder bar yükseklikleri sabit ama farklı (`[38, 62, ...]`) | Rakam yok olsa da sahte trend izlenimi oluşuyor; veri gelene kadar nötr skeleton kullanılmalı |
| `data/orchestrator/MUSTERI-PANEL-TASARIM-01_akis_haritasi.md` / gerçek rota | Akışta `/panel/raporlar`, kodda `/panel/raporlab` var | Rapor rotası ve menü etiketi koddan önce tekleştirilmeli |

#### 2. Sorun / eksik

1. **Menü çoğalıyor:** Üst bar ve yan bar aynı navigasyon işini bölüyor. Müşteri “hangi menü ana menü?” diye düşünmemeli.
2. **Ana ekran karar vermiyor:** İskelet, “hangi fırsat önemli ve şimdi ne yapmalıyım?” sorusuna ilk eylem sunmuyor. KPI/grafik yerleri tek başına değer üretmez.
3. **Kimlik sinyalde değil, renkte kalıyor:** Neon yeşil güçlü ama her aktif/live öğede kullanılırsa önem hiyerarşisi bozulur. İkonlar da Unicode karakterlerle karışık; mevcut `lucide-react` kullanılmalı.

#### 3. TaslaÄÄ±m

##### 3.1 Ürün konumlandırması

| Öğe | Öneri |
|---|---|
| Kategori | Ticari istihbarat / gelir fÄ±rsatÄ± istihbaratÄ± |
| Marka vaadi | Pazar sinyalini karar anÄ±na taÅÄ±r |
| Ana müşteri sorusu | “Kimi aramalıyım, ne değişti, sıradaki hareketim ne?” |
| Ürün karakteri | Sakin, keskin, kaynaklı, güvenli |
| Kaçınılacak algı | Hacker oyunu, neon terminal, veri deposu, gösterişli ama eylemsiz dashboard |
| Ana akış | Keşfet → Takip et → Sinyali yorumla → Raporla / harekete geç |

Dashboard veri deposu değil, karar kokpiti olmalı. İlk ekranın işi: **bugün ne değiştiğini, hangi fırsatın önemli olduğunu ve hangi eylemin önerildiğini** tek bakışta göstermek.

##### 3.2 Önerilen menü ağacı

Tek birincil navigasyon öneriyorum. Üst bar bağlam ve araçlar için kalır; sayfa seçimi yan çekmeceden yapılır.

```text
HUGINN
├─ GENEL BAKIŞ
├─ KEŞFET
│  ├─ Firma Ara
│  └─ Sektör Radarı
├─ TAKİP
│  ├─ Canlı Akış
│  ├─ Sinyaller
│  └─ Takip Listem
├─ ÇIKTI
│  ├─ RaporLab
│  └─ Raporlarım
└─ HESAP
   ├─ Krediler ve Paket
   └─ Ayarlar
```

Üst bar:

```text
[logo] [sayfa yolu / baÄlam]                     [Firma ara] [Kredi] [Mimir] [Profil]
```

- `Genel BakÄ±Å` tek ana giriÅ olsun.
- `Radarlar`, `Sinyaller`, `Canlı Akış` ayrı üst sekmeler olarak tekrarlanmasın; `Takip` altında gruplanmalı.
- `Firmalar` ve `Sektör Radarı` `Keşfet` altında birlikte düşünülmeli.
- `Raporlar` ve `RaporLab` ayrımı müşteri dilinde netleştirilmeli: üretim = `RaporLab`, geçmiş/indirme = `Raporlarım`.
- `Krediler` üst sekme değil; sürekli görünen bakiye göstergesi + `Krediler ve Paket` detay sayfası olmalı.
- Mobilde yan çekmece açılır; ilk erişilebilir dört hedef: `Genel Bakış`, `Keşfet`, `Takip`, `Çıktı`. Hesap çekmecede kalır.
- Menü öğeleri navigasyon ise `<Link>` olmalı; tıklama görünümü değiştiren kontroller buton kalmalı.

##### 3.3 Ana ekran wireframe'i

```text
┌ HUGINN ─ bağlam ───────────────────── [Firma ara] [Kredi] [Mimir] [Profil] ┐
├ çekmece ┬───────────────────────────────────────────────────────────────────┤
│         │ Bugünün resmi                         [Ana eylem]                 │
│ KEŞFET  │ Son güncelleme / veri tazeliği / durum şeridi                     │
│ TAKİP   ├───────────────────────────────────────────────────────────────────┤
│ ÇIKTI   │ Takipteki firmalar | Yeni sinyaller | Açık raporlar | Kredi durumu│
│ HESAP   ├───────────────────────────────────────────────────────────────────┤
│         │ Öncelikli fırsatlar / uyarılar             Son hareketler         │
│         ├───────────────────────────────────────────────────────────────────┤
│         │ Sinyal eğilimi (zaman)                    Sektör sıralaması       │
│         ├───────────────────────────────────────────────────────────────────┤
│         │ Kaynak + tazelik + veri tablosu / boş, yükleniyor, hata durumları  │
└─────────┴───────────────────────────────────────────────────────────────────┘
```

Önerilen sıra:

1. **Bağlam + tek ana eylem:** müşteri yeni ise `İlk firmanı keşfet`; veri varsa `Öncelikli sinyalleri aç`.
2. **Durum Åeridi:** veri tazeliÄi, baÄlantÄ± durumu ve eriÅim bilgisi; renk tek baÅÄ±na anlam taÅÄ±maz.
3. **Dört karar KPI'ı:** her biri kısa açıklama, değişim/trend, son güncelleme ve ilgili sayfaya bağlantı taşır.
4. **Öncelikli fırsatlar:** müşteriyi doğrudan aksiyona götüren liste; dekoratif karttan önce gelir.
5. **Grafikler:** zaman eÄilimi + kategori karÅÄ±laÅtÄ±rmasÄ±; grafik yanÄ±nda kaynak ve eriÅilebilir tablo.
6. **Son hareketler:** olay, firma, kaynak, zaman, sonraki eylem.

##### 3.4 Grafik sözleşmesi

| KullanÄ±cÄ± sorusu | Grafik | Kural |
|---|---|---|
| Sinyal artıyor mu, azalıyor mu? | Çizgi/alan | Zaman ekseni; 7/30/90 gün filtresi; tepe/dip anotasyonu |
| Hangi sektör öncelikli? | Yatay çubuk | Sıralı kategori; ilk sonuçlar görünür; uzun etiketler taşar/kesilmez |
| Hangi firmalar birlikte hareket ediyor? | Ağ/ilişki görünümü | Yalnız ilişki sorusu açıldığında; ana dashboard'a koyulmaz |
| Bir hedef hangi fırsat/risk bölgesinde? | Dağılım grafiği | Eksen adı, birim, kaynak ve açıklama zorunlu |
| Bir bütçe/kredi ne kadar kaldı? | KPI + ilerleme çubuğu | Donut varsayılan değil; yüzde yanında metin ve kalan eylem bulunur |

Grafik ilkeleri:

- `Sektör Dağılımı` için çizgi grafik yanlış anlam üretir; kategori karşılaştırmasında yatay bar kullanılmalı.
- Donut/pie yalnız az sayıda parçanın toplam içindeki payını anlatıyorsa kullanılmalı; küçük dilimler tabloya düşmeli.
- Her grafik başlığı görseli değil ana içgörüyü anlatmalı: `Sinyaller son dönemde nasıl değişti?` gibi.
- Renkler grafikler arasında sabit kalmalı; aynı sektör her grafikte aynı renkte görünmeli.
- Tooltip yalnÄ±z hover'a baÄlÄ± kalmamalÄ±; klavye eriÅimi ve veri tablosu bulunmalÄ±.
- Recharts mevcut; grafik katmanı için yeni paket eklenmemeli.

##### 3.5 Müşteri güveni ve Mimir sınırı

`huginn-mimir-dis` kurallarına göre müşteri yüzü dış dünyadır. Arayüzde:

- Veri her zaman tenant kapsamı ve kaynak/tazelik bilgisiyle gösterilmeli.
- Mimir yalnız salt okunur müşteri yardımcısı olarak görünmeli; admin işlemi, görev, pano veya kilit sözü yüzeye çıkmamalı.
- Firma/risk/eşleştirme yanıtlarında “kaynak” ve “siz karar verin” bağlamı korunmalı.
- Başka tenant verisi, iç anahtar, ham PII ve katalog dışı fiyat görünmemeli.
- Yetki yok, veri yok, eski veri ve hata durumları ayrı metinle anlatılmalı; hepsi “boş” gibi görünmemeli.

##### 3.6 Durum sözleşmesi

| Durum | Görsel | Metin davranışı | Eylem |
|---|---|---|---|
| Yükleniyor | Nihai şekle benzeyen nötr skeleton | Ekran yüksekliği korunur | Eylem yok veya iptal |
| Boş | Basit ikon + neden + değer önerisi | “Henüz takip edilen firma yok” | Tek ana CTA |
| Eski veri | Tazelik etiketi | Son güncelleme açık | Yenile |
| Hata | İkon + kısa neden | Çözüm adımı söyler | Tekrar dene / destek |
| Yetkisiz | Kilit ve açıklama | Veri göstermeden sınır belirtir | Yetki iste / paket bilgisi |
| BaÅarÄ±lÄ± | Veri + kaynak + zaman | Rakam tek baÅÄ±na bÄ±rakÄ±lmaz | Detaya git |

##### 3.7 Marka kiti v0.1

| Alan | Karar |
|---|---|
| Marka fikri | Radar, dosya ve sinyal izini tek sakin çalışma alanında birleştirir |
| Logo kullanÄ±mÄ± | Mevcut `H` iÅareti korunur; yeÅil yalnÄ±z canlÄ±/success aksanÄ± olarak kullanÄ±lÄ±r |
| Ana zemin | `#0D1B2A` — derin lacivert, güven ve odak |
| Panel | `#10233A` — zeminle düşük ama okunabilir ayrım |
| Metin | `#E6EDF3` — ana metin |
| İkincil metin | `#8FA3B8` — yardımcı bilgi |
| Birincil eylem | `#0072FF` — buton, bağlantı, seçili navigasyon |
| Canlı/success | `#00FF66` — canlı bağlantı, olumlu durum, sınırlı vurgu |
| UyarÄ±/hata | AyrÄ± amber/kÄ±rmÄ±zÄ± semantic token; yeÅil-kÄ±rmÄ±zÄ± ayrÄ±mÄ± metin/ikonla desteklenir |
| Tipografi | Mevcut Geist UI için korunur; ID, zaman ve teknik metadata `ui-monospace` + `tabular-nums` kullanır |
| Åekil | Kontrol/kart radius'larÄ± sÄ±nÄ±rlÄ± ve tutarlÄ±; her Åeyi `rounded-2xl` yapma |
| Derinlik | İnce border + az shadow; gölge içerikten güçlü olmamalı |
| İkon | Yüzey genelinde `lucide-react`; Unicode sembol karışımı yok |
| Motion | İlk yüklemede kısa fade-up; skeleton shimmer; etkileşimde kısa opacity/transform; `prefers-reduced-motion` altında hareketsiz/opacity varyantı |
| Ses tonu | “Kaynağı gösterir, kararı sana bırakır.” Kısa, somut, teknik jargonu açıklayan |
| Görsel metafor | İnce radar çizgisi, sinyal düğümü, dosya etiketi; yoğun grid ve dekoratif parazit yok |

Kullanılmayacaklar: mor/indigo varsayılanı, aşırı gradient, sürekli parlayan neon, sahte canlı veri, yalnız renkle durum, animasyonla anlam verme, stok görsel ve gereksiz üçüncü parti font.

##### 3.8 EriÅilebilirlik ve responsive kapÄ±

- Ä°lk focus noktasÄ± `Skip to content`; sticky header focus'u kapatmamalÄ±, scroll padding tanÄ±mlÄ± olmalÄ±.
- Tüm menü/ikon/arama/kredi/Mimir kontrolleri klavye ile erişilebilir ve görünür focus halkasına sahip olmalı.
- Mobil hedefler en az dokunulabilir alanı korumalı; sayfa 320 px ve %200 metin büyütmede yatay kaymamalı.
- Grafikler renk yanÄ±nda baÅlÄ±k, metin, tooltip ve veri tablosu ile anlatÄ±lmalÄ±.
- Canlı akış otomatik güncelleniyorsa duraklatma/yenileme kontrolü bulunmalı.
- 320 / 768 / 1024 / 1440 genişlikleri, klavye, reduced motion ve yüksek kontrast senaryoları kabul kapısı olmalı.

##### 3.9 Uygulama sÄ±rasÄ±

| Faz | Çıktı | Kapı |
|---|---|---|
| 0 | PO: IA + marka kiti A/B kararÄ± | OnaysÄ±z `/panel` deÄiÅmez |
| 1 | Rota sözleşmesi, tek sidebar, token adları, Link tabanlı navigasyon | Mevcut `/panel` rotalarıyla eşleşme |
| 2 | Genel Bakış: durum şeridi, boş durum, dört KPI, ilk CTA | Gerçek API + loading/empty/error |
| 3 | Sinyal eğilimi, sektör barı, hareketler | Kaynak/tazelik + erişilebilir veri tablosu |
| 4 | Mobil çekmece, focus, 320 px, reduced motion | UX-DENET zinciri + ekran kanıtı |
| 5 | Mimir müşteri yüzü ve tenant sınırı | `tenant_id` SQL filtresi + red-team kanıtı |

##### 3.10 Alternatifler

| | A — Karar kokpiti (önerilen) | B — Yoğun terminal görünümü |
|---|---|---|
| Kullanıcı | Yeni ve orta seviye müşteri | Günlük yoğun araştırmacı |
| Yerleşim | Tek sidebar, net CTA, az ama anlamlı grafik | Daha çok tablo, daha sıkı bilgi yoğunluğu |
| Güç | İlk değer ve öğrenilebilirlik yüksek | Hızlı tarama ve uzman verimliliği yüksek |
| Risk | Uzman kullanıcı için seyrek gelebilir | Yeni kullanıcıyı ve mobil deneyimi boğar |
| Karar | Varsayılan | Ölçüm sonrası opsiyonel “yoğun görünüm” |

**Öneri:** A varsayılan olsun. B ancak müşteri davranışı sık filtreleme, kısa oturumda çok kayıt tarama ve masaüstü yoğun kullanım gösterirse eklenmeli.

#### 4. AraÅtÄ±rma dayanaklarÄ±

- [Vercel Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md): semantik navigasyon, görünür focus, reduced motion, URL ile durum, boş/hata durumları.
- [W3C — Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions) ve [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39): gereksiz hareketi kapatma ve `prefers-reduced-motion`.
- [Material Design — responsive navigation](https://m2.material.io/go/design-bottom-navigation/): mobil alt navigasyon, tablet rail, masaüstü drawer geçişi.
- [Carbon — dashboards](https://www.carbondesignsystem.com/building-blocks/data-visualization/dashboards): dashboard hiyerarşisi, metrik sınırı, tutarlı renk, linked charts.
- [Carbon — chart anatomy](https://v10.carbondesignsystem.com/data-visualization/chart-anatomy/): nitelikli başlık, eksen, lejant, tooltip ve veri tablosu.

#### 5. Öz-eleştiri

- Canlı müşteri görüşmesi ve ürün analitiği yok; kategori, menü ve CTA önerileri mevcut kod + ekran + ürün bağlamından türetilmiş hipotezlerdir.
- `/panel-tasarim` ekranı görsel olarak incelendi; bu turda canlı tarayıcı klavye/320 px/ekran okuyucu doğrulaması yapılmadı.
- Renk oranları bu bölümde yeniden ölçülmedi; mevcut iskelet raporundaki ölçümler referans alındı.
- Tasarım yönü kodlanmadı; PO kararı ve UX ekran kanıtı beklenmeli.

### 4.8 bilo — İskeleti geliştirme + yenilik önerisi

> **Skill beyanı (D-383):** `frontend-ui-engineering` (mercek: yükleme/mobil/erişilebilirlik/performans) + `browser-testing-with-devtools` (gerçek tarayıcı ölçümü).
> **Durum:** ÖNERİ — kod değişikliği YOK (PO onayı bekliyor, D-420). Tarih: 2026-10-21.
> **Kapsam kararÄ± (PO 2026-10-21):** Mevcut `docs/brand/` kanonik kalÄ±r ve **v2'ye GENÄ°ÅLETÄ°LÄ°R**; sÄ±fÄ±rdan kit yazÄ±lmaz (D-211).
> **Detay belgesi:** [`MUSTERI_PANEL_BRANDING_V2_ONERI.md`](./MUSTERI_PANEL_BRANDING_V2_ONERI.md)

**1. Baktığım yer (ölçüm, D-382):**

| Kanıt | Ölçüm |
|---|---|
| `frontend-web/app/panel-tasarim/panel-kabuk.tsx` | 224 satÄ±r |
| `frontend-web/app/panel-tasarim/kabuk.css` | 50 satÄ±r (3 keyframe + reduced-motion) |
| `docs/brand/design-tokens.json` | 123 satır — kanonik renk/tipografi SSOT |
| `docs/brand/brand.md:121-135` | renk rolleri (D-44 §3) |
| `docs/brand/prompts/dashboard.md:10-22` | yüzey/grafik/mobil kuralları |
| `frontend-web/package.json` | `recharts ^3.10.1`, `lucide-react ^1.59.0`, `tailwindcss ^4.3.3` KURULU |
| `grep "2563FF\|09111F\|22D3EE\|4F46E5" frontend-web/` | **yalnÄ±z 2 eÅleÅme, ikisi de `app/manifest.ts`** |
| `frontend-web/app/layout.tsx:28` | gövde `bg-gray-50 text-gray-900` (AÇIK tema); kök layout marka token'ı kullanmıyor |

**2. Sorun / eksik (en çok 3):**

1. **İskelet markanın kendi token'larını kullanmıyor.** Uydurma palet: `#0D1B2A` / `#10233A` / `#0072FF` / `#00FF66`. Kanonik: `#09111F` / `#131C2F` / `#2563FF` / `#22D3EE`. `dashboard.md:11,14,18` bunları zaten yazıyor — iskelet üçünü de ihlal ediyor. PWA `manifest.ts:11` `#2563FF` derken panel `#0072FF` gösteriyor → aynı marka gibi görünmüyor.
2. **Kurulu ✅ ✅ â â Ã¢ÂÂ Ã¢ÂÂ kÃÂ¼tÃÂ¼phaneler kullanÃÂ±lmÃÂ±yor.** Grafikler CSS taklit bar (`panel-kabuk.tsx:66-73`), ikonlar emoji (`Ã¢ÂÂÃ¢ÂÂ¡Ã¢ÂÂÃ¢ÂÂ¤Ã¢ÂÂÃ¢ÂÂ¦Ã¢ÂÂÃ¢ÂÂ`, satÃÂ±r 25-42). Oysa `recharts` + `lucide-react` repoda kurulu. SonuÃÂ§: gerÃÂ§ek grafik dili yok; emoji ekran okuyucuda "yÃÂ±ldÃÂ±z iÃÂareti" diye okunur.
3. **Kök layout ile tema çakışıyor.** `layout.tsx:28` açık tema, iskelet koyu kap; `ThemeProvider` var ama iskelet onu kullanmıyor. Font iki yoldan yükleniyor (Inter CDN satır 26 + Geist `next/font` satır 8), kanonik karar Inter primary (`brand.md:148`).

---

#### 4.8.A — MEVCUT İSKELETİ GELİŞTİRME (hemen yapılabilir, düşük risk)

Yapı korunur (menü + 4 KPI + 2 grafik + tablo); yalnız doğru temele oturtulur.

| # | AdÄ±m | KanÄ±t / neden | Emek |
|---|---|---|---|
| A1 | İskelet paletini kanonik token'a çevir | Çakışma tablosu §1; `manifest.ts` zaten kanonik | küçük |
| A2 | Emoji ikonları `lucide-react` ile değiştir | Kütüphane kurulu; a11y (`aria-hidden` / `aria-label`) | küçük |
| A3 | CSS taklit bar → `recharts` (bar + donut) | Kütüphane kurulu; `dashboard.md:17-19` gradyan kuralı | orta |
| A4 | Kök layout: koyu tema + tek font (Inter primary, Geist fallback) | `layout.tsx:26-28`, `brand.md:148` | orta |
| A5 | **Menü çakışmasını çöz:** yan bar tek navigasyon kaynağı, üst bar yalnız global (arama/kredi/Mimir/hesap) | §2.1: 4 kavram iki menüde birden | orta |
| A6 | Boş durum dili + tek birincil CTA | ihsan §4.6 ile aynı bulgu; `panel-kabuk.tsx` metni yok | küçük |
| A7 | Erişilebilirlik: `aria-current`, odak halkası, dokunma ≥44px, grafik `role="img"`+tablo alternatifi | a11y sözleşmesi (kit v2 boşluğu #5) | orta |

**Menü şeması (A5 sonrası):**

```
┌ HUGINN [OSINT] ──────────── [Ara ⌘K] [Kredi] [Mimir] [Avatar] ┐  ← üst bar: SADECE global
├ yan bar ─┬─────────────────────────────────────────────────────┤
│ İZLEME   │ Sayfa başlığı + tek birincil CTA                     │
│ ANALİZ   │ [KPI][KPI][KPI][KPI]                                  │
│ HESAP    │ [Sinyal Yoğunluğu (bar)] [Sektör Dağılımı (donut)]   │
│          │ Son Hareketler (boşken: yönlendirme)                  │
└──────────┴──────────────────────────────────────────────────────┘
```
Üst bar sekmeleri (`Radarlar/Firmalar/Raporlar/Krediler`) yan bardaki karşılıklarına **birleşir** (çift tanım kalkar); `Genel Bakış` logo/ana sayfa olur.

---

#### 4.8.B — YENİLİK ÖNERİLERİ (sonraki faz, ölçüm şartlı)

| # | Fikir | DeÄer | KapÄ± |
|---|---|---|---|
| B1 | **Komut paleti (`⌘K`)** — ara/git/aksiyon | Yoğun kullanıcı menüyü taramaz | A tamamlanınca |
| B2 | **Kişiselleştirilebilir KPI** — kart seç/sırala | Her rol (founder/analyst) kendi görünümü | `docs/brand/personas/*` |
| B3 | **Canlı sinyal akışı** — akan liste + duraklat | "Canlı Akış" menüsünün gerçek karşılığı | gerçek veri bağlanınca |
| B4 | **Sektör karşılaştırma** — firma vs sektör ortalaması | Karar destek; donut/line kombinasyonu | yasu API sözleşmesi |
| B5 | **Gömülü Mimir** — sağ panel asistan (D-410) | Bağlam içi yardım | §4.5 ihsan notu |
| B6 | **Yoğun görünüm anahtarı** — sade ↔ Bloomberg | Her iki kullanıcı tipi | A + B1 sonrası |

---

**3. Ä°ki alternatif (PO kapÄ±sÄ±):**

| | A: sade kurumsal (4.8.A) | B: yoÄun terminal (+4.8.B) |
|---|---|---|
| Menü | yan bar tek kaynak, 3 grup | yan bar + komut paleti |
| Grafik | recharts, kanonik gradyan | yoÄun tablo + sparkline |
| Artı | Yeni müşteri korkmaz, mobil rahat, a11y kolay | Uzman hızlı tarar |
| Eksi | Uzman için seyrek | Yeni müşteri bunalır, mobil zor |

Öneri: **A zemin**, B "yoğun görünüm" anahtarı olarak sonra (ölçüm şartlı).

**4. Kit v2 boşlukları (özet — detay `MUSTERI_PANEL_BRANDING_V2_ONERI.md` §4):** ikonografi kuralı · komponent kütüphanesi · hareket ilkeleri · grafik paleti token'ı · erişilebilirlik sözleşmesi · boş durum dili · ton/ses (microcopy) · logo kullanım matrisi. Hepsi `docs/brand/` **içine** yazılır; ikinci kit açılmaz (D-211).

**5. Öz-eleştiri (D-382):** Bu görüşü **kaynak dosyaları okuyarak** yazdım; **canlı tarayıcıda gezmedim** (mobil/klavye/ekran okuyucu ölçümü YOK). Bu yüzden yargılar "kod okuması"dır, "ölçülmüş" değildir. Gerçek a11y/mobil/performans ölçümü `browser-testing-with-devtools` ile salih + bilo işi. **Ölçtüm mü? Hayır** — yalnız grep/satır sayımı yaptım. Ayrıca `docs/brand` kanonik kitine dokunulması gerekiyor; **D-211 gereği ikinci kit yazmadım**, yalnız çakışmayı raporladım.

**6. §4.7 (Codex ajanı) ile ilişki — ihsan §5 için not:** Codex §4.7 kapsamlı bir IA/güven/durum sözleşmesi sunuyor (tek yan bar, boş/hata/yükleniyor durumları, `<Link>` navigasyonu) — **bunlarla çelişmiyorum, aynı yönü destekliyorum.** İki somut fark:
- **Palet:** Codex §3.7 "Marka kiti v0.1" uydurma paleti (`#0D1B2A`/`#10233A`/`#0072FF`/`#00FF66`) öneriyor — bu **mevcut kanonik kit (`docs/brand/design-tokens.json`) ile çakışır** (kanonik: `#09111F`/`#131C2F`/`#2563FF`/`#22D3EE`) ve PWA `manifest.ts:11` `#2563FF` ile de uyuşmaz. Benim önerim (A1): **kanonik token kullan**, uydurma palet değil. Karar PO'ya.
- **Grafik:** Codex "Sektör Dağılımı için donut varsayılan değil, yatay bar" diyor; ben donut önermiştim. Codex'in gerekçesi (kategori karşılaştırması) benimkinden güçlü → **onun görüşünü kabul ediyorum** (yatay bar).


---

---

---

#### 4.8.C - ÖLÇÜM SONUÇLARI (EK GÖREV - 2026-10-21)

> **Skill beyanı (D-383):** rontend-ui-engineering (mercek: yükleme/mobil/erişilebilirlik/performans) + rowser-testing-with-devtools (gerçek tarayıcı ölçümü).
> **Görev:** EK GÖREV - §4.8'de "ölçmedim" dediklerimi ölçmek (B-1/B-2/B-3).
> **Tarih:** 2026-10-21.
> **Yasaklar:** kod değişikliği YOK (D-420), uydurma rakam yok (D-253/D-395), ölçmediğine "ölçtüm" demek yasak (D-382).

##### B-1 — §4.8.A adımlarının ölçülen değerleri

| Adım | İddia (§4.8.A) | Ölçülen değer | Kanıt | Emek (ölçülmüş) |
|---|---|---|---|---|
| A1 | Palet -> kanonik token | **24 hex satır**, **6 tekil renk** (#0072FF #00FF66 #0D1B2A #10233A #8FA3B8 #E6EDF3) panel-kabuk.tsx'de; kabuk.css'de 0 hex (rgba kullaniyor). Toplam 7 tekil renk (harita-yuvasi.tsx'te #B9C6D4 eklendi). | grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx = 24; kabuk.css = 0 | **küçük** (sed/replace + token import) |
| A2 | Emoji -> lucide-react | **8 emoji ikon** (panel-kabuk.tsx:25-42): ◉⚡★▤◎▦◆⚙. Her biri için lucide karşılığı var: Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings. | emoji_count.py = 8 unique | **küçük** (8 import + 8 JSX) |
| A3 | CSS bar -> recharts | recharts **node_modules 7.8 MB** kurulu; **0 import** (hiçbir dosyada kullanilmıyor). Marjinal bundle maliyeti: tree-shaking ile ~200-400 KB (gzipped ~60-100 KB) tahmini; **ölçülmedi** (next build çıktısı yok). | 
ode_modules/recharts = 7.8 MB; grep recharts = 0 | **orta** (2 grafik bileÅeni + veri baglama) |
| A4 | Kök layout dark + tek font | **2 font aileleri** indiriliyor: Geist (next/font/google, build-time self-host) + Inter (runtime CDN, onts.googleapis.com). Ikisi de latin subset, ikisi de sans-serif. Kanonik karar Inter primary + Geist fallback (rand.md:148) -> çift yükleme. Geist node_modules YOK (next/font/google build-time). | layout.tsx:7-28 + node_modules kontrolü | **orta** (layout.tsx + theme-provider) |

**B-1 özeti:** A1 ve A2 küçük emek (ölçüldü); A3 ve A4 orta emek (A3 bundle boyutu tahmini, next build çıktısı yok).

##### B-2 — A25 kaçak rengini kendi T2 sayımına ekle

| Renk | KullanÄ±m sayÄ±sÄ± | Dosya(lar) | Kontrast (tahmini) | Karar |
|---|---|---|---|---|
| #0072FF | 8 | panel-kabuk.tsx (aksiyon) | - | token'a girer (primary #2563FF ile çakışır -> birleştir) |
| #00FF66 | 6 | panel-kabuk.tsx (vurgu) | - | token'a girer (accent #22D3EE ile çakışır -> birleştir) |
| #0D1B2A | 4 | panel-kabuk.tsx (zemin) | - | token'a girer (dark #09111F ile çakışır -> birleştir) |
| #10233A | 4 | panel-kabuk.tsx (yüzey) | - | token'a girer (darkSecondary #131C2F ile çakışır -> birleştir) |
| #8FA3B8 | 6 | panel-kabuk.tsx + harita-yuvasi.tsx (ikincil metin) | 6.12 (AA geçer) | token'a girer (gray600 #94A3B8 ile çakışır -> birleştir) |
| #E6EDF3 | 6 | panel-kabuk.tsx (ana metin) | - | token'a girer (white #FFFFFF ile çakışır -> birleştir) |
| #B9C6D4 | 4 | harita-yuvasi.tsx (3) + dedektif/page.tsx (1) | 9.14 (AA geçer) | **token'a girer VEYA #8FA3B8'e katlanır** — kontrast farkı 9.14 vs 6.12, ikisi de AA geçer, teknik zorunluluk YOK |

**B-2 sonucu:** 7 tekil renk. 6'sı kanonik token ile çakışıyor (birleştir). #B9C6D4 için teknik zorunluluk yok (kontrast AA geçer); **karar PO'ya** — token'a girer (ikincil metin varyantı) veya #8FA3B8'e katlanır.

##### B-3 — "Yeni bağımlılık eklenmemeli" iddianın doğrulaması

| İddia | Ölçülen değer | Kanıt | Sonuç |
|---|---|---|---|
| recharts kurulu | node_modules 7.8 MB | 
ode_modules/recharts var | Kurulu ✅ ✅ â â Ã¢ÂÂ |
| recharts gerçekten import edilebiliyor mu? | **tsc --noEmit = 0 hata** (test dosyası ile) | pp/recharts_test_page.tsx -> tsc 0 hata | Çalışıyor ✅ ("kurulu" = "çalışıyor" ayrıştırıldı) |
| lucide-react ^1.59.0 ikon adları değişti mi? | **tsc --noEmit = 0 hata** (Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings, Radar, Bolt) | pp/lucide_test_page.tsx -> tsc 0 hata | Adlar kırılmamış ✅ (v1 major'da eski adlar hâlâ mevcut) |
| recharts gerçekten kullaniliyor mu? | **0 import** (hiçbir dosyada) | grep recharts = 0 | Kullanilmıyor — import edilmediği için bundle'a girmir (tree-shaking) |

**B-3 sonucu:** "kurulu" ≠ "çalışıyor" ayrıştırıldı -> ikisi de **çalışıyor** (tsc 0 hata). recharts kullanılmıyor (0 import), bu yüzden bundle'a girmir; import edildiğinde marjinal maliyet ~200-400 KB (tahmini, next build çıktısı yok).

##### B-4 — §4.8.A "emek: küçük/orta" yerine ölçülmüş sayılar

| Adım | Emek (önce) | Emek (ölçülmüş) | Açıklama |
|---|---|---|---|
| A1 | küçük | **küçük** (24 hex satır, 6 tekil renk, 1 dosya) | 24 satır degisimi, token import |
| A2 | küçük | **küçük** (8 emoji -> 8 lucide ikon) | 8 import + 8 JSX degisimi |
| A3 | orta | **orta** (2 grafik bileÅeni + veri baglama) | recharts marjinal ~200-400 KB; next build yok |
| A4 | orta | **orta** (layout.tsx + theme-provider + font) | 2 font -> 1 font; dark tema zorunlu |

**Ölçüm yöntemi (D-382):**
- grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx + kabuk.css
- Python emoji sayacÄ± (unicode range)
- du -sh node_modules/recharts + du -sh node_modules/lucide-react
- 	sc --noEmit test dosyalarÄ±yla (recharts_test_page.tsx, lucide_test_page.tsx)
- grep -r recharts + grep -r lucide-react import sayÄ±sÄ±
- layout.tsx font satÄ±r incelemesi + node_modules kontrol

**Canli tarayici ölçümü YOK:** Lighthouse/axe-core/D-382 dis ölçüm YOK. Bu rapordeki tüm yargilar "kod okumasi + build ciktisi" (tsc --noEmit) düzeyindedir. Gerçek a11y/mobil/performans ölçümü rowser-testing-with-devtools ile salih §2.11-§2.12 + bilo isi.

**Yasaklar uygulandi:** kod değişikliği YOK (D-420), uydurma rakam/etiket YOK (D-253/D-395), ölçmediğine "ölçtüm" demedik (D-382), geçici test dosyaları silindi.

### 4.8b Claude ajanı — ölçülmüş grafik paleti, marka SSOT çatışması, veri-önce iskelet (2026-10-21)

**Kapsam:** görüş/öneri. PO onayı olmadan kod kararı değildir. Codex (§4.7) bilgi mimarisi ve marka diline baktı; ben **ölçülebilir olanı ölçtüm**: palet, grafik formu, SSOT çatışması. Çakışan yerlerde Codex'in bulgusunu tekrarlamıyorum, ölçümle doğruluyorum veya düzeltiyorum.

---

---

---

#### 4.8.C - ÖLÇÜM SONUÇLARI (EK GÖREV - 2026-10-21)

> **Skill beyanı (D-383):** rontend-ui-engineering (mercek: yükleme/mobil/erişilebilirlik/performans) + rowser-testing-with-devtools (gerçek tarayıcı ölçümü).
> **Görev:** EK GÖREV - §4.8'de "ölçmedim" dediklerimi ölçmek (B-1/B-2/B-3).
> **Tarih:** 2026-10-21.
> **Yasaklar:** kod değişikliği YOK (D-420), uydurma rakam yok (D-253/D-395), ölçmediğine "ölçtüm" demek yasak (D-382).

##### B-1 — §4.8.A adımlarının ölçülen değerleri

| Adım | İddia (§4.8.A) | Ölçülen değer | Kanıt | Emek (ölçülmüş) |
|---|---|---|---|---|
| A1 | Palet -> kanonik token | **24 hex satır**, **6 tekil renk** (#0072FF #00FF66 #0D1B2A #10233A #8FA3B8 #E6EDF3) panel-kabuk.tsx'de; kabuk.css'de 0 hex (rgba kullaniyor). Toplam 7 tekil renk (harita-yuvasi.tsx'te #B9C6D4 eklendi). | grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx = 24; kabuk.css = 0 | **küçük** (sed/replace + token import) |
| A2 | Emoji -> lucide-react | **8 emoji ikon** (panel-kabuk.tsx:25-42): ◉⚡★▤◎▦◆⚙. Her biri için lucide karşılığı var: Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings. | emoji_count.py = 8 unique | **küçük** (8 import + 8 JSX) |
| A3 | CSS bar -> recharts | recharts **node_modules 7.8 MB** kurulu; **0 import** (hiçbir dosyada kullanilmıyor). Marjinal bundle maliyeti: tree-shaking ile ~200-400 KB (gzipped ~60-100 KB) tahmini; **ölçülmedi** (next build çıktısı yok). | 
ode_modules/recharts = 7.8 MB; grep recharts = 0 | **orta** (2 grafik bileÅeni + veri baglama) |
| A4 | Kök layout dark + tek font | **2 font aileleri** indiriliyor: Geist (next/font/google, build-time self-host) + Inter (runtime CDN, onts.googleapis.com). Ikisi de latin subset, ikisi de sans-serif. Kanonik karar Inter primary + Geist fallback (rand.md:148) -> çift yükleme. Geist node_modules YOK (next/font/google build-time). | layout.tsx:7-28 + node_modules kontrolü | **orta** (layout.tsx + theme-provider) |

**B-1 özeti:** A1 ve A2 küçük emek (ölçüldü); A3 ve A4 orta emek (A3 bundle boyutu tahmini, next build çıktısı yok).

##### B-2 — A25 kaçak rengini kendi T2 sayımına ekle

| Renk | KullanÄ±m sayÄ±sÄ± | Dosya(lar) | Kontrast (tahmini) | Karar |
|---|---|---|---|---|
| #0072FF | 8 | panel-kabuk.tsx (aksiyon) | - | token'a girer (primary #2563FF ile çakışır -> birleştir) |
| #00FF66 | 6 | panel-kabuk.tsx (vurgu) | - | token'a girer (accent #22D3EE ile çakışır -> birleştir) |
| #0D1B2A | 4 | panel-kabuk.tsx (zemin) | - | token'a girer (dark #09111F ile çakışır -> birleştir) |
| #10233A | 4 | panel-kabuk.tsx (yüzey) | - | token'a girer (darkSecondary #131C2F ile çakışır -> birleştir) |
| #8FA3B8 | 6 | panel-kabuk.tsx + harita-yuvasi.tsx (ikincil metin) | 6.12 (AA geçer) | token'a girer (gray600 #94A3B8 ile çakışır -> birleştir) |
| #E6EDF3 | 6 | panel-kabuk.tsx (ana metin) | - | token'a girer (white #FFFFFF ile çakışır -> birleştir) |
| #B9C6D4 | 4 | harita-yuvasi.tsx (3) + dedektif/page.tsx (1) | 9.14 (AA geçer) | **token'a girer VEYA #8FA3B8'e katlanır** — kontrast farkı 9.14 vs 6.12, ikisi de AA geçer, teknik zorunluluk YOK |

**B-2 sonucu:** 7 tekil renk. 6'sı kanonik token ile çakışıyor (birleştir). #B9C6D4 için teknik zorunluluk yok (kontrast AA geçer); **karar PO'ya** — token'a girer (ikincil metin varyantı) veya #8FA3B8'e katlanır.

##### B-3 — "Yeni bağımlılık eklenmemeli" iddianın doğrulaması

| İddia | Ölçülen değer | Kanıt | Sonuç |
|---|---|---|---|
| recharts kurulu | node_modules 7.8 MB | 
ode_modules/recharts var | Kurulu ✅ ✅ â â Ã¢ÂÂ |
| recharts gerçekten import edilebiliyor mu? | **tsc --noEmit = 0 hata** (test dosyası ile) | pp/recharts_test_page.tsx -> tsc 0 hata | Çalışıyor ✅ ("kurulu" = "çalışıyor" ayrıştırıldı) |
| lucide-react ^1.59.0 ikon adları değişti mi? | **tsc --noEmit = 0 hata** (Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings, Radar, Bolt) | pp/lucide_test_page.tsx -> tsc 0 hata | Adlar kırılmamış ✅ (v1 major'da eski adlar hâlâ mevcut) |
| recharts gerçekten kullaniliyor mu? | **0 import** (hiçbir dosyada) | grep recharts = 0 | Kullanilmıyor — import edilmediği için bundle'a girmir (tree-shaking) |

**B-3 sonucu:** "kurulu" ≠ "çalışıyor" ayrıştırıldı -> ikisi de **çalışıyor** (tsc 0 hata). recharts kullanılmıyor (0 import), bu yüzden bundle'a girmir; import edildiğinde marjinal maliyet ~200-400 KB (tahmini, next build çıktısı yok).

##### B-4 — §4.8.A "emek: küçük/orta" yerine ölçülmüş sayılar

| Adım | Emek (önce) | Emek (ölçülmüş) | Açıklama |
|---|---|---|---|
| A1 | küçük | **küçük** (24 hex satır, 6 tekil renk, 1 dosya) | 24 satır degisimi, token import |
| A2 | küçük | **küçük** (8 emoji -> 8 lucide ikon) | 8 import + 8 JSX degisimi |
| A3 | orta | **orta** (2 grafik bileÅeni + veri baglama) | recharts marjinal ~200-400 KB; next build yok |
| A4 | orta | **orta** (layout.tsx + theme-provider + font) | 2 font -> 1 font; dark tema zorunlu |

**Ölçüm yöntemi (D-382):**
- grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx + kabuk.css
- Python emoji sayacÄ± (unicode range)
- du -sh node_modules/recharts + du -sh node_modules/lucide-react
- 	sc --noEmit test dosyalarÄ±yla (recharts_test_page.tsx, lucide_test_page.tsx)
- grep -r recharts + grep -r lucide-react import sayÄ±sÄ±
- layout.tsx font satÄ±r incelemesi + node_modules kontrol

**Canli tarayici ölçümü YOK:** Lighthouse/axe-core/D-382 dis ölçüm YOK. Bu rapordeki tüm yargilar "kod okumasi + build ciktisi" (tsc --noEmit) düzeyindedir. Gerçek a11y/mobil/performans ölçümü rowser-testing-with-devtools ile salih §2.11-§2.12 + bilo isi.

**Yasaklar uygulandi:** kod değişikliği YOK (D-420), uydurma rakam/etiket YOK (D-253/D-395), ölçmediğine "ölçtüm" demedik (D-382), geçici test dosyaları silindi.

### 4.8b Claude ajanı — ölçülmüş grafik paleti, marka SSOT çatışması, veri-önce iskelet (2026-10-21)

**Kapsam:** görüş/öneri. PO onayı olmadan kod kararı değildir. Codex (§4.7) bilgi mimarisi ve marka diline baktı; ben **ölçülebilir olanı ölçtüm**: palet, grafik formu, SSOT çatışması. Çakışan yerlerde Codex'in bulgusunu tekrarlamıyorum, ölçümle doğruluyorum veya düzeltiyorum.

---

---

---

#### 4.8.C - ÖLÇÜM SONUÇLARI (EK GÖREV - 2026-10-21)

> **Skill beyanı (D-383):** rontend-ui-engineering (mercek: yükleme/mobil/erişilebilirlik/performans) + rowser-testing-with-devtools (gerçek tarayıcı ölçümü).
> **Görev:** EK GÖREV - §4.8'de "ölçmedim" dediklerimi ölçmek (B-1/B-2/B-3).
> **Tarih:** 2026-10-21.
> **Yasaklar:** kod değişikliği YOK (D-420), uydurma rakam yok (D-253/D-395), ölçmediğine "ölçtüm" demek yasak (D-382).

##### B-1 — §4.8.A adımlarının ölçülen değerleri

| Adım | İddia (§4.8.A) | Ölçülen değer | Kanıt | Emek (ölçülmüş) |
|---|---|---|---|---|
| A1 | Palet -> kanonik token | **24 hex satır**, **6 tekil renk** (#0072FF #00FF66 #0D1B2A #10233A #8FA3B8 #E6EDF3) panel-kabuk.tsx'de; kabuk.css'de 0 hex (rgba kullaniyor). Toplam 7 tekil renk (harita-yuvasi.tsx'te #B9C6D4 eklendi). | grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx = 24; kabuk.css = 0 | **küçük** (sed/replace + token import) |
| A2 | Emoji -> lucide-react | **8 emoji ikon** (panel-kabuk.tsx:25-42): ◉⚡★▤◎▦◆⚙. Her biri için lucide karşılığı var: Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings. | emoji_count.py = 8 unique | **küçük** (8 import + 8 JSX) |
| A3 | CSS bar -> recharts | recharts **node_modules 7.8 MB** kurulu; **0 import** (hiçbir dosyada kullanilmıyor). Marjinal bundle maliyeti: tree-shaking ile ~200-400 KB (gzipped ~60-100 KB) tahmini; **ölçülmedi** (next build çıktısı yok). | 
ode_modules/recharts = 7.8 MB; grep recharts = 0 | **orta** (2 grafik bileÅeni + veri baglama) |
| A4 | Kök layout dark + tek font | **2 font aileleri** indiriliyor: Geist (next/font/google, build-time self-host) + Inter (runtime CDN, onts.googleapis.com). Ikisi de latin subset, ikisi de sans-serif. Kanonik karar Inter primary + Geist fallback (rand.md:148) -> çift yükleme. Geist node_modules YOK (next/font/google build-time). | layout.tsx:7-28 + node_modules kontrolü | **orta** (layout.tsx + theme-provider) |

**B-1 özeti:** A1 ve A2 küçük emek (ölçüldü); A3 ve A4 orta emek (A3 bundle boyutu tahmini, next build çıktısı yok).

##### B-2 — A25 kaçak rengini kendi T2 sayımına ekle

| Renk | KullanÄ±m sayÄ±sÄ± | Dosya(lar) | Kontrast (tahmini) | Karar |
|---|---|---|---|---|
| #0072FF | 8 | panel-kabuk.tsx (aksiyon) | - | token'a girer (primary #2563FF ile çakışır -> birleştir) |
| #00FF66 | 6 | panel-kabuk.tsx (vurgu) | - | token'a girer (accent #22D3EE ile çakışır -> birleştir) |
| #0D1B2A | 4 | panel-kabuk.tsx (zemin) | - | token'a girer (dark #09111F ile çakışır -> birleştir) |
| #10233A | 4 | panel-kabuk.tsx (yüzey) | - | token'a girer (darkSecondary #131C2F ile çakışır -> birleştir) |
| #8FA3B8 | 6 | panel-kabuk.tsx + harita-yuvasi.tsx (ikincil metin) | 6.12 (AA geçer) | token'a girer (gray600 #94A3B8 ile çakışır -> birleştir) |
| #E6EDF3 | 6 | panel-kabuk.tsx (ana metin) | - | token'a girer (white #FFFFFF ile çakışır -> birleştir) |
| #B9C6D4 | 4 | harita-yuvasi.tsx (3) + dedektif/page.tsx (1) | 9.14 (AA geçer) | **token'a girer VEYA #8FA3B8'e katlanır** — kontrast farkı 9.14 vs 6.12, ikisi de AA geçer, teknik zorunluluk YOK |

**B-2 sonucu:** 7 tekil renk. 6'sı kanonik token ile çakışıyor (birleştir). #B9C6D4 için teknik zorunluluk yok (kontrast AA geçer); **karar PO'ya** — token'a girer (ikincil metin varyantı) veya #8FA3B8'e katlanır.

##### B-3 — "Yeni bağımlılık eklenmemeli" iddianın doğrulaması

| İddia | Ölçülen değer | Kanıt | Sonuç |
|---|---|---|---|
| recharts kurulu | node_modules 7.8 MB | 
ode_modules/recharts var | Kurulu ✅ ✅ â â Ã¢ÂÂ |
| recharts gerçekten import edilebiliyor mu? | **tsc --noEmit = 0 hata** (test dosyası ile) | pp/recharts_test_page.tsx -> tsc 0 hata | Çalışıyor ✅ ("kurulu" = "çalışıyor" ayrıştırıldı) |
| lucide-react ^1.59.0 ikon adları değişti mi? | **tsc --noEmit = 0 hata** (Activity, Zap, Star, Building2, Target, FileText, CreditCard, Settings, Radar, Bolt) | pp/lucide_test_page.tsx -> tsc 0 hata | Adlar kırılmamış ✅ (v1 major'da eski adlar hâlâ mevcut) |
| recharts gerçekten kullaniliyor mu? | **0 import** (hiçbir dosyada) | grep recharts = 0 | Kullanilmıyor — import edilmediği için bundle'a girmir (tree-shaking) |

**B-3 sonucu:** "kurulu" ≠ "çalışıyor" ayrıştırıldı -> ikisi de **çalışıyor** (tsc 0 hata). recharts kullanılmıyor (0 import), bu yüzden bundle'a girmir; import edildiğinde marjinal maliyet ~200-400 KB (tahmini, next build çıktısı yok).

##### B-4 — §4.8.A "emek: küçük/orta" yerine ölçülmüş sayılar

| Adım | Emek (önce) | Emek (ölçülmüş) | Açıklama |
|---|---|---|---|
| A1 | küçük | **küçük** (24 hex satır, 6 tekil renk, 1 dosya) | 24 satır degisimi, token import |
| A2 | küçük | **küçük** (8 emoji -> 8 lucide ikon) | 8 import + 8 JSX degisimi |
| A3 | orta | **orta** (2 grafik bileÅeni + veri baglama) | recharts marjinal ~200-400 KB; next build yok |
| A4 | orta | **orta** (layout.tsx + theme-provider + font) | 2 font -> 1 font; dark tema zorunlu |

**Ölçüm yöntemi (D-382):**
- grep '#[0-9A-Fa-f]{3,8}' panel-kabuk.tsx + kabuk.css
- Python emoji sayacÄ± (unicode range)
- du -sh node_modules/recharts + du -sh node_modules/lucide-react
- 	sc --noEmit test dosyalarÄ±yla (recharts_test_page.tsx, lucide_test_page.tsx)
- grep -r recharts + grep -r lucide-react import sayÄ±sÄ±
- layout.tsx font satÄ±r incelemesi + node_modules kontrol

**Canli tarayici ölçümü YOK:** Lighthouse/axe-core/D-382 dis ölçüm YOK. Bu rapordeki tüm yargilar "kod okumasi + build ciktisi" (tsc --noEmit) düzeyindedir. Gerçek a11y/mobil/performans ölçümü rowser-testing-with-devtools ile salih §2.11-§2.12 + bilo isi.

**Yasaklar uygulandi:** kod değişikliği YOK (D-420), uydurma rakam/etiket YOK (D-253/D-395), ölçmediğine "ölçtüm" demedik (D-382), geçici test dosyaları silindi.

### 4.8b Claude ajanı — ölçülmüş grafik paleti, marka SSOT çatışması, veri-önce iskelet (2026-10-21)

**Kapsam:** görüş/öneri. PO onayı olmadan kod kararı değildir. Codex (§4.7) bilgi mimarisi ve marka diline baktı; ben **ölçülebilir olanı ölçtüm**: palet, grafik formu, SSOT çatışması. Çakışan yerlerde Codex'in bulgusunu tekrarlamıyorum, ölçümle doğruluyorum veya düzeltiyorum.

**Skill beyanı (D-401):** `dataviz` (bundled skill; `references/palette.md`, `references/color-formula.md`, `scripts/validate_palette.js` okundu/koşturuldu) + `superpowers:using-superpowers`. `frontend-design` kasıtlı **kullanılmadı** — utku ve Codex o merceği zaten uyguladı; aynı skill ile aynı sonuca varmak görüş toplama defterinde değer üretmez (PO talebi: "herkes aynı skillerle yorumlamasın").

#### 1. Baktığım yer (ölçüm, 2 kanıttan fazla)

| Kanıt | Ölçüm (komut/dosya:satır) | Sonuç |
|---|---|---|
| `docs/brand/design-tokens.json:53-73` vs `panel-kabuk.tsx:89,94,129` | Marka SSOT primary `#2563FF`, zemin `#09111F`, kart `#131C2F`; iskelet `#0072FF`, `#0D1B2A`, `#10233A`, `#00FF66` | **SSOT çatışması:** iki palet var, ikisi de "panel" diyor. Karar kapısı §4.8/2'de |
| `docs/brand/ai-rules.md:22-28` | "Position as Startup Intelligence Platform, **not** OSINT Tool"; yasak sözcükler: Surveillance, Dark web, Hacker | `panel-kabuk.tsx:99` üst barda **`OSINT` rozeti** var; brif başlığı "OSINT temalı". Marka kuralıyla doğrudan çelişir |
| `docs/brand/design-tokens.json:47-51` (D-45 scope notu) | SSOT yalnız 2 kapsam tanımlıyor: `marketing` ve `productUI` (= Streamlit `tokens.py`, Indigo). **frontend-web paneli hiçbirinde yok** | Müşteri paneli için 3. kapsam (`customerPanel`) tanımlanmalı; aksi halde her görev kendi rengini uydurur |
| `validate_palette.js "#00FF66,#0072FF" --mode dark --surface "#10233A"` | **FAIL** — Lightness band: `#00FF66` L=0.872, 0.48–0.67 bandı dışında | `#00FF66` seri/grafik rengi olamaz. Yalnız nokta-aksan (canlı rozeti) olarak kalabilir |
| `validate_palette.js "#2563FF,#22D3EE,#4F46E5,#eda100,#e87ba4,#1baf7a" --mode dark --surface "#131C2F"` (marka renkleri doğrudan seri olarak) | **FAIL** — L bandı 3 ihlal; CVD WARN ΔE 6.1 (deutan, `#1baf7a↔#e87ba4`); `#4F46E5` kontrast 2.7:1 (<3:1) | Marka paleti **doğrudan grafik serisine dökülemez**. Grafik için ayrı adımlanmış set gerekir |
| `validate_palette.js "#2563FF,#d95926,#199e70,#c98500,#d55181,#9085e9" --mode dark --surface "#131C2F"` | **ALL CHECKS PASS** — 5/5; en kötü komşu CVD ΔE 8.4 (protan), normal görüş ΔE 19.3, tüm slotlar ≥3:1 | **Önerilen 6 slotluk grafik paleti.** Slot 1 marka primary'si; kalan 5 adımlanmış |
| `validate_palette.js "#2563FF,#d95926,#199e70" --pairs all` | **PASS** — tüm-çift CVD ΔE 9.4 | Dağılım/bubble/küçük-çoklu grafiklerde **seri üst sınırı 3**; 4+ seri → "Diğer" veya facet |
| `validate_palette.js "#cde2fb,#86b6ef,#3987e5,#256abf,#184f95" --ordinal` | **PASS** — tek hue, monoton L, açık uç 2.10:1 | Sıralı/ordinal (ısı haritası, kademe, funnel) için mavi rampa hazır |
| `validate_palette.js "#0ca30c,#fab219,#ec835a,#d03b3b"` (standart durum paleti) | **FAIL** — normal görüş ΔE 13.6 (`#ec835a↔#fab219`, 15 tabanı altında) | 4 kademe durum rengi bu haliyle olmaz. `serious`→`#e8743c` ile **PASS** (ΔE 11.2 deutan) |
| `panel-kabuk.tsx:66` | Bar placeholder yükseklikleri `[38, 62, 46, 78, 55, 88, 64, 72]` — sabit ama **farklı** | Rakam yok ama **sahte trend** var: göz "yükseliyor" okur. D-253/D-395 ruhu ihlal; nötr skeleton olmalı (Codex §4.7/1 ile aynı bulgu, bağımsız teyit) |
| `panel-kabuk.tsx:196` | `Sektör Dağılımı` grafiği `tip="line"` | Kategori verisi zaman eksenine çizilmiş. Form hatası; yatay bar olmalı (Codex §3.4 ile aynı; `dataviz/choosing-a-form` teyit eder) |
| `panel-kabuk.tsx:25-43` | İkonlar Unicode: `◉ ⚡ ★ ▤ ◎ ▦ ◆ ⚙` | `lucide-react` kurulu (`package.json:12`), gerçek panel onu kullanıyor (`panel-sidebar.tsx:6-13`). Unicode ikon fontlar arası kayar, ekran okuyucuda sesli okunur |

#### 2. Sorun / eksik (3 madde, en aÄÄ±rdan)

1. **Marka SSOT'u panel için TANIMSIZ — en ağır risk.** `design-tokens.json` kendi kapsamını `marketing` + `productUI (Streamlit/Indigo)` diye kilitlemiş (D-45: "iki palet birleştirilmez"). `frontend-web` müşteri paneli üçüncü bir yüzey ve **hiçbir SSOT'a bağlı değil**. Bu yüzden iskelet kendi paletini uydurdu (`#0D1B2A`/`#00FF66`), marka ise `#09111F`/`#2563FF` diyor. Palet kararı verilmeden iskelet dolgusuna geçilirse her görev farklı renk getirir.
2. **"OSINT" kimliği marka kuralını ihlal ediyor.** Brif "kurumsal OSINT tarzı" istedi, iskelet üst bara `OSINT` rozeti koydu (`panel-kabuk.tsx:99`). `ai-rules.md:22-28` bunu açıkça yasaklıyor ("not OSINT Tool"). Müşteri yüzünde görünen rozet, satış konumlandırmasını kendi kuralımıza karşı çeviriyor. PO kararı gerekir: ya kural değişir ya rozet gider.
3. **Grafik paleti ölçülmemişti.** Mevcut vurgu renkleri (`#00FF66`, `#0072FF`) KPI aksanı olarak çalışır ama seri rengi olarak ölçümü geçmiyor; marka renkleri de doğrudan geçmiyor (ikisi de yukarıda FAIL). Grafik katmanı için **ayrı, ölçülmüş** bir slot sırası gerekir — yoksa dolgu fazında renk körlüğü/kontrast sorunu kod içine gömülür ve sökülmesi pahalı olur.

#### 3. Taslağım — ölçülmüş grafik sözleşmesi (`panel.viz` token seti)

Codex §3.7 marka kitini sözel tanımladı; ben **grafik katmanının sayılarını** veriyorum. İkisi çakışmaz: marka = yüzey/metin/eylem, bu tablo = veri mürekkebi.

**VIZ-1 Kategorik seri sırası (sabit sıra, asla döngü yok)**

| Slot | Hue | Dark (`#131C2F` üstü) | Light (`#F8FAFC` üstü) | Not |
|---|---|---|---|---|
**Skill beyanı (D-401):** `dataviz` (bundled skill; `references/palette.md`, `references/color-formula.md`, `scripts/validate_palette.js` okundu/koşturuldu) + `superpowers:using-superpowers`. `frontend-design` kasıtlı **kullanılmadı** — utku ve Codex o merceği zaten uyguladı; aynı skill ile aynı sonuca varmak görüş toplama defterinde değer üretmez (PO talebi: "herkes aynı skillerle yorumlamasın").

#### 1. Baktığım yer (ölçüm, 2 kanıttan fazla)

| Kanıt | Ölçüm (komut/dosya:satır) | Sonuç |
|---|---|---|
| `docs/brand/design-tokens.json:53-73` vs `panel-kabuk.tsx:89,94,129` | Marka SSOT primary `#2563FF`, zemin `#09111F`, kart `#131C2F`; iskelet `#0072FF`, `#0D1B2A`, `#10233A`, `#00FF66` | **SSOT çatışması:** iki palet var, ikisi de "panel" diyor. Karar kapısı §4.8/2'de |
| `docs/brand/ai-rules.md:22-28` | "Position as Startup Intelligence Platform, **not** OSINT Tool"; yasak sözcükler: Surveillance, Dark web, Hacker | `panel-kabuk.tsx:99` üst barda **`OSINT` rozeti** var; brif başlığı "OSINT temalı". Marka kuralıyla doğrudan çelişir |
| `docs/brand/design-tokens.json:47-51` (D-45 scope notu) | SSOT yalnız 2 kapsam tanımlıyor: `marketing` ve `productUI` (= Streamlit `tokens.py`, Indigo). **frontend-web paneli hiçbirinde yok** | Müşteri paneli için 3. kapsam (`customerPanel`) tanımlanmalı; aksi halde her görev kendi rengini uydurur |
| `validate_palette.js "#00FF66,#0072FF" --mode dark --surface "#10233A"` | **FAIL** — Lightness band: `#00FF66` L=0.872, 0.48–0.67 bandı dışında | `#00FF66` seri/grafik rengi olamaz. Yalnız nokta-aksan (canlı rozeti) olarak kalabilir |
| `validate_palette.js "#2563FF,#22D3EE,#4F46E5,#eda100,#e87ba4,#1baf7a" --mode dark --surface "#131C2F"` (marka renkleri doğrudan seri olarak) | **FAIL** — L bandı 3 ihlal; CVD WARN ΔE 6.1 (deutan, `#1baf7a↔#e87ba4`); `#4F46E5` kontrast 2.7:1 (<3:1) | Marka paleti **doğrudan grafik serisine dökülemez**. Grafik için ayrı adımlanmış set gerekir |
| `validate_palette.js "#2563FF,#d95926,#199e70,#c98500,#d55181,#9085e9" --mode dark --surface "#131C2F"` | **ALL CHECKS PASS** — 5/5; en kötü komşu CVD ΔE 8.4 (protan), normal görüş ΔE 19.3, tüm slotlar ≥3:1 | **Önerilen 6 slotluk grafik paleti.** Slot 1 marka primary'si; kalan 5 adımlanmış |
| `validate_palette.js "#2563FF,#d95926,#199e70" --pairs all` | **PASS** — tüm-çift CVD ΔE 9.4 | Dağılım/bubble/küçük-çoklu grafiklerde **seri üst sınırı 3**; 4+ seri → "Diğer" veya facet |
| `validate_palette.js "#cde2fb,#86b6ef,#3987e5,#256abf,#184f95" --ordinal` | **PASS** — tek hue, monoton L, açık uç 2.10:1 | Sıralı/ordinal (ısı haritası, kademe, funnel) için mavi rampa hazır |
| `validate_palette.js "#0ca30c,#fab219,#ec835a,#d03b3b"` (standart durum paleti) | **FAIL** — normal görüş ΔE 13.6 (`#ec835a↔#fab219`, 15 tabanı altında) | 4 kademe durum rengi bu haliyle olmaz. `serious`→`#e8743c` ile **PASS** (ΔE 11.2 deutan) |
| `panel-kabuk.tsx:66` | Bar placeholder yükseklikleri `[38, 62, 46, 78, 55, 88, 64, 72]` — sabit ama **farklı** | Rakam yok ama **sahte trend** var: göz "yükseliyor" okur. D-253/D-395 ruhu ihlal; nötr skeleton olmalı (Codex §4.7/1 ile aynı bulgu, bağımsız teyit) |
| `panel-kabuk.tsx:196` | `Sektör Dağılımı` grafiği `tip="line"` | Kategori verisi zaman eksenine çizilmiş. Form hatası; yatay bar olmalı (Codex §3.4 ile aynı; `dataviz/choosing-a-form` teyit eder) |
| `panel-kabuk.tsx:25-43` | İkonlar Unicode: `◉ ⚡ ★ ▤ ◎ ▦ ◆ ⚙` | `lucide-react` kurulu (`package.json:12`), gerçek panel onu kullanıyor (`panel-sidebar.tsx:6-13`). Unicode ikon fontlar arası kayar, ekran okuyucuda sesli okunur |

#### 2. Sorun / eksik (3 madde, en aÄÄ±rdan)

1. **Marka SSOT'u panel için TANIMSIZ — en ağır risk.** `design-tokens.json` kendi kapsamını `marketing` + `productUI (Streamlit/Indigo)` diye kilitlemiş (D-45: "iki palet birleştirilmez"). `frontend-web` müşteri paneli üçüncü bir yüzey ve **hiçbir SSOT'a bağlı değil**. Bu yüzden iskelet kendi paletini uydurdu (`#0D1B2A`/`#00FF66`), marka ise `#09111F`/`#2563FF` diyor. Palet kararı verilmeden iskelet dolgusuna geçilirse her görev farklı renk getirir.
2. **"OSINT" kimliği marka kuralını ihlal ediyor.** Brif "kurumsal OSINT tarzı" istedi, iskelet üst bara `OSINT` rozeti koydu (`panel-kabuk.tsx:99`). `ai-rules.md:22-28` bunu açıkça yasaklıyor ("not OSINT Tool"). Müşteri yüzünde görünen rozet, satış konumlandırmasını kendi kuralımıza karşı çeviriyor. PO kararı gerekir: ya kural değişir ya rozet gider.
3. **Grafik paleti ölçülmemişti.** Mevcut vurgu renkleri (`#00FF66`, `#0072FF`) KPI aksanı olarak çalışır ama seri rengi olarak ölçümü geçmiyor; marka renkleri de doğrudan geçmiyor (ikisi de yukarıda FAIL). Grafik katmanı için **ayrı, ölçülmüş** bir slot sırası gerekir — yoksa dolgu fazında renk körlüğü/kontrast sorunu kod içine gömülür ve sökülmesi pahalı olur.

#### 3. Taslağım — ölçülmüş grafik sözleşmesi (`panel.viz` token seti)

Codex §3.7 marka kitini sözel tanımladı; ben **grafik katmanının sayılarını** veriyorum. İkisi çakışmaz: marka = yüzey/metin/eylem, bu tablo = veri mürekkebi.

**VIZ-1 Kategorik seri sırası (sabit sıra, asla döngü yok)**

| Slot | Hue | Dark (`#131C2F` üstü) | Light (`#F8FAFC` üstü) | Not |
|---|---|---|---|---|
**Skill beyanı (D-401):** `dataviz` (bundled skill; `references/palette.md`, `references/color-formula.md`, `scripts/validate_palette.js` okundu/koşturuldu) + `superpowers:using-superpowers`. `frontend-design` kasıtlı **kullanılmadı** — utku ve Codex o merceği zaten uyguladı; aynı skill ile aynı sonuca varmak görüş toplama defterinde değer üretmez (PO talebi: "herkes aynı skillerle yorumlamasın").

#### 1. Baktığım yer (ölçüm, 2 kanıttan fazla)

| Kanıt | Ölçüm (komut/dosya:satır) | Sonuç |
|---|---|---|
| `docs/brand/design-tokens.json:53-73` vs `panel-kabuk.tsx:89,94,129` | Marka SSOT primary `#2563FF`, zemin `#09111F`, kart `#131C2F`; iskelet `#0072FF`, `#0D1B2A`, `#10233A`, `#00FF66` | **SSOT çatışması:** iki palet var, ikisi de "panel" diyor. Karar kapısı §4.8/2'de |
| `docs/brand/ai-rules.md:22-28` | "Position as Startup Intelligence Platform, **not** OSINT Tool"; yasak sözcükler: Surveillance, Dark web, Hacker | `panel-kabuk.tsx:99` üst barda **`OSINT` rozeti** var; brif başlığı "OSINT temalı". Marka kuralıyla doğrudan çelişir |
| `docs/brand/design-tokens.json:47-51` (D-45 scope notu) | SSOT yalnız 2 kapsam tanımlıyor: `marketing` ve `productUI` (= Streamlit `tokens.py`, Indigo). **frontend-web paneli hiçbirinde yok** | Müşteri paneli için 3. kapsam (`customerPanel`) tanımlanmalı; aksi halde her görev kendi rengini uydurur |
| `validate_palette.js "#00FF66,#0072FF" --mode dark --surface "#10233A"` | **FAIL** — Lightness band: `#00FF66` L=0.872, 0.48–0.67 bandı dışında | `#00FF66` seri/grafik rengi olamaz. Yalnız nokta-aksan (canlı rozeti) olarak kalabilir |
| `validate_palette.js "#2563FF,#22D3EE,#4F46E5,#eda100,#e87ba4,#1baf7a" --mode dark --surface "#131C2F"` (marka renkleri doğrudan seri olarak) | **FAIL** — L bandı 3 ihlal; CVD WARN ΔE 6.1 (deutan, `#1baf7a↔#e87ba4`); `#4F46E5` kontrast 2.7:1 (<3:1) | Marka paleti **doğrudan grafik serisine dökülemez**. Grafik için ayrı adımlanmış set gerekir |
| `validate_palette.js "#2563FF,#d95926,#199e70,#c98500,#d55181,#9085e9" --mode dark --surface "#131C2F"` | **ALL CHECKS PASS** — 5/5; en kötü komşu CVD ΔE 8.4 (protan), normal görüş ΔE 19.3, tüm slotlar ≥3:1 | **Önerilen 6 slotluk grafik paleti.** Slot 1 marka primary'si; kalan 5 adımlanmış |
| `validate_palette.js "#2563FF,#d95926,#199e70" --pairs all` | **PASS** — tüm-çift CVD ΔE 9.4 | Dağılım/bubble/küçük-çoklu grafiklerde **seri üst sınırı 3**; 4+ seri → "Diğer" veya facet |
| `validate_palette.js "#cde2fb,#86b6ef,#3987e5,#256abf,#184f95" --ordinal` | **PASS** — tek hue, monoton L, açık uç 2.10:1 | Sıralı/ordinal (ısı haritası, kademe, funnel) için mavi rampa hazır |
| `validate_palette.js "#0ca30c,#fab219,#ec835a,#d03b3b"` (standart durum paleti) | **FAIL** — normal görüş ΔE 13.6 (`#ec835a↔#fab219`, 15 tabanı altında) | 4 kademe durum rengi bu haliyle olmaz. `serious`→`#e8743c` ile **PASS** (ΔE 11.2 deutan) |
| `panel-kabuk.tsx:66` | Bar placeholder yükseklikleri `[38, 62, 46, 78, 55, 88, 64, 72]` — sabit ama **farklı** | Rakam yok ama **sahte trend** var: göz "yükseliyor" okur. D-253/D-395 ruhu ihlal; nötr skeleton olmalı (Codex §4.7/1 ile aynı bulgu, bağımsız teyit) |
| `panel-kabuk.tsx:196` | `Sektör Dağılımı` grafiği `tip="line"` | Kategori verisi zaman eksenine çizilmiş. Form hatası; yatay bar olmalı (Codex §3.4 ile aynı; `dataviz/choosing-a-form` teyit eder) |
| `panel-kabuk.tsx:25-43` | İkonlar Unicode: `◉ ⚡ ★ ▤ ◎ ▦ ◆ ⚙` | `lucide-react` kurulu (`package.json:12`), gerçek panel onu kullanıyor (`panel-sidebar.tsx:6-13`). Unicode ikon fontlar arası kayar, ekran okuyucuda sesli okunur |

#### 2. Sorun / eksik (3 madde, en aÄÄ±rdan)

1. **Marka SSOT'u panel için TANIMSIZ — en ağır risk.** `design-tokens.json` kendi kapsamını `marketing` + `productUI (Streamlit/Indigo)` diye kilitlemiş (D-45: "iki palet birleştirilmez"). `frontend-web` müşteri paneli üçüncü bir yüzey ve **hiçbir SSOT'a bağlı değil**. Bu yüzden iskelet kendi paletini uydurdu (`#0D1B2A`/`#00FF66`), marka ise `#09111F`/`#2563FF` diyor. Palet kararı verilmeden iskelet dolgusuna geçilirse her görev farklı renk getirir.
2. **"OSINT" kimliği marka kuralını ihlal ediyor.** Brif "kurumsal OSINT tarzı" istedi, iskelet üst bara `OSINT` rozeti koydu (`panel-kabuk.tsx:99`). `ai-rules.md:22-28` bunu açıkça yasaklıyor ("not OSINT Tool"). Müşteri yüzünde görünen rozet, satış konumlandırmasını kendi kuralımıza karşı çeviriyor. PO kararı gerekir: ya kural değişir ya rozet gider.
3. **Grafik paleti ölçülmemişti.** Mevcut vurgu renkleri (`#00FF66`, `#0072FF`) KPI aksanı olarak çalışır ama seri rengi olarak ölçümü geçmiyor; marka renkleri de doğrudan geçmiyor (ikisi de yukarıda FAIL). Grafik katmanı için **ayrı, ölçülmüş** bir slot sırası gerekir — yoksa dolgu fazında renk körlüğü/kontrast sorunu kod içine gömülür ve sökülmesi pahalı olur.

#### 3. Taslağım — ölçülmüş grafik sözleşmesi (`panel.viz` token seti)

Codex §3.7 marka kitini sözel tanımladı; ben **grafik katmanının sayılarını** veriyorum. İkisi çakışmaz: marka = yüzey/metin/eylem, bu tablo = veri mürekkebi.

**VIZ-1 Kategorik seri sırası (sabit sıra, asla döngü yok)**

| Slot | Hue | Dark (`#131C2F` üstü) | Light (`#F8FAFC` üstü) | Not |
|---|---|---|---|---|
| 1 | mavi | `#2563FF` | `#2563FF` | marka primary — birinci seri daima marka rengi |
| 2 | turuncu | `#d95926` | `#eb6834` | |
| 3 | yeşil-deniz | `#199e70` | `#1baf7a` | light'ta <3:1 → etiket/tablo zorunlu |
| 4 | amber | `#c98500` | `#eda100` | light'ta <3:1 → etiket/tablo zorunlu |
| 5 | magenta | `#d55181` | `#e87ba4` | light'ta <3:1 → etiket/tablo zorunlu |
| 6 | mor | `#9085e9` | `#6250d6` | |

Dark seti **5/5 kontrolü geçti** (komut yukarıda). 7. seri **yeni renk üretmez** → "Diğer"e katlanır veya küçük-çoklu'ya ayrılır.

**VIZ-2 Sert sınırlar (ölçümden çıkan, tartışmaya kapalı)**

| Kural | Ölçüm dayanağı |
|---|---|
| Dağılım/bubble/harita/küçük-çoklu → **en çok 3 seri** | `--pairs all` 3 slotta PASS, 4. slotta amber↔turuncu çifti tabanın altına düşer |
| `#00FF66` grafikte **seri rengi olamaz** | L=0.872, band 0.48–0.67 dışı (FAIL) |
| Light modda slot 3/4/5 kullanılırsa **doğrudan etiket veya veri tablosu zorunlu** | kontrast 2.69 / 2.07 / 2.57 (<3:1 → relief kuralı) |
| **Çift eksen (iki y-skalası) yasak** | `dataviz` 1 numaralı anti-pattern; iki ölçek → iki grafik veya ortak tabana indeksleme |
| Sıralı (magnitude) = **tek hue açık→koyu**; ıraksak = **iki hue + nötr gri orta** | rainbow ve ortada renkli hue yasak |
| Renk **varlÄ±ÄÄ±** izler, sÄ±rasÄ±nÄ± deÄil | filtre seri sayÄ±sÄ±nÄ± deÄiÅtirince kalanlar yeniden boyanmaz |
| Durum rengi seri rengi olarak **asla** yeniden kullanÄ±lmaz | status paleti ayrÄ± ve ikon+etiketle gelir |

**VIZ-3 SÄ±ralÄ± rampa (Ä±sÄ± haritasÄ±, kademe, funnel)**

Tek hue mavi, `100→650`: `#cde2fb · #86b6ef · #3987e5 · #256abf · #184f95` — ordinal kontrolünden PASS. Dark modda **`#184f95`'ten koyuya gitme** (2.15:1 tabanı). İkinci eş zamanlı sıralı bağlam gerekirse slot 2'nin hue'su (turuncu) kendi tek-hue rampası olur.

**VIZ-4 Durum paleti (sabit, temalanmaz) — ÖLÇÜM DÜZELTMESİ**

| Rol | Hex | Not |
|---|---|---|
| iyi | `#0ca30c` | |
| uyarÄ± | `#fab219` | |
| ciddi | **`#e8743c`** | standart `#ec835a` **FAIL verdi** (uyarÄ± ile ÎE 13.6 < 15); `#e8743c` ile ÎE 11.2 PASS |
| kritik | `#d03b3b` | |

Dördü de `#131C2F` üstünde ≥3:1. **Her durum rengi ikon + metin etiketiyle birlikte gelir** — renk tek başına anlam taşımaz (Codex §3.5 ile aynı ilke, burada hex düzeyinde bağlandı).

**VIZ-5 Grafik kromu (eksen/grid/mürekkep)**

| Rol | Dark | Light |
|---|---|---|
| grafik yüzeyi | `#131C2F` | `#F8FAFC` |
| ana metin | `#E2E8F0` (gray200) | `#0F172A` (gray900) |
| ikincil metin | `#94A3B8` (gray400) | `#475569` (gray600) |
| eksen etiketi (muted) | `#64748B` (gray500) | `#64748B` |
| grid (saç çizgisi) | `#1E293B` (gray800) | `#E2E8F0` |
| taban çizgisi | `#334155` (gray700) | `#CBD5E1` |

Tümü mevcut `design-tokens.json` gri rampasından alındı — **yeni renk uydurulmadı**.

**VIZ-6 Ä°Åaret (mark) spesifikasyonu**

- Çubuk: ince, veri ucu 4px yuvarlatılmış, taban çizgisine çakılı; komşu çubuklar arası **2px yüzey boşluğu**
- Çizgi: 2px; işaretçi ≥8px; üst üste binen işaretlere 2px yüzey halkası
- Etiket **seçici**: her noktaya sayı yazılmaz; ilk/son/tepe/dip
- Metin daima metin token'ı giyer — **sayı asla seri rengiyle yazılmaz**, yanındaki renkli işaret kimliği taşır
- ≥2 seri → lejant **daima var**; ≤4 seri ayrıca doğrudan etiketlenir (kimlik asla yalnız renkte olmaz)
- Tek seri → lejant kutusu yok, başlık seriyi adlandırır

**VIZ-7 Etkileşim katmanı (varsayılan açık)**

HTML/SVG grafik zaten etkileşimlidir: çizgi/alanda **crosshair + tooltip**, çubuk/nokta/hücrede işaret-başına tooltip. Vuruş hedefi işaretten büyük. Filtreler grafiklerin üstünde **tek satır**. Tooltip'in klavye eşdeğeri ve veri tablosu zorunlu (yalnız hover'a bağlı bilgi erişilemez). Tek istisna: grafiksiz çıplak KPI kutusu.

**VIZ-8 Form seçimi — mevcut iskelete düzeltme**

| Kutu | Åimdi | OlmalÄ± | Neden |
|---|---|---|---|
| Sinyal Yoğunluğu | bar (`tip="bar"`) | zaman ekseninde **çizgi/alan** + 7/30/90 aralığı | "yoğunluk zamanla nasıl değişti" sorusu magnitude-over-time |
| Sektör Dağılımı | **çizgi** (`tip="line"`) | **yatay bar**, değere göre sıralı | kategori kimliği; çizgi sektörler arasında sahte süreklilik üretir |
| 4 KPI | shimmer kutu | **stat tile**: etiket + değer + değişim + son güncelleme + hedef sayfa bağlantısı | çıplak sayı karar üretmez |
| Kredi durumu | KPI kutusu | **metre/ilerleme** + kalan metin | donut varsayÄ±lan deÄil |
| Bar placeholder yükseklikleri | `[38,62,46,78,55,88,64,72]` | **eşit yükseklik** nötr skeleton | farklı yükseklik = sahte trend (D-253/D-395) |

#### 4. İki alternatif (palet kararı — PO kapısı)

| | **A — Marka SSOT'una dön** (önerilen) | **B — İskelet paletini kurumsallaştır** |
|---|---|---|
| Yüzey | `#09111F` zemin / `#131C2F` kart | `#0D1B2A` zemin / `#10233A` panel |
| Eylem | `#2563FF` (marka primary) | `#0072FF` |
| CanlÄ± aksan | `#22D3EE` (marka accent) | `#00FF66` |
| Artı | Pazarlama sitesi ↔ panel aynı marka; `design-tokens.json` tek SSOT kalır; grafik paleti slot 1'i marka rengi olur | Mevcut iskelet dosyası değişmez; "radar/canlı" hissi `#00FF66` ile güçlü |
| Eksi | `panel-kabuk.tsx` + `kabuk.css` renk değerleri güncellenir (~10 satır) | **İkinci marka doğar**; `ai-rules.md` ve `design-tokens.json` ile kalıcı çatışma; `#00FF66` grafikte ölçümü geçmiyor, neon "hacker" algısı marka yasağına yakın |
| Ölçüm | Grafik paleti `#131C2F` üstünde 5/5 PASS (koşturuldu) | Grafik paleti `#10233A` için **yeniden koşturulmalı**; `#00FF66` seri olarak FAIL |

**Önerim: A.** Gerekçe ölçüm değil, maliyet: iki markanın bakımı iki kat iş ve her yeni görevde renk tartışması demektir. `#0D1B2A` ↔ `#09111F` farkı gözle neredeyse ayırt edilemez; ödün küçük, kazanç tek SSOT. `#00FF66` **tamamen atılmaz** — "canlı bağlantı" nokta rozetinde (grafik dışı aksan) kalabilir, orada ölçüm kapısına girmez.

Her iki durumda da **`design-tokens.json`'a `scope.customerPanel` satırı eklenmeli** (D-45 notu güncellenir, Kural 7 gereği eski metin silinmez). Aksi halde panel SSOT'suz kalır ve bu tartışma her görevde yeniden açılır.

#### 5. Öz-eleştiri

- **Canlı tarayıcıda gezmedim.** Tüm UI yargılarım kod okumasına dayanıyor; `localhost:3000/panel-tasarim` açılmadı, ekran görüntüsü de incelenmedi. "Sahte trend" ve "Unicode ikon" bulguları koddan kesin, ama *görsel ağırlığı* ölçülmedi — salih'in ekran kanıtı olmadan kesin sayılmaz (D-382).
- **Palet ölçümlerim yüzey varsayımına bağlı.** Hepsini `#131C2F` (marka kartı) üstünde koşturdum. PO B seçeneğini seçerse (`#10233A`) **tüm tablo yeniden koşturulmalı** — sonuçları oraya taşımak doğru değil, kontrast yüzeye bağlıdır.
- **Light mod ikincil kaldı.** Panel dark-first (`design-tokens.json:118`), light sadece bir kez ölçüldü ve slot 3/4/5 relief gerektirdi. Light mod ciddi gereksinimse ayrı adımlama gerekir.
- **Grafik formu önerilerim veri şeklini bilmeden yapıldı.** "Sektör dağılımı yatay bar olmalı" demek için sektör sayısını bilmem gerekir; 30+ sektör varsa bar da yetmez (ısı haritası/tablo gerekir). yasu'nun API/tablo bağlama görüşü gelmeden form kararı yarım.
- **Ölçüm aracı tek.** `validate_palette.js` OKLab/CVD simülasyonu yapar; gerçek renk körü kullanıcı testi değildir. Geçen palet "ölçümü geçti" demektir, "kullanıcı ayırt etti" demez.

#### 6. Dış kaynaklar (Codex'in listesiyle çakışmayanlar)

| Kaynak | AlÄ±nan somut kural |
|---|---|
| [W3C WCAG 2.2 — SC 2.5.8 Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | Dokunma/tıklama hedefi **≥24×24 CSS px** (veya 24px boşluk); ikon butonlar ve kapatma düğmeleri tipik ihlal. Mevcut yan bar `px-2 py-2` + 14px metin ≈ sınırda — ölçülmeli |
| [WCAG 2.2 — SC 2.4.11 Focus Not Obscured](https://www.w3.org/TR/WCAG22/) | Sticky header focus'lanan öğeyi **kapatmamalı**: `html { scroll-padding-top: <header-yükseklik> }`. `panel-kabuk.tsx:91` sticky header var, scroll-padding yok |
| [Accessible Data Interfaces — ARIA for data UIs](https://www.accessible-data-interfaces.com/core-aria-keyboard-navigation-for-data-uis/) | Dashboard'da ≥5 etkileşim bölgesi olur; **her landmark'a tekil `aria-label`**; async yükleme `aria-busy` ile duyurulur. İskelette `aria-label` var (iyi), `aria-busy` yok |
| [Skip-link deseni](https://newstack.dev/frontend/accessibility-checklist/) | İlk tab durağı skip-link; hedefe **`tabindex="-1"`** şart — çoğu uygulamanın atladığı kısım tam bu |
| [DAR Design — B2B dashboard IA 2026](https://dardesign.io/blog/b2b-dashboard-information-architecture-2026) | Filtre **altyapıdır**: global (kapsam) vs yerel (modül) ayrılır; aktif filtre kaldırılabilir çip olarak görünür. "Tooltip, eksik IA'nın çöp kutusu değildir" |
| [SaaS filtering & sorting UX 2026](https://www.saasui.design/blog/saas-filtering-sorting-ux-patterns) | Filtre/sıralama **URL'de kodlanır** → paylaşılabilir, yer imlenebilir, geri tuşu çalışır. Kaydedilmiş görünüm `localStorage`'da değil **birinci sınıf veri** olarak durur |
| [SaaS dashboard best practices 2026](https://www.aydesign.ai/blog/saas-dashboard-design-best-practices-2026) | Performans bütçesi: **ilk etkileşim <1 s, filtre yanıtı <300 ms**. Tek birincil CTA; "filtreyle sıfır sonuç" ≠ "boş" — ayrı durum, hangi filtrenin gevşetileceğini söyler |
| [Progressive disclosure / bilişsel yük](https://usertourkit.com/blog/complex-dashboard-onboarding) | Eşzamanlı görünür metrik ~**5 ile sınırlı**; derin kontroller komut paleti veya ayarlara iner. Boş durum, veri yokken tam ekran sıfır-gürültü onboarding alanıdır |
| [4Byte — dashboard patterns](https://www.4byte.agency/resources/saas-dashboard-design) | Komut paleti (⌘K) görünür navigasyonun **yerine geçmez**, yanında durur — yeni kullanıcı için keşfedilebilirlik sorunu vardır |

**Dolgu fazı için somut ek öneriler (iskelete dokunmaz, kabul kriteri olur):**

1. **URL durum sözleşmesi:** sekme/filtre/zaman aralığı query param'da (`?sekme=takip&aralik=30g`). Şu an `useState` → yenileyince kaybolur, paylaşılamaz. Codex §4.7/1'in `<Link>` bulgusunun ölçülebilir karşılığı.
2. **Performans kapısı:** ilk etkileşim <1 s, filtre yanıtı <300 ms — kabul kriterine yazılır, ölçülür (D-382).
3. **Metrik sınırı:** ana ekranda eşzamanlı görünür metrik ≤5. Şu an 4 KPI + 2 grafik = sınırda; 5. KPI eklenmek istenirse biri gider.
4. **`aria-busy`:** veri yüklenirken grafik/tablo bölgesine konur; skeleton'ın ekran okuyucu karşılığı yoktur, bu onu sağlar.
5. **`scroll-padding-top`:** sticky header yüksekliği kadar — tek satır CSS, WCAG 2.4.11 kapanır.

### 4.9 salih — Test/UX denetçi: müşteri senaryosu + ölçülmüş erişilebilirlik + rota sözleşmesi (2026-10-21)

**Kapsam:** görüş/öneri. PO onayı olmadan kod kararı değildir. Codex (§4.7) IA ve marka dilini, Claude (§4.8) paleti ölçtü. Ben **denetçi gözüyle** bakıyorum: müşteri gerçekten kullanabiliyor mu, ölçüm mandalı var mı, test bunu yakalıyor mu. Tekrar ettiğim her bulguyu bağımsız ölçümle teyit ettim.

**Skill beyanı (D-401):** `web-design-guidelines` (Vercel — `command.md` canlı çekildi, §Accessibility / §Focus States / §Navigation & State / §Anti-patterns okundu). Claude'un `dataviz`'i ve Codex'in `frontend-design`'ı **kasıtlı kullanılmadı** — rotasyon kuralı (brif) ve görüş defterinde tekrar üretmemek için. Benim merceğim: *insan kullanımı senaryosu + ölçüm kapısı + test kırılganlığı*.

#### 1. Baktığım yer (komut + çıktı)

| Kanıt (komut) | Ölçüm sonucu | Tasarım/test sonucu |
|---|---|---|
| `node -e` ile WCAG kontrast hesabı (9 çift) | `#0072FF` metin/zemin **4.02:1 KALDI**; beyaz/#0072FF **4.33:1 KALDI**; marka `#2563FF` metin/#09111F **3.88:1 KALDI**. Geçenler: `#E6EDF3` 14.72, `#8FA3B8` 6.71/6.12, `#00FF66` 12.83, `#E2E8F0`/#131C2F 13.80 | Bağlantı/metin olarak mavi **iki paletin ikisinde de** 4.5 eşiğini geçmiyor → mavi yalnız **dolgu** (beyaz metinli buton) değil, 14px+bold olmadıkça **metin rengi olarak kullanılamaz** |
| `Select-String panel-kabuk.tsx` (a11y izleri) | `aria-label` var (nav + 4 section); **`aria-busy` yok, `tabIndex` yok, `Link` yok, `usePathname` yok** | Async yükleme ekran okuyucuya duyurulmuyor; navigasyon URL üretmiyor (geri tuşu/paylaşım/yeni sekme çalışmaz) |
| `Get-ChildItem app -Include *.css,*.tsx \| Select-String 'scroll-padding\|Skip to content\|sr-only'` | **0 eşleşme** | WCAG 2.4.11: sticky header (`panel-kabuk.tsx:91`) focus'lanan öğeyi kapatabilir; skip-link yok |
| `Get-ChildItem app\panel -Recurse -Filter page.tsx` | Gerçek rotalar: `/panel`, `/panel/cuzdan`, `/panel/raporlab`, `/panel/sektor-radar` (**4**) | — |
| `panel-sidebar.tsx:22-28` vs üstteki envanter | Sidebar hedefleri: `/panel`, `/panel/radar`, `/panel/raporlab`, `/panel/ag`, `/panel/cuzdan`, `/panel/ayarlar`. Var olmayan hedef **3** (`radar`, `ag`, `ayarlar`); **erişilemeyen sayfa 1** (`sektor-radar` menüde yok) | **Rota sözleşmesi kırık:** menüde olup sayfası olmayan 3, sayfası olup menüde olmayan 1. İskelet 8 öğe listeliyor; bunların kaçının rotası var, kimse doğrulamıyor |
| `package.json` | `vitest`, `@testing-library/*`, `jsdom`, **`vitest-axe` kurulu** | Erişilebilirlik otomatik testi **yazılmamış** — araç var, kullanan yok |
| `panel-kabuk.test.tsx:19-23` | `expect(metin).not.toMatch(/\d/)` | Test **kırılgan**: gerçek veri/`son güncelleme` saati gelince patlar. Niyet "uydurma veri yok" ise hedef `data-yer-tutucu` işareti olmalı, rakam yasağı değil |
| `panel-kabuk.tsx:66` bar yükseklikleri | `[38, 62, 46, 78, 55, 88, 64, 72]` | Claude ile **bağımsız aynı bulgu**: rakam yok ama gradyan trend var → göz "yükseliyor" okur (D-253/D-395 ruhu) |
| `panel-kabuk.tsx:200` | `aria-label="Harita yeri"` section'ı var | §2 dosya haritası ve Codex/Claude taslaklarında **harita yok**; iskelet 4 KPI + 2 grafik **+ harita + tablo** içeriyor. Belge ile kod çelişiyor |
| `/panel-tasarim` canlı açma denemesi | `open_browser_page` **30 sn timeout**, `read_page` CDP timeout | **Görsel doğrulama yapılamadı.** Aşağıdaki tüm UI yargıları kod okumasıdır — ekran kanıtı yok |

#### 2. Sorun / eksik (en aÄÄ±rdan, 3 madde)

1. **Rota sözleşmesi hiçbir yerde test edilmiyor — en ağır risk.** Menü 8 hedef, gerçek sayfa 4. Bu, "müşteri tıklar, 404 görür" sınıfı hatadır ve iskelet onaylanınca `/panel`'e taşınacak. Bugün `vitest` bunu yakalamaz çünkü test yok.
2. **Erişilebilirlik "ölçüm" değil "niyet" düzeyinde.** `vitest-axe` kurulu ama 0 kullanım; `aria-busy` yok; skip-link ve `scroll-padding` yok. PO'nun canlıda bulduğu üç kaçak (yanlış e-posta, okunmayan renk, eksik onay kutusu) **tam olarak bu boşluktan** geçti.
3. **Müşteri ilk 10 saniyede ne yapacağını bilmiyor.** İskelette 4 KPI + 3 grafik kutusu + tablo var, ama **tek bir ana eylem (CTA) yok**; "yer tutucu" etiketi müşteriye değil geliştiriciye konuşuyor. Boş durum metni de yok.

#### 3. Taslağım — 5 senaryoluk denetim tablosu (brif Faz A standardının iskelete uygulanışı)

Bu tablo **müşteri gözünden** ölçer, geliştirici gözünden değil. Her satır kabul kapısı olabilir.

| # | Senaryo | Beklenti | İskelette gerçek (kanıt) | Karar |
|---|---|---|---|---|
| 1 | **10 yaşındaki ilk kez görüyor** | 10 sn'de "ne yapacağım" belli | Ana CTA yok; 7 kutu + tablo; metinler "yer tutucu"/"KPI yeri" (geliştirici dili) | **KALDI** |
| 2 | **Aceleci kullanıcı** | En sık işlem ≤3 tık | Üst bar (5) + yan bar (8) = 13 hedef; hangisi birincil belirsiz; sekmeler URL üretmiyor → geri tuşu işe yaramaz | **KALDI** |
| 3 | **Hata anı** (boş/yetkisiz/eski veri) | Ayrı metin + tek çıkış yolu | Hiçbir durum bileşeni yok; `aria-busy` yok; skeleton "sonsuz yükleniyor" gibi okunur | **KALDI** |
| 4 | **Mobil (320 px)** | Yatay kayma yok, dokunma hedefi ≥24 px | Yan bar `hidden lg:block` → mobilde **hiç menü yok**; mobil çekmece yok; `px-2 py-2` ≈ 34 px yükseklik (sınırda) | **KALDI** |
| 5 | **Okunabilirlik** (kontrast) | Metin ≥4.5:1 | `#0072FF`=4.02, `#2563FF`=3.88, beyaz/`#0072FF`=4.33 → **3 çift eşik altı**; koyu metinler 6.1–14.7 ile rahat | **KALDI** |

**Beş senaryonun beşi de kaldı.** Bu bir başarısızlık değil: iskelet *dolgu öncesi* aşamada ve bu tablo **dolgu kabul kriteri** olarak kullanılmalı.

##### 3.1 Ölçülebilir kabul kapısı (benim işim bu — test danışmanı)

| KapÄ± | Ne yapar | Nereye girer |
|---|---|---|
| **K-1 Rota sözleşmesi testi** | `panel-sidebar.tsx` NAV_ITEMS ↔ `app/panel/**/page.tsx` eşleşmesini doğrular; menüde olup sayfası olmayan / sayfası olup menüde olmayan listeyi **kırmızı** yapar | `vitest`, yeni dosya `app/panel/rota-sozlesmesi.test.ts` |
| **K-2 axe kapısı** | Her panel sayfası render → `vitest-axe` ile ihlal 0 | Mevcut bağımlılık, ek kurulum yok |
| **K-3 Kontrast kapısı** | Palet token'ları için 4.5:1 / 3:1 (büyük metin) hesabı; bugünkü 3 çift kırmızı çıkar | `node` script + `npm run test` zinciri |
| **K-4 Durum matrisi testi** | Her sayfa 4 durumda render edilir: `yukleniyor / bos / hata / yetkisiz`; eksik durum = kÄ±rmÄ±zÄ± | `@testing-library` |
| **K-5 Reduced-motion kapÄ±sÄ±** | `prefers-reduced-motion` altÄ±nda animasyon kapalÄ± mÄ± (mevcut CSS doÄru, test yok) | `jsdom` + matchMedia mock |

**Neden kapı:** Brifin varlık nedeni (PO 19.10: "kodu çalışıyor = ürün satıyor değil"). Kapı olmadan aynı kaçaklar `/panel`'e taşınır.

##### 3.2 İskelete 5 somut düzeltme (kod değişikliği önerisi, ben yazmam — utku'ya)

| # | Düzeltme | Dosya:satır | Gerekçe |
|---|---|---|---|
| 1 | Bar yüksekliklerini **eşitle** (`h-[52%]` hepsi) | `panel-kabuk.tsx:66` | sahte trend (D-253) |
| 2 | `<button>` → `<Link href>` + `aria-current` | `panel-kabuk.tsx:108,148` | geri tuşu, paylaşım, yeni sekme |
| 3 | Mobil menü ekle (çekmece) veya en az yatay kaydırmalı şerit | `panel-kabuk.tsx:139` | mobilde menü **yok** |
| 4 | `html { scroll-padding-top: <header> }` + skip-link | `kabuk.css` / `page.tsx` | WCAG 2.4.11 |
| 5 | Boş durum + tek CTA bloğu ("İlk firmanı keşfet") | `panel-kabuk.tsx` gövde başı | senaryo 1 |

##### 3.3 Müşteri güveni açısından bir uyarı

`panel-kabuk.tsx:99` üst barda **`OSINT` rozeti** var. Claude bunu marka kuralı ihlali olarak ölçtü (`ai-rules.md:22-28` "not OSINT Tool"). Denetçi olarak ekliyorum: **müşteri için bu rozet güven değil "beni izliyorlar" algısı** üretir — ürün karar sorusu PO'ya aittir, ama A/B testinde ölçülmesi gereken tek kelime budur.

#### 4. Ä°ki alternatif (denetim stratejisi)

| | **A — Kapı-önce** (önerilen) | **B — Dolgu-önce** |
|---|---|---|
| Sıra | K-1…K-5 testleri yazılır → iskelet bu kapılardan geçirilir → sonra dolgu | İskelet `/panel`'e taşınır, dolgu yapılır, denetim en sonda |
| Artı | Kaçaklar koda girmeden yakalanır; mevcut `vitest-axe` boşa durmaz; PO'nun 3 kaçağı tekrar etmez | Hızlı görünür ilerleme |
| Eksi | 1 tur gecikme; test yazımı görünmez emek | Aynı 3 kaçak sınıfı tekrar eder; düzeltme maliyeti 5–10× (Claude'un palet uyarısıyla aynı mantık) |
| Risk | Testler iskelet değişince güncellenir (kabul edilebilir) | Denetim "yeşil" der, canlıda PO kırmızı bulur — **bugünkü tablo** |

**Önerim: A.** Gerekçe ölçüm: bugün 5/5 senaryo kaldı ve hiçbiri testle yakalanmıyor; sıra değişmezse `/panel`'de aynı sonucu ölçeriz.

#### 5. Öz-eleştiri

- **Canlı tarayıcıda göremedim.** `open_browser_page` ve `read_page` 30 sn'de timeout verdi; ekran kanıtım **yok**. "Mobilde menü yok" bulgusu `hidden lg:block` sınıfından kesin, ama *görsel ağırlık* ve gerçek 320 px davranışı ölçülmedi (D-382: ölçmediğim şeyi "gördüm" saymam).
- **Kontrast ölçümüm metin varsayımına bağlı.** `#0072FF`'i 14px normal metin kabul ettim; 18.66px+ bold ise eşik 3:1 olur ve **geçer**. Hangi yerde metin, hangi yerde buton dolgusu olduğu tasarım kararıdır — benim tablom "metin olarak kullanılırsa kaldı" diyor.
- **Rota sözleşmesi bulgum sidebar'a ait, iskelete değil.** İskelet 8 öğeyi kendi listesinde tutuyor; gerçek uyumsuzluk `panel-sidebar.tsx` ile `app/panel` arasında. İskelet onaylanınca **hangi listeye** bağlanacağı hâlâ belirsiz — brifte "rota sözleşmesi tek dosya" maddesi olduğu hâlde.
- **Senaryo tablom kullanıcı testi değil.** 5 senaryo masa başı uzman değerlendirmesidir; gerçek müşteriyle yapılmadı. "10 sn'de anlar" iddiası test edilmedi, hipotezdir.
- **`vitest-axe` kurulu ama sürümü (`0.1.0`) eski** — axe-core API farkı çıkabilir; K-2 kapısı yazılırken ilk iş sürüm doğrulaması olmalı. Bunu bugün ölçmedim.

#### 6. Dış kaynaklar (Codex/Claude listesiyle çakışmayan)

| Kaynak | AlÄ±nan somut kural |
|---|---|
| [Vercel Web Interface Guidelines — Navigation & State](https://vercel.com/design/guidelines) | "URL reflects state — filters, tabs, pagination in query params"; "Links use `<a>`/`<Link>` (Cmd/Ctrl+click, middle-click)". K-1 ve düzeltme #2'nin dayanağı |
| [Vercel WIG — Anti-patterns](https://vercel.com/design/guidelines) | "`<div>`/`<span>` with click handlers", "Inline `onClick` navigation without `<a>`" — iskeletin `button` navigasyonu bu sınıfa girer |
| [Vercel WIG — Accessibility](https://vercel.com/design/guidelines) | "Headings hierarchical; include skip link for main content", "`scroll-margin-top` on heading anchors", "Icon-only buttons need `aria-label`" |
| [Kent C. Dodds — Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications) | Rota sözleşmesi ve durum matrisi **entegrasyon** testidir, snapshot değil; K-1/K-4 bu katmanda yazılmalı |
| [Playwright — accessibility testing](https://playwright.dev/docs/accessibility-testing) | Ekran kanıtı + `axe` taramasının aynı koşuda alınması; brifteki "kanal mazereti yok" maddesinin aracı |

### 4.10 ihsan — müşteri gözü: şirket sahibi + pazarlamacı; öncelik, TR/EN, öğretici, Mimir balonu (2026-10-21)

**Skill beyanı:** `site-specification` (site tipi → hedef kitle → yerleşim → tipografi çıkarımı) + `ihsan-rapor-tarzi`. Önceki görüşler mühendis/denetçi/marka merceğiydi; bu bölüm **müşterinin cebinden** bakar. Kod yok (D-420); yalnız iskelete eklenecek **boş yuva** önerisi.

#### 1. Baktığım yer (ölçüm)

| Ne | Bulgu |
|---|---|
| `frontend-web/package.json` + `app/layout.tsx` | i18n paketi **yok** (`next-intl`/`i18next`/`react-intl` aramasında 0 sonuç). Tek iz: `<html lang="tr">`. İngilizce bugün **sıfır** |
| `frontend-web/app/panel/page.tsx` (gerçek `/panel`) | Metinler koda gömülü ve **aksansız** ("Canli", "Baglaniyor...", "Henuz sinyal yok", "Radardaki Sirket", "Yeni Eslesme"). Müşteri ilk ekranda bunu görür |
| aynı dosya | "Profil Inceleyenler" KPI'sı `deger={null}` — veri yok, boş kart. "Bu sayı ne işe yarar" metni yok |
| aynı dosya | Giriş/karşılama/"önce şunu yap" yok; yeni müşteri 0 kredi + 0 sinyal ile boş ekran görür (hipotez: terk riski; test edilmedi) |
| `package.json` | `sonner` (toast) kurulu. Tur kütüphanesi (`driver.js`/`joyride`) **yok**. Mimir balonu için kütüphane gerekmez |
| `panel-kabuk.tsx` (iskelet) | Sağ üst boş; Mimir, kredi, dil, yardım yuvası yok (§4.6 ile aynı bulgu) |

#### 2. Müşteri kim? Ne sorar? (hipotez — gerçek müşteri görüşmesi yapılmadı)

| Persona | Ä°lk 10 saniyede aradÄ±ÄÄ± soru | Panelde cevabÄ± |
|---|---|---|
| Şirket sahibi | "Param nerede, ne kadar kaldı, bana ne kazandırdı?" | Kredi bakiyesi + kalan gün + bu ay getirdiği (eşleşme sayısı) |
| Şirket sahibi | "Riskim var mı? Müşterim/tedarikçim batıyor mu?" | Öncelikli uyarı şeridi (kırmızı/sarı, kaç firma) |
| Pazarlamacı/satış | "Bugün kimi aramalıyım?" | Öncelikli fırsat listesi (en üst 5, tek tık "radara ekle") |
| Pazarlamacı/satış | "Yeni ne çıktı, rakip ne yaptı?" | Canlı sinyal akışı (mevcut) + "son girişten beri N yeni" |
| İkisi de | "Buna güvenebilir miyim, veri ne kadar taze?" | Her blokta kaynak + son güncelleme (D-213 VERI-ETIKET-01) |
| İkisi de | "Nasıl kullanılıyor, takıldım." | Öğretici + Mimir balonu |

#### 3. Öncelik sırası (P0 → P2)

| SÄ±ra | Ne | Neden | BaÄÄ±mlÄ±lÄ±k |
|---|---|---|---|
| P0-1 | Durum şeridi: kredi · kalan gün · yeni uyarı sayısı | Sahibin ilk sorusu "param"; bugün sağ üstte yok | kredi API (cüzdan hook'u var) |
| P0-2 | Karşılama kartı (yeni müşteri): "3 adımda başla" kontrol listesi | Boş ekran = terk | yok (statik) |
| P0-3 | Öncelikli fırsatlar/uyarılar (en üst 5) | Pazarlamacının "bugün ne yapayım"ı | sinyal akışı (var) |
| P0-4 | Boş/yükleniyor/hata/yetkisiz durumlar iki dilde | Güven; salih K-4 ile aynı | durum sözleşmesi §3.6 |
| P0-5 | TR/EN dil anahtarı + metin sözlüğü (çeviri anahtarları) | PO şartı; sonradan eklemek tüm dosyaları yeniden yazdırır | karar: kütüphane |
| P1-1 | Mimir balonu (sağ alt) | PO şartı; öğretici + destek tek kapı | D-410 sınırı |
| P1-2 | Bağlamsal yardım: her KPI/grafikte "?" ve "nasıl okunur" | Pazarlamacı grafiği yorumlayamazsa değer görmez | metin yazımı |
| P1-3 | Türkiye OSB haritası (§7) | PO talebi | harita brifi |
| P2-1 | Rapor indir/paylaÅ (PDF/e-posta) | Sahip ortaÄÄ±na/muhasebeye iletir | rapor altyapÄ±sÄ± |
| P2-2 | Bildirim tercihleri (e-posta/uygulama içi) | Radar değeri "ben bakmazken haber ver" | bildirim servisi |
| P2-3 | Takım/kullanıcı davet, fatura geçmişi | Büyüyen müşteri | satış modeli kararı |

#### 4. Ana sayfa = tek dikey akÄ±Å (yukarÄ±dan aÅaÄÄ±; her blok bir soruya cevap)

```
┌ Üst bar: logo · [Genel][Radarlar][Firmalar][Raporlar][Krediler] ── [Kredi 120 · 18 gün] [🔍] [TR|EN] [?] [Hesap] ┐
│ ① DURUM ŞERİDİ    "Bugün": N yeni uyarı · N yeni eşleşme · bakiye · kalan gün       (3 saniyede okunur)
│ ② KARŞILAMA/YOL   yeni müşteri: [1 Firma ekle][2 Radar kur][3 İlk raporu aç] ilerleme çubuğu → tamamlanınca KAYBOLUR
│ ③ ÖNCELİKLİ       "Bugün bakman gerekenler": en üst 5 satır + [Radara ekle]/[İncele]
│ ④ KPI (4)         her kartta: ad · değer · önceki döneme fark · (?) ne işe yarar
│ ⑤ TREND + DAĞILIM 2 grafik; her birinin altında tek cümle yorum "bu ne demek?"
│ ⑥ CANLI AKIŞ      mevcut sinyal akışı; filtre: önem / sektör / il
│ ⑦ HARİTA          Türkiye OSB haritası (§7) — aşağıda, ilk ekranı yormaz
│ ⑧ SON İŞLEMLER    rapor/kredi/radar hareketleri tablosu
│ ⑨ YARDIM ŞERİDİ   "Takıldın mı?" kısa kılavuzlar + Mimir'e sor
└ Sağ alt: [Mimir balonu] (sabit, her sayfada) ┘
```

Kurallar: (a) ①-③ ilk ekranda (katlama çizgisi üstü); (b) aşağı inildikçe **derinleşir** (özet → detay → tablo); (c) ② tamamlanınca ve ③ boşsa gizlenir, yer boşluğu bırakılmaz; (d) uzun listede "tümünü gör" bağlantısı gerçek sayfaya gider (rota sözleşmesi, salih K-1); (e) her blokta kaynak+tarih (D-213).

#### 5. Menü yol haritası (D-253: **olmayan sayfa menüde görünmez**; "yakında" etiketi de koyma, çünkü hayalet menüdür)

| Aşama | Menü (kanonik: Codex §4.7 ağacı) | Not |
|---|---|---|
| Şimdi (sayfası var) | Genel Bakış · Sektör Radarı · Raporlarım · Kredi/Cüzdan | `/panel`, `/panel/sektor-radar`, `/panel/raporlab`, `/panel/cuzdan` |
| Sonra (sayfa yazılınca eklenir) | Radarlarım · Firma Arama/Analiz · Takip Listem · Ayarlar · Yardım Merkezi | salih'in bulduğu 3 kırık rota önce çözülmeli |
| Gelecek (PO kararı gerekir) | Harita (OSB) · Bildirimler · Takım/Kullanıcılar · Fatura/Plan · Entegrasyonlar (API) · Rakip Karşılaştırma | Her biri ayrı karar + ürün kartı (D-386) |

Menüye gelecek öğe için **yer** ayırmak serbest (grup başlığı + kaydırılabilir yan bar); öğenin kendisi sayfa yazılınca eklenir.

#### 6. İki dil sözleşmesi: Türkçe varsayılan, İngilizce ikinci

| Konu | Öneri |
|---|---|
| Altyapı | Metin koddan çıkar: tek sözlük dosyası/dil (`tr`, `en`), anahtar = anlam (`kpi.credit.label`), **cümle birleştirme yok** (çeviri bozulur). Kütüphane seçimi utku'nun ölçümüne bağlı (karar: Next 16 App Router ile uyum) |
| Varsayılan | `tr`. Dil seçimi sırası: kullanıcı profili → çerez → tarayıcı dili → `tr`. Panel arama motoruna açılmıyor; `hreflang` gerekmez |
| Anahtar konumu | Üst barda `TR | EN` iki harfli bölünmüş düğme; seçili olan `aria-pressed`; değişince sayfa **yenilenmeden** metinler değişir ve seçim kalıcı |
| Biçimler | Tarih `gg.aa.yyyy` (TR) / yerel EN biçimi; sayı ve para `Intl` ile (TR: `1.234,56`; EN: `1,234.56`); kredi birimi iki dilde aynı sözcük sözlükte tanımlı |
| Marka terimleri | Çevrilmez: Huginn, Mimir, Radar, Premium (D-394 ad standardı) |
| Uzunluk | EN metni TR'den kısa/uzun olabilir: düğme ve kart `min-width` + `truncate` + `title`; iki dilde de görsel kontrol (salih mandalı) |
| Aksan | `Canli/Henuz/Sirket` gibi aksansız TR metinler **hata** sayılır; sözlüğe geçerken düzelir. Vitest'te "aksansız yaygın kelime" listesi mandalı önerilir |
| Hata/boş metinler | Her durum iki dilde yazılı olmadan sayfa "bitti" sayılmaz (§3.6 durum sözleşmesi) |
| Mimir | Kullanıcının seçili dilinde yanıt verir; soru önerileri de çevrilir |
| `<html lang>` | Dil değişince `lang` güncellenir (okuyucu yazılımı doğru telaffuz etsin) |

#### 7. Öğretici sistemi (müşteri bırakıp gitmesin)

| Katman | Ne | Ne zaman | KayÄ±t |
|---|---|---|---|
| 1. Karşılama kontrol listesi | 3 adım + ilerleme çubuğu (dashboard ②) | İlk girişten tamamlanana kadar | profil bayrağı (yasu tarafı) |
| 2. Kısa tur (isteğe bağlı) | 4-5 durak: durum şeridi → fırsatlar → KPI → menü → Mimir. **Zorla değil**, "Atla" daima var | İlk giriş + Yardım menüsünde "Turu yeniden başlat" | yerel + profil |
| 3. Boş durum rehberi | Boş kartta "ne yapınca dolar" + tek buton | Veri yokken | — |
| 4. Bağlamsal "?" | KPI/grafik başlığında: ne ölçer · nasıl hesaplanır · nasıl yorumlanır (3 satır) | İstendiğinde | — |
| 5. Yardım merkezi | Kısa kılavuzlar (3-5 dk okuma) + sık sorular; her kılavuz iki dilde | Menüde `?` | — |
| 6. Mimir | Sorulara canlÄ± cevap (aÅaÄÄ±da) | Her yerde saÄ alt | oturum |

Kural: öğretici metin **ürün sözlüğünden** gelir (§18 pazarlama sözlüğü, D-395); kanıtsız iddia ("en doğru", "garantili") yok.

#### 8. Mimir chat balonu (D-410: yalnız asistan, salt okunur müşteri yüzü)

| Konu | Öneri |
|---|---|
| Konum | Sağ alt sabit yuvarlak düğme; mobilde alt çubuğun üstünde, güvenli alan payıyla. (Önceki taslakta "sağ üst" idi; sağ üst kredi/dil/hesap için ayrıldı) |
| Açılış | Düğme → 360 px genişlikte panel (masaüstü) / tam ekran sayfa (mobil). `Esc` kapatır, odak panele girer, kapanınca düğmeye döner |
| İlk mesaj | Karşılama + **3 öneri soru** ("Bu sinyal ne demek?", "Kredim ne zaman biter?", "İlk radarı nasıl kurarım?"). Sorular bağlama göre değişir (hangi sayfadaysa) |
| Sınır | Salt okunur: kredi düşürme, radar silme, ödeme yapma **yok**. Yalnız kendi hesabının verisini okur (tenant sınırı); başka firmanın özel verisini göstermez; KVKK yasu'da (D-410) |
| Güven | Yanıtın altında kaynak/sayfa bağlantısı; emin değilse "bilmiyorum, destekle iletişime geç" (uydurma yasak, D-395) |
| Durumlar | Yazıyor göstergesi, hata (yeniden dene), kota doldu (kalan hak + yükseltme yolu — Mimir kota paketleri D-395), çevrimdışı |
| Erişilebilirlik | Düğmede `aria-label`, panel `role="dialog"`, yeni mesajlar `aria-live="polite"`, klavye ile tam kullanım |
| Dil | Seçili UI diliyle yanıt; dil değişirse bir sonraki yanıttan itibaren |
| Ölçüm | Tıklanma, soru sayısı, "işe yaradı/yaramadı" (PANEL-OLAY-OLCUM-01 hattı kullanılır; yeni olay tipi utku/yasu kararı) |

#### 9. Ä°skelete eklenecek BOÅ yuvalar (kod PO onayÄ±ndan sonra, D-420)

| Yuva | Ä°skelette yeri | Faz |
|---|---|---|
| Durum şeridi | Üst bar sağı + ana sayfa ① | A (boş çerçeve) |
| Dil anahtarı | Üst bar sağı | A |
| Yardım `?` menüsü | Üst bar sağı | A |
| Hesap menüsü | Üst bar en sağ | A |
| Karşılama/yol kartı | Ana sayfa ② | A |
| Öncelikli fırsatlar | Ana sayfa ③ | A |
| KPI "?" ve fark rozeti yuvası | KPI kartı içi | A |
| Yardım şeridi | Ana sayfa ⑨ | A |
| Mimir balonu | Sağ alt sabit | A (yalnız düğme, panel boş) |
| Mobil alt gezinme / menü çekmecesi | Mobil | A (salih: mobilde menü bugün yok) |
| Sözlük dosyaları (`tr`,`en`) + sağlayıcı | Altyapı | B |

#### 10. 2 alternatif

| | ArtÄ± | Eksi |
|---|---|---|
| **A — Önce dil+sözlük altyapısı, sonra yuvalar** | Sonradan çeviri yükü sıfır; aksansız metinler baştan düzelir | İlk görünür ilerleme gecikir; tüm ekip dosyalarına dokunur |
| **B — Önce yuvalar (TR gömülü), dil sonra** | PO hızlı görsel ilerleme görür | Sonra tüm metinleri taşımak = çift iş (makespan kötü); gömülü aksansız metin kalır |

**Öneri: A.** Gerekçe: çeviri yükü sonradan eklenince en pahalı iştir; yuva çerçevesi sözlük anahtarlarıyla yazılırsa çift iş çıkmaz. Makespan etkisi: sözlük altyapısı kısa bir ön iş, yuvalar paralel ilerler.

#### 11. Öz-eleştiri

- **Müşteri sesi yok.** Persona soruları masa başı hipotez; gerçek müşteri görüşmesi/ölçüm yapılmadı. İlk 3 müşteriyle "ilk 10 sn" testi yapılmadan P0 sıraları kesin sayılmaz.
- **Kapsam şişme riski.** 9 blok + 6 öğretici katman + Mimir tek seferde fazla. Gerçekçi sıra: P0 (şerit, karşılama, fırsat, durumlar, dil) → P1 (Mimir, "?") → P2. PO onayı sırayla.
- **Veri bağımlılığı ölçülmedi.** "Önceki döneme fark", "kalan gün", "bu ay getirdiği" için API alanlarının var olup olmadığını yasu ile ölçmedim; yoksa o kutular boş durumda kalır, uydurma sayı yazılmaz.
- **i18n kütüphane seçimi açık.** `next-intl` vb. önerisini ölçmeden dayatmadım; utku Next 16 uyumunu ölçmeli.
- **Eski taslağım (§4.6)** sağ üstte Mimir diyordu; burada sağ alta taşıdım. Çakışma bilerek, gerekçe: sağ üst kredi/dil/hesap için dolu.

#### 12. Karar kapÄ±larÄ± (PO)

| # | Soru | Öneri |
|---|---|---|
| K-a | Dil altyapısı önce mi (A), yuvalar önce mi (B)? | A — **PO kararı: A (21.10)**, sıra: dil + sözlük → yuvalar |
| K-b | Mimir balonu sağ alt, sağ üst yerine? | Evet — **PO: öneriler geçerli (21.10)** |
| K-c | Öğretici: zorunlu tur mu, isteğe bağlı mı? | İsteğe bağlı + karşılama listesi — **PO: geçerli (21.10)** |
| K-d | İlk 3 müşteriyle "ilk 10 sn" testi P0'dan önce yapılsın mı? | Evet, ucuz ve hızlı — **PO: geçerli (21.10)** |

### 4.10-utku — taşıma mühendisliği: iskelet → `/panel` (2026-10-21, kör yazıldı)

**Körleme beyanı (dürüst):** Bu bölümü yazarken §4.7, §4.8, §4.8b, §4.9 **gövdesini okumadım**; belgede yalnız başlık satırlarını listeledim (bölüm sınırı için, `_tmp/yapi_basliklar.py`). **Ama bir istisna var:** §4.1'i (kendi bölümüm) yazarken §4.7 ve §4.8'i **zaten okumuştum** (21.10 sabahı). O okuma beynimde duruyor; bu bölümde onlardan alıntı ya da sonuç kullanmadım, bağımsız ölçüm yaptım ama "tamamen kör" değilim. Derlemede ağırlığı buna göre ver. §1, §2, §3, §4.6 ve brif okundu; kod okundu.

**Skill okundu:** `deprecation-and-migration` (taşıma/emeklilik disiplini) ve `incremental-implementation` (ince dilimler). Yasak dört skill kullanılmadı. Bu bölümden çıkan ana fikir: **taşıma bir tasarım işi değil bir geçiş işi**; geri dönüş yolu olmadan "bitti" denmez.

**Kova özeti:** §1 tablosunda **11 [A] kanıt**; ön-kayıtlı **2 [B] iddia**; **3 [C] PO kararı** (§5 "Karar kapıları"). Metnin tamamında etiket sayısı [A] 27 · [B] 4 · [C] 7 (taşıma adımları, alt satırlar ve öz-eleştiri tablosu dahil); özet yalnız ana iddiaları sayar.

---

#### 1. BaktÄ±ÄÄ±m yer

Hepsi `_tmp/tasima_olcum.py`, `tasima_ek*.py` çıktısı; tek satır özet + ham dosya `data/_tmp/tasima_*.md`.

| # | Komut / dosya:satır | NE gördüm | Kova |
|---|---|---|---|
| 1 | Envanter sayımı (`tasima_olcum.py` §1) | İskelet **6 dosya, 450 satır** (`panel-kabuk.tsx` 232, `harita-yuvasi.tsx` 58, `kabuk.css` 50, 2 test, `page.tsx` 13). Gerçek panel: `components/panel` **8 dosya 611 satır**, `app/panel` **8 dosya 941 satır** | [A] |
| 2 | Çakışma sayımı (§2) | **Dosya adı çakışması: 1** (`page.tsx`, farklı dizinler, gerçek çakışma değil). **Export sembol çakışması: 0** (iskelet 5 sembol, gerçek 14). **CSS sınıf çakışması: 0** (3 sınıf, hepsi `kabuk-` önekli) | [A] |
| 3 | Bağlantı grafiği (§3) | İskeleti DIŞARIDAN import eden **kod dosyası: 0** (`tsconfig.tsbuildinfo` artefakt, kod değil). `design/tr-outline.ts` yalnız iskelet içinden import ediliyor | [A] |
| 4 | `app/panel/layout.tsx:8-14` + `panel-kabuk.tsx:92,137,173` | Gerçek layout `SidebarProvider > PanelSidebar + SidebarInset > PanelTopbar + <main>`. İskelet **kendi** `<header>`(92) + `<aside>`(137) + `<main>`(173) çiziyor, `SidebarProvider` kullanmıyor, `components/ui/*` shadcn bileşeni **0** kullanıyor | [A] |
| 5 | `middleware.ts:29,44` | `matcher: ['/', '/panel/:path*']`. `/panel-tasarim` bu matcher'ı **kapsamıyor** (regex `^/panel/` → False); yani iskelet host kapısından (sirketarama → ticariradar 307) **muaf**, üç host'ta da açık | [A] |
| 6 | Renk kaynağı (`tasima_ek3.py`) | İskelet: `panel-kabuk` **33** + `harita-yuvasi` **9** = **42 sabit hex, 0 tema tokeni**. Gerçek panel (6 dosya): **0 sabit hex, 20 tema tokeni** (`raporlab` 10, `kpi-kart` 3, …) | [A] |
| 7 | Menü karşılaştırması (`tasima_ek5.py`) | Gerçek menü **7 öğe** (Panel, Radar⏳, RaporLab, Sektör Radarı, UBO Ağı⏳, Cüzdan, Ayarlar⏳). İskelet **5 üst + 8 yan** sabit öğe, `href` alanı **yok**. Ortak etiket: **1** (`ayarlar`). Gerçek sayfa karşılığı olan iskelet öğesi: yalnız "Sektör Radarı" (iskelette `/panel/sektor`, gerçekte `/panel/sektor-radar`) | [A] |
| 8 | `app/panel/page.tsx:54-57` | Gerçek ana sayfa **canlı veriye bağlı**: 4 `KpiKart` (`kalanKredi`, `scored_companies`, `total_active_signals`, `null`), `RadaraEkleButon`, `KrediYetersizModal`, `useEffect` fetch. İskelet bunların **hiçbirine** sahip değil | [A] |
| 9 | Test kırılma yüzeyi (`tasima_ek2.py`) | Panel testleri import ediyor: `panel.test.tsx` → `kpi-kart`, `kredi-yetersiz-modal`, `yukselt-modal`; `rota-sozlesmesi.test.ts` → `panel-sidebar`; `sektor-radar.test.tsx` → `./page`. **İskeleti import eden test: 0**. Vitest taban: `app/panel-tasarim` + `app/panel` + `components/panel` = **32 test, 32 geçti, 0 kalan, 17 suite** | [A] |
| 10 | `git log --since=48h` (§7, ek4 §3) | Panel/iskelet dizinlerine 48 saatte **3 commit**: `ee2d5543` (iskelet), `5fded8b5` (harita), `c3d878dc` (rota sözleşmesi + `panel-sidebar.tsx`). Commit'siz değişiklik: **yok** | [A] |
| 11 | `app/panel-tasarim/page.tsx:7-8` | İskelet `robots: {index:false}` taşıyor; gerçek `app/panel/layout.tsx` **taşımıyor** (YOK). Taşınınca noindex ya kaybolur ya gerçek paneli de etkiler | [A] |

**Kritik olmayan ama dürüst not:** `components/panel/*` ve iskelet birbirinden **bağımsız büyüdü**; çakışma sayısı 0 olması "kolay taşınır" demek değil, tam tersi: **birleştirilecek ortak arayüz yok**, çünkü iki taraf aynı işi farklı adla ve farklı renk sistemiyle yapıyor.

---

#### 2. Sorun / eksik (en aÄÄ±rdan)

1. **Taşıma "kopyala-yapıştır" değil "yeniden yaz" ve riski ikiye bölünmüyor.** [A] İskelet gerçek layout'un **yerine geçemez**: kendi header/aside/main'ini çiziyor, gerçek `layout.tsx` zaten `SidebarProvider` ile aynı üçlüyü çiziyor. İkisini birlikte render etmek **çift sidebar + çift topbar** üretir. Seçenek yalnız ikisi: (i) iskeleti gerçek `layout.tsx`'in **içine** bileşen olarak oturtmak (kabuğun `<header>/<aside>/<main>` sarmalayıcısını atıp yalnız içerik bloklarını almak), ya da (ii) gerçek layout'u iskeletin sarmalayıcısıyla **değiştirmek** (shadcn `SidebarProvider`, mobil `Sheet`, `PanelTopbar` kaybı). (ii) mevcut mobil davranışı ve `sidebar` shadcn bileşeninin klavye/aria desteğini **geri alır**.
2. **Taşıma sırasında iki yüzeyin aynı anda değişmesi.** [A] Son 48 saatte `panel-sidebar.tsx`'e iki ayrı görev dokundu (`c3d878dc` rota sözleşmesi, ve Sektör Radarı/Ayarlar kararları). Aynı dosyayı taşıma sırasında üçüncü bir iş de değiştirirse sessiz birleşme çakışması çıkar. İskelet `UST_SEKMELER/YAN_GRUPLAR`'ı (33 satır) sabit; gerçek menü `NAV_ITEMS` (tek kaynak, rota sözleşmesi testiyle korunuyor). **İskeletin menüsünü canlı menüye taşımak, rota sözleşmesinin korumasını atlatır**: sabit sabitleri `NAV_ITEMS`'a çevirmeden taşıma yapılırsa test hiçbir şey yakalamaz.
3. **Güvenlik/host kapısı iskelette yok.** [A] `/panel-tasarim` matcher dışında; üç host'ta açık ve auth yok. Şu an zararsız (statik, veri yok) ama **taşımadan sonra veri bağlanırsa** aynı kapıdan geçmesi gerekir. Taşıma planı bunu T-adımı olarak içermeli, sonradan akla gelen bir madde olmamalı.

---

#### 3. Taslağım — taşıma planı (tablo; rakam yok, her adım ölçülebilir)

**Ä°lke:** her adÄ±m **tek commit**, her adÄ±mda `vitest app/panel components/panel` yeÅil, her adÄ±m **tek baÅÄ±na geri alÄ±nabilir** (`git revert <hash>`), `/panel-tasarim` taÅÄ±ma bitene kadar **silinmez** (yan yana yaÅar).

| Adım | Ne değişir (dosya) | Çıkış ölçüsü (komut) | Geri alma | Kova |
|---|---|---|---|---|
| **T0** (önkoşul) | Kod yok. `UST_SEKMELER/YAN_GRUPLAR` yerine karar: iskelet menüsü `NAV_ITEMS`'tan **türetilecek** mi? Rota sözleşmesi testi `panel-tasarim`'i de taramalı | `rota-sozlesmesi.test.ts` kapsamını `panel-tasarim`'e genişletme kararı | — | [C] |
| **T1** | `design/` altına token tanımı: iskeletin 42 hex'i için **mevcut** `responsive.css` tokenlarıyla eşleme tablosu (yeni token yalnız eşleşme yoksa) | `rg "\[#[0-9A-Fa-f]{6}" app/panel-tasarim` = hedef 0 | `git revert` | [A] |
| **T2** | `app/panel-tasarim/*` içinde: 42 hex → token (sadece iskelet dosyaları, `/panel`'e dokunma). Dark+light ekran | sabit hex = 0; Playwright dark/light ekran farkı gözle | `git revert` (iskelet yalnız kendi dizinini etkiledi) | [A] |
| **T3** | İskeletin içerik bloklarını (`YerTutucuKart`, `GrafikYerTutucu`, `HaritaYuvasi`, `ParselKarti`) `components/panel/` altına **bileşen** olarak çıkar; `panel-kabuk.tsx` bunları oradan import etsin | `vitest components/panel` + `app/panel-tasarim` yeşil; export çakışması = 0 (şu an 0) | `git revert` | [A] |
| **T4** | `app/panel/page.tsx` (103 satır) **yanına** yeni bileşenleri ekle, eski `KpiKart` bloğunu **silme**; iki yerleşim yan yana, bayrakla seçilir | `vitest app/panel` yeşil; `panel.test.tsx` 10 test hâlâ geçiyor | bayrağı kapat (kod silinmez) | [A] |
| **T5** | Header/aside/main sarmalayıcısını **atla**: gerçek `layout.tsx` kabuğu korunur, iskeletten yalnız içerik gelir. `layout.tsx` değişmez | `layout.tsx` diff = 0 satır | — | [A] |
| **T6** | Menü: iskeletin sabit menüsü gerçek `NAV_ITEMS`'a **bağlanır**; `href` yok olan öğeler çıkar (rota sözleşmesi testi korur) | `rota-sozlesmesi.test.ts` yeşil | `git revert` | [A] |
| **T7** | `/panel`'in eski bloğu bayrakla kapatılır, 1 hafta sonra silinir; `app/panel-tasarim` `git rm` | iskelet import eden kod = 0 | silme öncesi etiketle (tag) | [C] |

```
BUGUN                       T1-T2 (izole)            T3-T4 (yan yana)           T5-T7 (gecis)
/panel-tasarim  [iskelet]   [iskelet, token'li]      [iskelet] ──┐              [silindi]
                                                                 ├ ortak bilesen (components/panel)
/panel          [gercek]    [gercek, DEGISMEZ]       [gercek + bayrakli yeni] → [yeni yerlesim]
layout.tsx      [gercek]    [gercek]                 [gercek]                  [gercek, DEGISMEDI]
```

**Taşıma tek commit mi?** Hayır. [A] Gerekçe ölçümlerden: 450 satırlık iskelet, 941 satırlık `app/panel` ve 611 satırlık `components/panel` birlikte 1.7 bin satırdan fazla alan; test kırılma yüzeyi 5 dosya; aynı dosyaya 48 saatte 2 ayrı görev dokundu. Tek commit'te bir hata bütün taşımayı geri çevirir.

**Kaç adım?** 8 (T0–T7), ama bunların **5'i `/panel`'e hiç dokunmuyor** (T1, T2, T3 kısmen, T0, T7 sonrası). Gerçek paneli etkileyen yalnız T4, T5, T6.

**Geri alma maliyeti:** [A] **Düşük**, çünkü (a) iskeleti import eden dış kod 0, (b) `layout.tsx` hiç değişmiyor (T5), (c) T4 bayraklı, (d) her adım ayrı commit. Tek maliyet: `design/tr-outline.ts` ve `design/LISENS.md` iskelet silinse de **kalır** (lisans kaydı yetim olmamalı).

---

#### 4. Ä°ki alternatif

| | **A — Dilimli taşıma (yukarıdaki T0–T7)** | **B — Tek PR, iskelet = yeni `/panel`** |
|---|---|---|
| Artı | Her adım ayrı geri alınır; `/panel` bozulursa tek adım geri; testler her dilimde koşar | Hızlı (tek inceleme); iskelet olduğu gibi gelir, bileşen çıkarma işi yok |
| Eksi | 8 commit, 3–4 gün sürer; bayraklı çift yerleşim geçici kod yükü | **Çift sidebar/topbar** riski (bkz. Sorun 1); `SidebarProvider` + mobil `Sheet` kaybı; 42 hex dark modu bozar; `panel.test.tsx` 10 test canlı veri bağlamayı kaybeder |
| Risk | Düşük | Yüksek (canlı müşteri paneli) |
| **Önerim** | **A** | |

**Gerekçem:** [A] ölçüm B'yi doğrudan çürütüyor: iskeletin `<main>/<aside>/<header>` üçlüsü gerçek `layout.tsx` ile çakışıyor ve iskelet `SidebarProvider` kullanmıyor. B ancak `layout.tsx`'i **silerek** çalışır; bu mobil davranışı geri alır. **Bu bir tercih değil mühendislik gerçeği.**

**Tercih kısmı [C]:** T0'daki "iskelet menüsü `NAV_ITEMS`'tan mı türetilsin" ve "T7'de iskeleti ne zaman silelim (1 hafta mı, onaydan hemen sonra mı)" PO kararıdır; ölçüm karar vermez.

---

#### 5. Öz-eleştiri

**"Ölçtüm mü?"**

| İddia | Ölçtüm mü? | Nasıl |
|---|---|---|
| Çakışma sayıları (1 dosya adı, 0 sembol, 0 CSS), hex/token sayıları (42/0, 0/20), menü karşılaştırması, git commit sayısı, test sayısı 32/32 | **EVET** | `tasima_*.py` betikleri çalıştırıldı, çıktı dosyadan okundu |
| "Çift sidebar/topbar üretir" (Sorun 1) | **HAYIR — kod okumasıdır.** | `panel-kabuk.tsx:92,137,173` ve `layout.tsx:8-14` satırlarını okudum. İkisini yan yana render edip Playwright ile **görmedim**. "Görmedim, mantıksal çıkarım" |
| "Dark modda 42 hex bozar" | **HAYIR — kod okumasıdır.** | Sabit hex olduğu ve `.dark` tokenı kullanılmadığı doğru; **dark'ta görsel olarak bozulduğunu ekranda görmedim**. Önceki turda (§4.1) bunu açıkça "bilmediğim" yazmıştım, hâlâ görmedim |
| "Geri alma maliyeti düşük" | **KISMEN** | İçe aktarma grafiği ölçüldü (0 dış import); ama bir adımı **gerçekten geri alıp** testleri koşmadım |
| "Taşıma 3–4 gün" | **HAYIR — tahmin.** | Hiçbir ölçüm değil, adım sayısından çıkarım. **Çıkarın**, derlemede ağırlık vermeyin |

**ZayÄ±f yanÄ±m:**
- Gerçek `/panel`'i canlı müşteri gözüyle hiç kullanmadım; "gerçek panel iyi çalışıyor" varsayıyorum çünkü 32 test geçiyor. Test geçmesi UX'in iyi olduğunu göstermez.
- Taşıma planı **benim yazdığım iskeletin** taşınması; kendi koduma karşı yumuşak olma riskim var. Bu yüzden "iskelet yeniden yazılır" ihtimalini (iskeleti çöpe atıp `components/panel` üstüne sıfırdan bileşenleştirmek) alternatif olarak yazmadım. Yazmalıydım: [C] bunu başkaları değerlendirsin.
- Körleme tam değil (yukarıda beyan ettim).
- `deprecation-and-migration` skill'inin "Churn Rule" (kaldırılan kodun sorumluluğu) bölümünü uyguladım mı? **Hayır**: iskelet silinirken kimin neyi geri taşıyacağını tanımlamadım. Eksik.

**Kova ve ön-kayıt:**

| Ä°ddia | Kova |
|---|---|
| 1–11 (envanter, çakışma, grafik, layout, middleware, renk, menü, sayfa, test, git, noindex) | **[A]** |
| T1–T6'nın ölçülebilir çıkışları | **[A]** |
| "Çift sidebar" ve "dark bozulur" (kod okuması, görsel doğrulama yok) | **[A]** ama **doğrulanmadı** → T2/T5 sonrası Playwright |
| T0 menü türetme kararı; T7 silme zamanı; iskeleti çöpe atma alternatifi | **[C]** |
| Taşıma sonrası müşterinin "ilk 10 sn" davranışı | **[B]** (aşağıda) |

**[B] Ön-kayıt 1 — taşıma müşteri akışını bozmaz**
- **İddia:** Taşıma sonrası (T4–T6) `/panel` ana sayfasında müşterinin "Radara Ekle" butonuna ulaşma süresi taşıma öncesinden **daha uzun olmaz**.
- **Test:** Aynı 3 senaryo (giriş → ana sayfa → Radara Ekle), taşıma öncesi/sonrası, **n = 5 kullanıcı** (iç ekip dışı; yoksa ihsan'ın 3 pilot müşterisi), tıklama sayısı ve süre.
- **Eşik:** Sonrası, öncesine göre **en fazla %10** yavaşsa ve tıklama sayısı **artmıyorsa** kazanır; aksi halde **FARK YOK, mevcut `/panel` korunur, T7 yapılmaz**.

**[B] Ön-kayıt 2 — yeni yerleşim bilgiyi bulmayı kolaylaştırır**
- **İddia:** İskeletin KPI → grafik → harita → tablo sırası, mevcut KPI+buton sırasına göre müşterinin "kredi bakiyem ne?" sorusunu **daha hızlı** yanıtlatır.
- **Test:** Aynı 5 kullanıcı, tek soru ("bakiyeni bul"), iki yerleşim rastgele sırayla (within-subject), süre.
- **Eşik:** Yeni yerleşimde medyan süre eskisinden **en az %20 kısa** ise kazanır; **altındaysa FARK YOK, mevcut korunur** (görsel güzellik karar vermez).

**Karar kapıları (PO) [C]:** (1) T0: iskelet menüsü `NAV_ITEMS`'tan türetilsin mi? (2) T7: iskelet ne zaman silinsin? (3) İskeleti çöpe atıp `components/panel` üstüne sıfırdan bileşenleştirme alternatifi değerlendirilsin mi?

---

#### 6. Ek: i18n kütüphane ölçümü + boş yuva ölçümü (ihsan'ın 21.10 04:18 talebi, kod yok, yalnız ölçüm)

**Soru (ihsan, §4.10 alt başlık 6 ve 9):** "frontend-web'de yalnız `html lang=tr` var, i18n kütüphane ölçümü yap" ve "boş yuva listesi".
Betikler: `_tmp/i18n_olcum.py`, `i18n_metin_say.py`, `aksan_olcum.py`, `yuva_olcum.py` (çıktı `data/_tmp/*.txt`).

**i18n [A] ölçülen:**

| Ölçüm | Sonuç |
|---|---|
| Kurulu ✅ ✅ â â Ã¢ÂÂ Ã¢ÂÂ i18n paketi (`next-intl`, `next-i18next`, `react-i18next`, `i18next`, `react-intl`, `@lingui/core`) | **HiÃÂ§biri yok** (`package.json` + `node_modules/next-intl` yok) |
| Dil izi | YalnÄ±z `app/layout.tsx:22` `<html lang="tr">`. `useTranslations`/`locale` kullanÄ±mÄ± **0** (ihsan'Ä±n tespiti doÄru) |
| Sürümler | `next 16.4.1`, `react ^19.3.1` |
| `next-intl` uyumu (npm registry, ağ) | `latest 4.14.9`, MIT, `peerDependencies.next` aralığı `^16.0.0` dahil, sürüm uyumsuzluğu **engel değil**. Bağımlılık sayısı **10** (`@swc/core`, `@parcel/watcher` dahil; ikisi native, build süresi etkisi **ölçülmedi**) |
| Panel metin hacmi (yaklaşık, regex ile) | `app/panel` **26** · `components/panel` **29** · `app/panel-tasarim` **35** benzersiz kullanıcı metni, toplam **~90** sözlük anahtarı adayı (13 iskelet menü etiketi bunun içinde) |
| Aksansız TR kelime (sözleşme 888. satır: "hata sayılır") | **12 eşleşme**, 4 dosya: `app/panel/page.tsx` 8 (`Canli`, `Sirket`, `Eslesme`), `cuzdan/page.tsx:22` 1 (`Cuzdan`), `panel-sidebar.tsx:27,136` 2 + `yukselt-modal.tsx:16` 1 (`Yukselt`). **Yanlış pozitif olabilir**; tek tek doğrulanmadı |

**Okuma [A]:** Sözlüğe geçiş maliyeti küçük (~90 anahtar). Engel kütüphane değil, **aksansız metinler**: çeviri öncesi düzeltilmezse yanlış yazım iki dile de taşınır. `next-intl` için yalnız "peer aralığı uygun" diyorum; **kurulum ve derleme denemesi yapılmadı** (D-420: kod yok), "çalışır" demiyorum.

**i18n [C] PO kararı:** Kütüphane seçimi (`next-intl` mi, bağımlılıksız kendi `tr.json`/`en.json` + `t()` mi) tercihtir, ölçüm karar vermez. Kendi `t()` için ~90 anahtar bağımlılık getirmez ama çoğul/tarih biçimini elle yazmak demektir; sayı/para için `Intl` tarayıcıda zaten var, kütüphane gerektirmez.

**Boş yuva ölçümü (alt başlık 9) [A]:** Gerçek `/panel`'de şu an boş/`null` kutu: **1**, `app/panel/page.tsx:57` `<KpiKart baslik="Profil Inceleyenler" deger={null} />`. `KpiKart` zaten `null` için "—" ve eşik altı için "< 20" gösteriyor (`kpi-kart.tsx:21,31`): **boş yuva davranışı gerçek panelde zaten tanımlı**. İskeletin `kabuk-iskelet` shimmer'ı ayrı bir görsel dil. API alanı olarak yalnız `scored_companies` ve `total_active_signals` var (`lib/api.ts:6-7`); `fark`, `kalan gün`, `bu ay getirisi` alanları **kodda hiç tanımlı değil** (ihsan'ın "şu an null" tespitindeki "null", aslında "alan yok").

**Ayrıştığım nokta [C]:** İhsan 9. alt başlıkta "boş yuva listesi" istiyor. Ölçümüm gerçek panelde **tek** boş yuva ve tanımlı davranış gösteriyor. Yeni yuvalar iskeletteki gibi shimmer ile "bekleniyor" mu desin, yoksa `KpiKart`'ın "—" davranışına mı bağlansın? Görsel dil tercihi, PO kararı.

**Doğrulanmadı:** 12 aksansız eşleşmenin kaçı gerçek hata (tek tek açıp bakmadım). `next-intl` kurulumu denenmedi. "~90 anahtar" regex yaklaşımıdır: JSX içindeki `{...}` ifade metinleri sayılmıyor, **alt sınır** sayın.

---

## 5. Derleme (ihsan, 2026-10-21, MUSTERI-PANEL-TASARIM-01)

> **Sonuç:** 8 gerçek çelişki → 3 kapalı, 5 açık. Açık 5, **5 PO kararına** iner (K1-K5). Ölçüm yalnız K4'te taraf tutuyor; K1, K2, K3, K5 **TERCİH — ölçüm karar vermiyor**. Oylama yok, ağırlıklı puan yok (D-253/D-395). Kaynak: [`MUSTERI_PANEL_IDDIA_DEFTERI.md`](MUSTERI_PANEL_IDDIA_DEFTERI.md) §2.12, §3.1-3.3 (Kova A: 27 kapalı, 2 açık).

### 5.1 Çelişki matrisi (yalnız gerçek çelişki)

| # | Konu | Biri der ki | Öteki der ki | Kova | Nasıl kapanır | Durum |
|---|---|---|---|---|---|---|
| 1 | Yüzey paleti | Codex §4.7: `#0D1B2A/#10233A/#0072FF/#00FF66` | bilo + Claude: `#09111F/#131C2F/#2563FF/#22D3EE` kanonik | C | PO seçer (K1). Ölçüm: iskelet 3 koyu ton + 1 sahipsiz renk taşıyor (A25/A29/A31); iki tarafı da seçmiyor | AÇIK |
| 2 | SSOT dosyası | Claude: `design-tokens.json` + `scope.customerPanel` | utku: `responsive.css` kanonik | C (kısmen A) | K1 ile birlikte. Ölçüm: `responsive.css:283` kendisi 3. ton `#1A1A2E` taşıyor (A29) | AÇIK |
| 3 | Menü yapısı | Codex 4 grup; bilo 3 grup (sidebar tek kaynak) | utku 5 öge (yalnız var olan sayfa); ihsan §4.10 4 "Şimdi" öge | B | Ağaç testi B1/B3 (ön-kayıtlı). O güne dek D-253: olmayan sayfa görünmez | AÇIK |
| 4 | "Yakında" etiketi | utku: tut | ihsan §4.10 + salih: kaldır (hayalet menü) | C | PO (K3) | AÇIK |
| 5 | Sektör Dağılımı grafik tipi | Codex, Claude, utku: çizgi → çubuk | bilo `BRANDING_V2`: **donut** | C | PO (K5). Çizginin yanlış olduğunda 4 ajan hemfikir; çelişki yalnız yeni tipte | AÇIK |
| 6 | Taşıma sırası | Codex: Faz 0 marka önce | utku: T1-T2 şimdi; ihsan K-a: dil+sözlük önce | C | PO 21.10 K-a verdi (dil+sözlük önce). **Not:** utku T1 (token eşleme) K1'e bağlı → K1'den önce bitmez | KAPALI (K-a) |
| 7 | Rota sözleşmesi testi var mı | salih §4.9: yok / bozuk | utku + defter: 3/3 yeşil, ulaşılamayan sayfa 0 | A | Ölçüm kazandı (A9) | KAPALI |
| 8 | Mimir yeri | ihsan §4.6: sağ üst | ihsan §4.10: sağ alt (kendi içimde çelişki) | C | PO K-b: sağ alt balon (D-410). §4.5 = ihsan notu (mimir araçsız) | KAPALI |

**Çelişki sayılmayanlar (sebep):** bilo ≥44px vs salih ≥24px = farklı eşik (A26; WCAG 24, rahatlık 44, ölçülen 36px) · bilo 42 hex vs ölçülen 44 = sayım farkı (A27) · mobil menü yok = herkes aynı yönde.

### 5.2 Bağımsız teyit (aynı yön ≠ çelişki; ≠ kanıt)

| Bulgu | Kimler gördü | Ağırlık |
|---|---|---|
| Sahte trend çubukları | Codex, Claude, salih, utku, bilo | 5 ajan; ölçüm de var |
| Çizgi grafik uygun değil | Codex, Claude, utku, bilo | tip ayrımı #5'te |
| Emoji ikon → `lucide-react` | bilo, Claude, Codex | tercih, ucuz |
| "OSINT" rozeti `ai-rules.md:22-28` ile çatışıyor | Claude, salih, Codex | kural metni |
| İskelet kanonik token dışı | bilo, Claude, utku, salih (A31, A25) | ölçülü |
| Menü `<Link>` değil, URL durumu yok | Codex, salih, utku, defter (`a[href]`=0) | ölçülü |
| `#0072FF` metin olarak AA geçmiyor | salih (Node), Claude (W3C), axe-core 4.14.0 | **3 bağımsız araç, 16/16 çift, 0 sapma** — en sağlam bulgu |
| Mobilde navigasyon yok | Claude A8, salih, ihsan, gerçek tarayıcı (A23: ≤767px 0 nav + A28: 320px'te 20px taşma) | ölçülü, ekran kanıtlı |

**Bağımsızlık sınırı (dürüst):** körleme yalnız utku/yasu/mimir'e uygulandı. utku §4.10 kısmi maruz kaldığını kendisi yazdı. salih §4.9 Codex/Claude'u görerek yazdı. yasu bağımsızlığı doğrulanmadı. mimir oturumu araçsız, §4.5'i yazamadı → §4.5 ihsan notu, bağımsız görüş sayılmaz → C4 için bağımsız girdi yok. Codex+Claude kurgu gereği bağımsız. Aynı yönde 5 ajan = 5 kanıt değil; kanıt sütunu "ölçülü" yazanlar.

### 5.3 İddia sahibini yanlışlayan ölçümler

| # | Kimin iddiası | İddia | Ölçüm | Sonuç |
|---|---|---|---|---|
| A7 | salih | dokunma hedefi "sınırda" | 36px; WCAG 2.5.8 eşiği 24px | GEÇER |
| A9 | salih | rota sözleşmesi kırık, test yok | test 3/3 yeşil, ulaşılamayan sayfa 0 (menüde sayfasız hedef 3 kaldı) | İDDİA YANLIŞ |
| A15 | **Claude (defter yazarÄ±)** | grafik kromu `#1E293B/#334155` yeterli | 1.16 / 1.64; non-text eÅiÄi 3:1 | **KENDÄ° Ä°DDÄ°ASI YANLIÅ** |
| A20 | salih | `vitest-axe` ihlal çıkaracak | 0 ihlal, 22 kural geçti | İDDİA YANLIŞ |
| A21 | **Claude (defter yazarı)** | `aria-current` yok (grep) | axe DOM'da 2 | **KENDİ İDDİASI YANLIŞ** — ders: grep varlığı ölçer, kural motoru davranışı ölçer |

Beşin ikisi defteri yazanın kendisi. Defter bu yüzden tarafsız sayılır: yazar kendini de yanlışlıyor.

### 5.4 PO karar paketi (en çok 2 alternatif; rakamı olmayanı ölçülmedi diye yazdım, D-395)

| K | Karar | Alternatif A | Alternatif B | Ölçüm taraf tutuyor mu? | Geri alma |
|---|---|---|---|---|---|
| **K1** | **C1 + C2 BİRLİKTE:** yüzey paleti + "OSINT" kimliği | Marka SSOT: `#09111F/#131C2F/#2563FF/#22D3EE`; OSINT rozeti kalkar. ≈10 satır palet + 1 satır rozet (`panel-kabuk.tsx:99`); iskelet 44 hex ayrıca T2'de | İskelet paleti kurumsallaşır: `#0D1B2A/#10233A/#0072FF/#00FF66`. ≈10 satır palet + `ai-rules.md:22-28` kuralı değişir (1 satır) | **TERCİH — ölçüm karar vermiyor.** İki palet de kendi başına kontrastı geçecek şekilde kurulabilir. Tek notlar: grafik slot 1 = marka birincil (A ile hizalı); `#0072FF` metinde AA geçmiyor (B seçilirse metinde yasak) | A **ucuz** (`app/manifest.ts` zaten `#2563FF`). B **orta** (ikinci marka, `manifest.ts` ile uyumsuz) |
| **K2** | **C3** yoğunluk | Sakin kurumsal, şimdi | Yoğun terminal, sonra aç/kapa düğmesi | **TERCİH — ölçüm karar vermiyor.** Karar verisi B6 (müşteri) | **Ucuz**: B sonradan eklenir |
| **K3** | Menü kaynağı + "yakında" (T0) | Sidebar tek kaynak, `NAV_ITEMS`'tan türer; "yakında" yok (D-253); üst bar yalnız global (⌘K, kredi, Mimir, avatar). Satır sayısı ölçülmedi, utku T0/T6'da çıkarır | Statik iskelet menüsü kalır, "yakında" etiketli | **TERCİH — ölçüm karar vermiyor.** İki yolda da geçerli ölçüm: menü `<Link>` olmalı (`a[href]`=0, salih düzeltme 2 `:108,148`) | A **ucuz-orta** (T6 geri alınır). B ucuz |
| **K4** | Taşıma yolu | utku dilimli: T0-T7, 8 commit, 3-4 gün (utku tahmini); 8 adımın 5'i `/panel`'e dokunmaz | Tek PR | **EVET, A lehine.** İskelet `<main>/<aside>/<header>` gerçek `layout.tsx` ile çarpışıyor, `SidebarProvider` kullanmıyor, mobil Sheet kaybolur. utku: "tercih değil mühendislik gerçeği" | A **düşük**. B yüksek (gerçek panel bozulur) |
| **K5** | Sektör Dağılımı grafik tipi (küçük) | Çubuk (Codex, Claude, utku) | Donut (bilo) | **Ölçüm yok** (sektör sayısı ölçülmedi). K1 ile aynı oturumda karar | **Ucuz** |

**C4 (Mimir yeri):** PO K-b ile sağ alt balonu onayladı. Karar istemiyorum. §4.5 mimir görüşü değil, ihsan notu (mimir oturumu araçsız; PO emri 21.10). Mimir kendi görüşünü sonradan yazarsa yeniden açılır.

**Rehberlik (ölçüm değil, maliyet ve risk):** K1 A, K2 A, K3 A, K4 A, K5 çubuk. Gerekçe yalnız geri alma maliyeti ve D-253/ai-rules uyumu; bu bir hüküm değil.

**PO kararı (21.10.2026):** K1 A, K2 A, K3 A, K4 A, K5 çubuk — HEPSİ ONAYLANDI. D-420 kapısı yalnız utku T0–T2 için kalktı (görev `MUSTERI-PANEL-TASIMA-T0T2-01`); T3+ hâlâ kapalı. `.gitattributes merge=union` kapsamı: kod değil (config), zaten append-only log'larda mevcut, `ajan-chat.jsonl` bilerek dışarıda (yerinde güncelleniyor); değişiklik yok.

### 5.5 SÄ±ra, kapÄ±, makespan

| SÄ±ra | Ä°Å | Kim | KapÄ± |
|---|---|---|---|
| 0 | K1-K5 karar | PO | Yok (D-420: onaysÄ±z kod yok) |
| 1 | T0 (K3) → T1 token eşleme (**K1'e bağlı**) → T2 iskelet 44 hex → token | utku | K1, K3 |
| 1 | K-a dil + sözlük | ihsan | PO verdi |
| 1 | A30 yeniden ölç (aktif öge koordinatı doğrulanmadı, hipotez) | salih | Yok |
| 2 | **Üst kapı:** ≤767px navigasyon + 320px 20px taşma (A23/A28) | utku | Müşteriye gösterilmeden önce |
| 2 | K-1..K-5 kapÄ±larÄ± (rota testi `panel-tasarim`'i taramalÄ±, axe, kontrast, durum matrisi, reduced-motion) | salih | T2 sonrasÄ± |
| 3 | T3-T6 | utku | K-1..K-5 yeÅil |
| 4 | A19 performans: **üretim build + dolu içerik + bir filtre** (dev + boş iskelet = yalnız alt sınır: TTFB 94 ms, FCP 208 ms) | salih (utku doldurunca) | Faz B dolu |
| 5 | B1 ağaç testi, ön-kayıtlı | ihsan + PO | ≥3 müşteri (K-d) |
| 6 | T7 eski bloğu bayrakla kapat, 1 hafta sonra `git rm app/panel-tasarim` | utku | PO zamanı seçer |

**Makespan:** kritik yol = PO kararı → T1 → T2 → T3-T6 → T7. utku tahmini 3-4 gün; sapma aralığını **hesaplamadım** (Monte Carlo yok, veri yok). Paralel dallar kritik yolu uzatmaz: K-a, A30, K-1..K-5.

**Kova A'da kalan açık 2:** A19 (üretim build bekliyor) · A30 (hipotez). A23, A24 kapandı: gerçek tarayıcı, salih §2.12, 5 PNG `data/orchestrator/SALIH_EKRAN_panel-tasarim_*px_2026-10-21.png`.

**Güvenlik notu:** `middleware` matcher `['/', '/panel/:path*']` `/panel-tasarim`'i dışarıda bırakıyor → 3 host'ta girişsiz açık, yalnız noindex. Gerçek müşteri verisi girmeden matcher'a eklenmeli (utku).

### 5.6 Rapor (D-407)

**1. SIRADAKÄ° ADIM:** PO K1-K5'i verir. OnaysÄ±z kod yok.

**2. STRATEJİK ADIM:** Önce marka paleti + menü kaynağı (K1, K3), sonra dilimli taşıma. Mobil navigasyon müşteri görmeden önce kapanır. Menü ağacı müşteri ağaç testiyle netleşir.

**3. YAPILMASI GEREKENLER:**
- PO: K1-K5 karar
- salih: A30 yeniden ölçüm
- utku: onay sonrasÄ± T0-T2 (Åimdi bekler)

### 5.7 Öz-eleştiri (D-406)

Evet, kayırma riski var: §4.6 taslağım "sakin kurumsal, yoğun sonra" idi ve K2'de aynı yönü öneriyorum; bunu "ölçüm karar vermiyor" diye etiketledim ve gerekçeyi yalnız geri alma maliyetine bağladım, ayrıca kendi Mimir iç çelişkimi (#8) matrise kendi satırım olarak yazdım.

## 6. Lisans notu (Open Design ve OpenCode)

| Konu | Durum |
|---|---|
| Open Design | Apache-2.0 (`open-design/LICENSE`). Açık kaynaktır. Kullanım için izin/ücret gerekmez. |
| Lisans ne zaman devreye girer? | Yalnız dosya/kod KOPYALAYIP dağıtırsak: lisans kopyası + telif notu + değişiklik notu korunur. Fikir/renk/yerleşim ilham almak lisans yükümlülüğü doğurmaz. |
| Paket içi istisnalar | `guizang-ppt`, `html-ppt`, `web-clone` MIT; bazı design-systems paketleri kendi `LICENSE`/`manifest.source` dosyasını taşır. Paket bazında bakılır. |
| Marka uyarısı | Marka adı anan design-system paketleri "estetik ilham"dır, resmî marka varlığı değildir (`design-systems/README.md`). Marka logosu/adı kullanılmaz. |
| OpenCode (Bilo'nun aracı, D-422) | Açık kaynak MIT olarak biliniyor; bu repoda lisans dosyası doğrulanmadı. Araç kullanımı bizden lisans istemez; ürün koduna girmez. |

## 7. Türkiye OSB haritası (PO talebi 21.10, ihsan taslağı)

**İstek:** müşteri paneline etkileşimli Türkiye haritası. OSB'ler nokta; yan listede "yeni açılacak OSB parselleri". Google Maps şart değil. Open Design yalnız ilham (PO onayı 21.10).

| Konu | Karar / durum |
|---|---|
| Kapsam (ilk tur) | Yalnız `osbs` tablosundaki **15 Ankara OSB**. Türkiye geneli sonra. |
| Nokta kaynağı | OSBÜK dizini (`osbuk`) `scrape=False`: kazıma YOK. Önce site sahibinden izin; o zamana dek mevcut master. |
| Koordinat | `osbs`'te kolon doğrulanmadı. yasu ölçer; kaynaksız koordinat uydurulmaz. |
| Yeni açılacak parseller | Kaynak YOK. Liste boş, `ORNEK` etiketli yuva. `companies.osb_parcel` (firma parseli, %0,2 dolu) bu liste DEĞİL. |
| Görsel yol (A, hafif) | Türkiye TopoJSON/SVG + nokta katmanı (recharts yanında, D-375 uyumlu). Zoom/sokak gerekmez. |
| Görsel yol (B, ağır) | MapLibre + deck.gl. Parsel poligonu gelirse, tile kaynağı ücretsiz doğrulanınca (D-373). |
| Open Design | YalnÄ±z renk/kart/boÅ durum ilhamÄ±. Kopya olursa Apache-2.0 lisans + telif + deÄiÅiklik notu. |

```
┌──────────────────────────────┬─────────────────────┐
│ TÜRKİYE HARİTASI             │ YENİ AÇILACAK       │
│   ● ●  ← OSB noktaları       │ PARSELLER [ORNEK]   │
│   (tıkla → OSB kartı)        │ Veri kaynağı        │
│ [Filtre: il / durum]         │ bekleniyor          │
└──────────────────────────────┴─────────────────────┘
```

| Görev | Ajan | Çıktı |
|---|---|---|
| `VERI-OSB-HARITA-01` | yasu | Koordinat ölçümü + OSBÜK izin taslağı + parsel kaynağı raporu |
| `MUSTERI-PANEL-HARITA-01` | utku | `/panel-tasarim` içinde boş harita yuvası (yol A), DOLGU YOK |

**Öz-eleştiri:** OSBÜK'ü kazımak hızlı olurdu ama izinsiz. Parsel listesini doldurmak uydurma olurdu. Koordinat kolonunu henüz kendim ölçmedim.

## 8. Analiz yöntemi ve iddia defteri (Claude ajanı, 2026-10-21)

Bu belge **görüş toplar**; görüşlerin nasıl analiz edileceği ayrı belgededir:

**[[Huginn Data Insights/docs/MUSTERI_PANEL_IDDIA_DEFTERI]]** — iddia defteri + Kova A ölçümleri.

| Ne içerir | Özet |
|---|---|
| **Yöntem** (§1) | Oylama ve ağırlıklı puan matrisi **reddedildi** (gerekçeli). 3 kova: **A** bugün ölçülebilir · **B** müşteri verisi gerekir · **C** tercih, PO kararı. Ön-kayıt kuralı (eşik ölçümden önce yazılır) + körleme kuralı |
| **Kova A ölçümleri** (§2) | `npm test` 77/77 yeşil · 13 kontrast çifti · 6 palet koşusu · a11y grep envanteri · hedef boyutu · responsive eşikler · rota envanteri · `vitest-axe` sürüm uyumu |
| **İkinci doğrulama** (§2.11) | PO talebi: **axe-core 4.14.0 kendi kontrast motoru** (Deque, ayrı kod tabanı) → 16 çiftte **16 tam isabet, 0 sapma** · **axe kural taraması** → **0 ihlal, 22 kural PASS** |
| **Ekran kanıtı** (§2.12, salih) | Gerçek tarayıcı: **320/375px'te 0 nav öğesi** · **20px yatay taşma** (WCAG 1.4.10) · `body`=`#1A1A2E` · ekranda **4 çakışan koyu ton** · 5 PNG |
| **İddia defteri** (§3) | §4.6–§4.9'daki iddialar kovalara atandı: **Kova A 27 kapalı / 2 açık** (A19 perf · A30 aktif öğe), Kova B 6 ön-kayıt bekliyor, Kova C 4 PO kararı |
| **Süreç + prompt** (§4, §5) | Ajan başına kör prompt (utku/yasu/mimir) + ihsan derleme promptu |

**Ölçümün iddia sahibini yanlışladığı 5 nokta** (defterin kendi kendini düzeltme kanıtı — **ikisi defteri yazanın kendi iddiası**):

| # | İddia | Ölçüm | Sonuç |
|---|---|---|---|
| A7 | "dokunma hedefi sınırda" (§4.9) | 36px, eşik 24px | **geçersiz** — rahat PASS |
| A9 | "rota sözleşmesi kırık, test yok" (§4.9) | `rota-sozlesmesi.test.ts` **3/3 yeşil**, erişilemeyen sayfa **0** | **geçersiz** — kapı kapanmış |
| A15 | grafik kromu `#1E293B`/`#334155` (**§4.8b, kendi önerim**) | 1.16 / 1.64 — non-text 3:1 **FAIL**; axe-core da teyit etti | **kendi önerim yanlış** |
| A20 | "a11y ihlalleri var, `vitest-axe` boşta" (§4.9) | axe: **0 ihlal, 22 kural PASS** | **geçersiz** — iskelet yapısal olarak temiz |
| A21 | "`aria-current` yok" (**§2.5, kendi iddiam**) | axe DOM sayımı: **2 adet var** | **kendi iddiam yanlış** |

A21 dersi: grep **varlık** ölçer, kural motoru **davranış** ölçer. `aria-current={aktif ? 'page' : undefined}` koşullu ifadesi grep envanterime düzgün yansımamış.

**İkinci doğrulamanın en büyük sürprizi:** iskelet yapısal erişilebilirlikte **temiz**. `heading-order`, `landmark-unique`, `aria-hidden-focus`, `nested-interactive`, `button-name` — en sık ihlal edilen kurallar hepsi geçti. utku'nun `aria-label` disiplini işe yaramış. Eksikler yapısal değil **davranışsal**: `aria-busy` 0, `a[href]` 0 (navigasyon URL üretmiyor), skip-link yok.

**Teyit edilen:** salih'in 4 kontrast ölçümü **üç bağımsız kaynakta** tam isabet (salih / benim W3C formülüm / axe-core Deque motoru — fark 0.00). Nüans: üç mavi çift normal metinde FAIL, **büyük metinde (≥24px / ≥18.66px bold) 3:1 ile PASS**.

**Ortak kör nokta KAPANDI.** Bu bölümü ilk yazdığımda *"beş ajanın hiçbirinin ekran kanıtı yok"* demiştim; `npm run dev`/`curl`/`launch.json` benim oturumumda izin engelliydi. salih §2.12'de gerçek tarayıcıyla ölçtü ve **5 PNG** üretti. A23 + A24 kapandı, 5 yeni bulgu (A28–A32) çıktı.

Açık kalan 2: **A19** perf (dev+dolgusuz ölçüm 13.8 ms geçer ama production build + dolgu sonrası tekrarı şart; filtre yanıtı **ölçülemez — filtre yok**) · **A30** yan bar aktif öğe kontrastı (salih'in öz-eleştirisi: koordinat doğrulanmadı, **hipotez düzeyinde**).

**En ağır tek bulgu:** 320/375px'te **0 navigasyon öğesi + 20px yatay taşma**. Benim §2.7 sınıf okumam doğruydu ama yarım — taşmayı görmemiştim. İki WCAG ihlali birlikte; mobil müşteri ürünü kullanamaz.

**A25 + A29 + A31 aynı kökten:** ekranda `#0D1B2A` · `#10233A` · `#1A1A2E` · `#B9C6D4` = **4 çakışan/tanımsız ton**, niyet 2 tondu. Bu A18'in (panel hiçbir SSOT kapsamında yok) ölçülmüş maliyeti. **C1 palet kararı acil** — gecikirse her yeni dosya ton sayısını artırır.

## Ilgili Nodlar

- [[Huginn Data Insights/docs/MUSTERI_PANEL_IDDIA_DEFTERI]] — analiz yöntemi + ölçülmüş kanıt hanesi + ajan promptları
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
- [[Huginn Data Insights/plans/brief_utku_MUSTERI-PANEL-TASARIM-01]]
- [[Huginn Data Insights/plans/brief_utku_MUSTERI-PANEL-HARITA-01]]
- [[Huginn Data Insights/plans/brief_yasu_VERI-OSB-HARITA-01]]
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/docs/brand/ai-rules]] — "Startup Intelligence Platform, not OSINT Tool"; §4.8/2 ihlal bulgusu buradan
- [`docs/brand/design-tokens.json`](brand/design-tokens.json) — marka SSOT (JSON, wikilink değil); §4.8 palet çatışmasının kaynağı, `scope.customerPanel` eklenmeli
