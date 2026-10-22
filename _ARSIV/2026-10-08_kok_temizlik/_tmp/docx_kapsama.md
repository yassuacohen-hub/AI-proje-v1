# docx → strateji belgeleri kapsama denetimi (mekanik, grep)

Kaynak: `yedekler/Altyapı alan adı pazarlama stratejimiz.docx` → `_tmp/docx_metin.txt` (1774 paragraf, `N|metin`).
Hedef: `Huginn Data Insights/docs/strateji/*.md` (9) + `docs/brand/brand.md`.
Durum: KAPSANDI / KISMİ / EKSİK / SİLİNDİ (bilerek, STRATEJI_05 §4 L51).

| # | docx satır | konu | eşleşen belge §bölüm | durum (önce) | durum (sonra) |
|---|---|---|---|---|---|
| 1 | L5–21 | domain satın alma sırası | 01 §5 | KAPSANDI | KAPSANDI |
| 2 | L23–27 | SaaS kurgusu, tek domain | 00 §1 | KAPSANDI | KAPSANDI |
| 3 | L30–39 | ana sayfa: "2 Milyon+", 3 arama, "10 Kredi ile Aç", "Kendi Firmanı Ekle" | 07 §2.4 | KISMİ ("2 Milyon+" sayaç yok) | KAPSANDI (07 §2.4 iddia notu) |
| 4 | L41–47 | abonelik+kredi hibrit: 500 kredi/ay, AI risk 50, konşimento 20, Ek 100 | 07 §2.3, 03 §4.1 | KISMİ (konşimento) | KISMİ — gümrük/konşimento veri kaynağı yok (D-310 katman dışı), rapor eklenmez |
| 5 | L49–59 | `/sinyaller`, `/rakip-takibi`, Daily Digest e-posta | — | EKSİK | KAPSANDI (07 §2.3 satır) |
| 6 | L61–67 | çift taraflı pazar, UGC SEO | 06 §1, §4.2 N4 | KAPSANDI | KAPSANDI |
| 7 | L69–73 | 3 aşama yol haritası | 04 §4.1 | KAPSANDI | KAPSANDI |
| 8 | L76–105 | dashboard 4 KPI | 07 §2.3 | KAPSANDI | KAPSANDI |
| 9 | L106–127 | ihale dashboard 5/50 kredi; iş ilanı sinyali (Kariyer.net/LinkedIn) | 07 §2.6 | KISMİ (iş ilanı sinyali) | KAPSANDI (07 §2.6 satır + PO B33) |
| 10 | L131–152 | SEO ana sayfa ihale, "butik dijital dedektiflik" | 07 §2.6, 00 §4 | KAPSANDI | KAPSANDI |
| 11 | L154–158 | kurulum sırası | 04 §4.1 | KAPSANDI | KAPSANDI |
| 12 | L163–174 | kapasite dashboard 15 kredi, hurda | 07 §2.1, 06 §2.5 | KAPSANDI | KAPSANDI |
| 13 | L176–182 | `/atil-kapasite/`, `/hurda-malzeme/` dizinleri | 00 §4 | KISMİ (`/hurda-malzeme/`) | KAPSANDI (00 §4 not: ayrı dizin değil, kategori) |
| 14 | L184–193 | 3 iterasyon; vergi levhası doğrulama; iletişim 50 kredi | 06 §3 (Mersis), 03 §9.2 B23 | KISMİ (vergi levhası) | KAPSANDI (06 §3 satır) |
| 15 | L199–243 | programatik SEO 100.000 sayfa/gün, AI 1-2 cümle özet, SSR, uydu no-index | 04 §4.3, 06 N4, 01 §4 | KISMİ (100.000/gün iddia; AI özet) | KAPSANDI (04 §4.5 satır) |
| 16 | L244–277 | uydu SEO ağı (çoklu site) | 05 §4 L51, 01 §7 | SİLİNDİ | SİLİNDİ |
| 17 | L281–307 | SSO/JWT/Masterpass | 05 §4 L51 | SİLİNDİ | SİLİNDİ |
| 18 | L308–320 | PR endeks, bülten, CAC≈0, spin-off exit | 00 §4.1 | KISMİ (spin-off exit) | KISMİ — exit/yatırım stratejisi ürün belgesi kapsamı dışı |
| 19 | L322–336 | riskler: duplicate/PBN, KVKK ticari sır maddesi, Residential Proxy maliyet 4-5×, sahte ilan | 01 §3, 06 §3 | KISMİ (ticari sır; proxy maliyeti) | KAPSANDI (03 §4.2 madde, 03 §9.2 not) |
| 20 | L338–383 | karşılaştırma + Kontrollü Hibrit | 01 §2, §4 | KAPSANDI | KAPSANDI |
| 21 | L383–418 | hibrit kazançları | 01 §4 | KAPSANDI | KAPSANDI |
| 22 | L422–463 | sayfa içi kanca 10/20/15 + 3 altın kural | 07 §2.1, §2.2 | KAPSANDI | KAPSANDI |
| 23 | L469–496 | AI rapor 5/25/50, Ankara örneği | 03 §9.2 B23 | KAPSANDI | KAPSANDI |
| 24 | L499–535 | JSON-LD paywall | 06 §5.5, 00 §4 | KAPSANDI | KAPSANDI |
| 25 | L540–550 | kredi politikası 1/3/5/200/300 | 03 §9.2 | KAPSANDI | KAPSANDI |
| 26 | L552–602 | 4 tier matris | 03 §9.1 | KAPSANDI | KAPSANDI |
| 27 | L604–613 | sınırsız API 12 ay + 2.000 USD depozito | 03 §9.3 | KAPSANDI | KAPSANDI |
| 28 | L616–629 | eleştiriler: 60/dk 5.000/gün, 720+480, 300 kredi iade | 03 §9.3, §9.4 | KAPSANDI | KAPSANDI |
| 29 | L630–668 | checkout: SSL, kart saklama → top-up %40, GİB, %95 şirket kartı | 03 §9.4.1 | KISMİ (%40, %95 iddia) | KAPSANDI (03 §9.4.1 satır) |
| 30 | L670–681 | iyzico hosted, 3D Secure, webhook alanları (`plan_type` …) | 03 §9.4.1, 05 §4 #1 | KISMİ (alan adları) | KISMİ — alan adları `ALTYAPI-ODEME-WEBHOOK-01` tasarımında; belgeye şema yazılmaz |
| 31 | L683–686 | havale `HUGIN-API-9482` | 03 §9.4.1 | KAPSANDI | KAPSANDI |
| 32 | L688–718 | veri kaynakları: TOBB TSG, İTO Şirket Kartı, KAP, KYB, UBO | 03 §4.2 m.1, brand L83 | KISMİ (İTO/KAP/KYB) | KAPSANDI (03 §4.2 not + PO B31) |
| 33 | L721–742 | 5 ürün: UBO ağ, imza alarm, NACE/bölge yoğunluk matrisi, sağlık/yaş skoru, Fraud API | 05 §4 #5/5b/5c | KISMİ (yoğunluk matrisi; sağlık/yaş skoru) | KAPSANDI (05 §4 satır) |
| 34 | L745–759 | yol haritası: TOBB TSG fiyat, Neo4j, MVP doğrulama+alarm | 05 §4 #5 | KISMİ (Neo4j kararı) | KAPSANDI (05 §5 satır) |
| 35 | L762–812 | feature-based pricing, gateway, scope, 4 endpoint, 403, OpenAPI, Stripe metered | 02 §4.1/4.2, 00 §4 | KAPSANDI (Kong kısmı SİLİNDİ) | KAPSANDI |
| 36 | L815–826 | API 3 aşama, `GET /v1/companies/{vkn}/tenders` | 02 §4.1 | EKSİK | KAPSANDI (02 §4.1 satır + PO B32) |
| 37 | L828–845 | 4 risk; kaynak maliyeti ≤ %20 satış fiyatı; SLA iade | 03 §9.4 | EKSİK (≤ %20 kuralı) | KAPSANDI (03 §4.1 satır) |
| 38 | L848–916 | API paket matrisi 30/60/120/60 | 03 §9.1 | KAPSANDI | KAPSANDI |
| 39 | L917–945 | 4 eleştiri: Mırmır, Dijital Ayak İzi 30, GİB, Enterprise 2.720 | 03 §9.2, §9.3 | KAPSANDI | KAPSANDI |
| 40 | L948–1015 | fraud-check istek/yanıt şeması, FRD kodları | 02 §4.1, §4.4, 05 #5c | KISMİ (yanıt alanları) | KISMİ — şema `API-FRAUD-CHECK-01` tasarımında; kodlar 02 §4.4'te |
| 41 | L1017–1038 | panel modalları | 07 §2.5 | KAPSANDI | KAPSANDI |
| 42 | L1043–1079 | JSON-LD "HuginInsight AI" | 06 §5.5, 01 §3 (marka yazımı) | KAPSANDI | KAPSANDI |
| 43 | L1081–1101 | SLA taslağı: unvan, %99.9, kaynak kesintileri hariç, 429, KVKK, ham veri yasağı | 03 §9.4, §4.2 m.6 | KISMİ (kaynak kesintileri; unvan) | KAPSANDI (03 §9.4 satır + PO B34) |
| 44 | L1103–1136 | iyzico webhook: imza, idempotency, +30 gün, `payment_history` | 03 §9.4.1, 05 §3, #1 | KISMİ (+30 gün, tablo adı) | KISMİ — `kredi_hareket` zaten var; süre uzatımı görev tasarımında |
| 45 | L1138–1206 | net kâr formülü bileşenleri → 41,25 ₺ %27,5 | 03 §9.3 B21, 05 #6 | KISMİ (bileşenler) | KAPSANDI (03 §9.3 satır) |
| 46 | L1208–1226 | 4 kategori A–D | 06 §2.1 | KAPSANDI | KAPSANDI |
| 47 | L1230–1261 | dinamik havuz | 06 §2.3 | KAPSANDI | KAPSANDI |
| 48 | L1263–1290 | hacim kademeleri, Data Room/VIP | 06 §2.3, 07 §2.8 | KAPSANDI | KAPSANDI |
| 49 | L1292–1296 | ilan büyüme: 5→3, TÜRMOB/Luca modülü, EKAP/DMO talep | 06 §2.5 | KISMİ (TÜRMOB/Luca) | KAPSANDI (06 §2.5 satır) |
| 50 | L1298–1307 | Kategori E | 06 §2.1 | KAPSANDI | KAPSANDI |
| 51 | L1309–1371 | ilan kartı wireframe (`HGN-98421`, gösterim sayacı) | 06 §5.5, §2.2 | KISMİ (gösterim sayacı) | KISMİ — UI detayı, `PY-F*` görev tasarımında |
| 52 | L1373–1384 | AI tags Elasticsearch/SQL, JSONB | 06 §2.1, §5.1 | KISMİ (Elasticsearch) | KAPSANDI (06 §6 satır) |
| 53 | L1386–1400 | 6 kategori, F→G eşiği 20 | 06 §5.3 | KAPSANDI | KAPSANDI |
| 54 | L1402–1407 | "İlk İlana 3 Kredi" | 06 §2.4 | KAPSANDI | KAPSANDI |
| 55 | L1409–1447 | `business_rules` JSON + SQL | 06 §2.3, §5.2 | KAPSANDI | KAPSANDI |
| 56 | L1450–1484 | GTM 3 aşama: OSB listeleri, WhatsApp, SMS, "KOBİ Mağazası", mali müşavir, KPI | 04 §4.2, §4.5, 06 §2.5 | KISMİ (OSB adayları; KOBİ Mağazası) | KAPSANDI (04 §4.2 satır) |
| 57 | L1488–1597 | Node/TS cüzdan kodu | 05 §4 L51 | SİLİNDİ | SİLİNDİ |
| 58 | L1599–1646 | iç linkleme şablonu | 04 §4.3, 06 §2.4 | KAPSANDI | KAPSANDI |
| 59 | L1649–1702 | recursive CTE UBO, D3/Vis.js | 05 #5 | KISMİ (D3/Vis.js) | KISMİ — görselleştirme kütüphanesi `VERI-UBO-ZINCIR-01` tasarımında; yeni bağımlılık kararı PO |
| 60 | L1704–1763 | EKAP scraper kodu | 05 §4 L51 | SİLİNDİ | SİLİNDİ |
| 61 | L1765–1773 | yönetici özeti | 00 §1 | KAPSANDI | KAPSANDI |

## Sayım

| durum | yama öncesi | yama sonrası |
|---|---|---|
| KAPSANDI | 32 | 47 |
| KISMİ | 22 | 7 (gerekçeli: 4, 18, 30, 40, 44, 51, 59) |
| EKSİK | 3 | 0 |
| SİLİNDİ | 4 | 4 |
| toplam | 61 | 61 |

## Yama doğrulaması (findstr, yama sonrası)

Yeni terimler strateji belgelerinde bulundu: Daily Digest (07 L39), 2 Milyon (07 L44), Kariyer.net (07 L62), `/tenders` (02 L45), %20'si (03 L48), İTO Şirket Kartı (03 L52), Residential (03 L130), kurumlar vergisi (03 L146), MERNİS (03 L152), 100.000 sayfa (04 L79), Neo4j (05 L64), Elasticsearch (06 L232), hurda-malzeme (00 L44), B31–B34 (PO L55–58). Türkçe karakterli terimler (İvedik, KOBİ Mağazası, TÜRMOB, vergi levhası, yoğunluk matrisi, ticari sır) cmd `findstr` kodlamasında eşleşmedi; `apply_diff` sonucu "modified" ile doğrulandı.

Yamalanan: 00 §4; 02 §4.1; 03 §4.1, §4.2 m.1/m.3, §9.2, §9.3, §9.4, §9.4.1; 04 §4.2, §4.5; 05 §4, §5; 06 §2.5, §3 #1, §6; 07 §2.3, §2.4, §2.6; PO B31–B34.

## Gözlem

- STRATEJI_07 başlıklarındaki docx satır referansları (L843–925, L2033–2075, L2415–2897, L3197–3291) `_tmp/docx_metin.txt` numaralamasını (1774) aşıyor; farklı çıkarım (muhtemelen `alan adı.txt` / satır kırılmalı). Düzeltme bu işin kapsamı dışı.
- `yedekler/alan adı.txt` docx ile aynı değil; docx esas alındı.
