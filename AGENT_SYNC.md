# AGENT_SYNC — Otomatik Olusturuldu (task_board'dan)

> Son guncelleme: 2026-09-10T20:05:00
> Kaynak: data/orchestrator/task_board.json

## ÔÜí Frontend/Web Oturumu ├ûzeti (2026-09-10, dashboard ajan─▒) ÔÇö DI─ŞER AJANLARA ├ûNEML─░

Bu oturumda web dashboard'a **uyelik/oturum sistemi** eklendi; tum endpoint'ler ve sema degisti:

- **┼Şifre sistemi:** users tablosuna `password_hash` (PBKDF2-SHA256, 120k iter, `pbkdf2$iter$salt$hash` format─▒). Kay─▒t art─▒k ┼şifre zorunlu (min 8); login ┼şifre do─şrulamal─▒. Yeni endpoint: `POST /api/buyer/logout`, `POST /api/buyer/change-password`. Eski hash'siz kay─▒tlar i├ğin ge├ği┼ş istisnas─▒ var.
- **Yeni users kolonlar─▒ (migration 0014 + 0015, her iki DB'de):** `employee_range, certificates, tax_number, phone, trade_name, address, password_hash`. `GET/PUT /api/buyer/profile` bunlar─▒ i┼şler; profil_tamlama **10 alan** ├╝zerinden.
- **Yeni admin API'ler:** `GET/POST /api/admin/categories` (product_categories CRUD; 409 code ├ğak─▒┼şmas─▒) ÔÇö `require_admin`.
- **Bugfix'ler:** toggleWatchDetail anahtar tutars─▒zl─▒─ş─▒ (watchKeyOf), task_board.json BOM (utf-8-sig okuma), isletmemAccountTab tip parametresi.
- **UI:** ─░┼şletmem 4 sekme (Firma Profili/Bilgiler/E┼şle┼ştirme/Hesap) + g├Âr├╝n├╝r k─▒sa bilgi kartlar─▒ + "Notlar" tek-tu┼ş kapatma; topbar ─░┼şletmem butonu kald─▒r─▒ld─▒ ÔåÆ Paket/Tier rozeti; Son g├╝ncelleme CANLI chip'ine ta┼ş─▒nd─▒; match paneline "Arama Y├Ân├╝" (Y22).
- **Admin'ler:** admin@huginn.local (┼şifre: Admin2026!) + yassuacohen@gmail.com (11223344) ÔÇö `scripts/set_admin_password.py add|set|--list` ile y├Ânetilir.
- **Panel revizesi:** X01ÔÇôX05 eklendi (a┼şa─ş─▒da), Y24/Y26 revize edildi. Dashboard canl─▒: `http://localhost:8000` (Docker) / 8010 (yerel uvicorn).
- Ajanlar users tablosuna do─şrudan yazacaksa yeni kolonlar─▒ dikkate als─▒n; DB yazan scriptler `password_hash`'e dokunmamal─▒.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum |
|-------|--------|-------|---------|-------|
| P3-2 | VKN web kazima genisle (sadece footer de | web_kazima | plan | blocked |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | P1 | blocked |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | P1 | plan |
| P6-1 | Ã„Â°Ã…Å¸ ilanlarÃ„Â± ve ÃƒÂ§alÃ„Â±Ã…Å¸an | web_kazima | P1 | cancelled |
| P7-1 | DB Migration 0007 - Job Intelligence tab | gelistirici | P0 | plan |
| P7-2 | Job Intelligence modul yapisi olusturma | mimar | P0 | plan |
| P7-5 | Ã„Â°SKUR Scraper | kazi_scraper | P1 | aktif |
| P7-6 | Kariyer.net Scraper | kariyer_scraper | P2 | aktif |
| Y21 | ARASTIRMA: ISKUR kurumsal eslestirme ver | arastirmaci |  | plan |
| Y23 | Odeme entegrasyonu (iyzico/Stripe) - oto | gelistirici |  | plan |
| Y24 | Uye e-posta dogrulama linki + Telegram h | gelistirici |  | plan |
| Y26 | Enterprise API key yonetimi + kullanim r | gelistirici |  | plan |
| X01 | ARASTIRMA: GIB VKN dogrulama (acik API + | arastirmaci | P1 | plan |
| X02 | BUG: VKN zenginlestirme (MERSIS + web fo | gelistirici | P1 | blocked |
| X05 | Y26: API key yonetimi - rotasyon + kulla | gelistirici | P2 | plan |
| GOV-01 | Orkestrasyon reconciliation denetimi ve  | koordinator | P0 | aktif |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu (10 | web_kazima | P1 | plan |
| APIFY-03 | Apify Webhook + Kalici Olay Isleme (idem | web_kazima | P1 | plan |
| MCP-01 | Kontrollu Apify MCP Erisimi: izinli arac | arastirmaci | P2 | plan |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector (ge | arastirmaci | P2 | plan |
| REL-01 | Teslimat Kapisi: CI hard-gate (lint/Band | devops | P1 | plan |
| DOC-01 | Kanonik Dokumantasyon: tek V10 kaynagi + | koordinator | P1 | plan |

## Tamamlananlar (Son 10)

| Gorev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| P8-3 | Is ilani takip motoru: buyume sinyali sk | arastirmaci | 2026-09-09 |
| P8-4 | Is ilani takip motoru: risk sinyali skor | arastirmaci | 2026-09-09 |
| P8-5 | Is ilani takip motoru: teknoloji donusum | arastirmaci | 2026-09-09 |
| P8-6 | Is ilani takip motoru: yatirim ve olcekl | arastirmaci | 2026-09-09 |
| P8-7 | Is ilani takip motoru: cografi genisleme | backend | 2026-09-09 |
| P8-8 | Is ilani takip motoru: kurumsal rapor ve | web_kazima | 2026-09-09 |
| X03 | MATCH v3: buyer profili skorlari (olcek  | gelistirici | 2026-09-09 |
| X04 | UYELIK: sifre sifirlama + kurumsal e-pos | gelistirici | 2026-09-09 |
| SEC-01 | API Guvenlik Regresyonu: admin fail-clos | gelistirici | 2026-09-10 |
| SEC-02 | Ag ve Ajan Izolasyonu: TLS verify + work | gelistirici | 2026-09-10 |
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi a | harici_arastirma | 2026-09-10 |

## Son Handoff'lar

- **P4-1**: Kalite skoru 27.5 -> ~64 tamamlandi
- **P4-4**: Dashboard performans izleme ve slow query optimiza
- **P8-8**: Kurumsal rapor ve medya entegrasyonu tasari tamaml
- **SEC-01**: web_app.py require_admin fail-closed ve CSV export
- **SEC-02**: TLS dogrulama varsayilan yapildi (verify=False kal | done: dinamik domain policy_for + workspace containment, 21 regresyon testi passed (2026-09-10)
- **SEC-03**: scripts altinda TLS verify=False/CERT_NONE temizlendi (8 script), commit 45cd8fe
- **P7-GATE**: tek migration kopyasi dogrulandi, test_job_intelligence_dikey.py dikey akis testleri (11 passed), commit 7de2abc; DATA-01/P7-GATE/SEC-01/SEC-02 panoda done (2026-09-10)
- **Y21**: ISKUR araştırması tamamlandı — public e-sub'da açık API YOK, özel sektör işyeri adları GİZLİ. P7-5 firma-eşleştirme odaklı değil, ilan metadata + aggregation intelligence odaklı çalışacak. Not: İşveren Kayıt Sorgulama authenticated erişimle SGK/VKN üzerinden firma adı üretebilir; bu yöntem aktif olursa P7-5 firma-level matching için REVİZYON yapılacak.
- **APIFY-01**: OSINT_Scraper_Motoru araştırması tamamlandı. 3 araç kıyaslandı: Apify (GO - mevcut adapter entegre edilecek, anti-bot siteler icin), Firecrawl (GO with CAVEATS - yedek opsiyon, AGPL self-host riski), Scrapy (NO for MVP - buyuk refactoring). Sonuc: `data/orchestrator/apify_research_result.json`. APIFY-02/03 baslayabilir.

## Harici Ajan Bildirimleri

| Ajan | Dosya | Durum |
|------|-------|-------|
| kariyer_scraper | `workspace/external/NOTIFICATION_Y21_P75_kariyer_scraper.md` | ✅ Bildirim yazıldı |
| kazi_scraper | `workspace/external/NOTIFICATION_Y21_P75_kazi_scraper.md` | ✅ Bildirim yazıldı |

**Not:** Kariyer.net scraper (P7-6) Y21 sonuçlarından doğrudan etkilenmez. İSKUR scraper (P7-5) authenticated erişim olursa revize edilecek.


