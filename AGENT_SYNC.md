# AGENT_SYNC — Otomatik Olusturuldu (task_board'dan)

> Son guncelleme: 2026-09-10T00:30:00
> Kaynak: data/orchestrator/task_board.json

## ⚡ Frontend/Web Oturumu Özeti (2026-09-10, dashboard ajanı) — DIĞER AJANLARA ÖNEMLİ

Bu oturumda web dashboard'a **uyelik/oturum sistemi** eklendi; tum endpoint'ler ve sema degisti:

- **Şifre sistemi:** users tablosuna `password_hash` (PBKDF2-SHA256, 120k iter, `pbkdf2$iter$salt$hash` formatı). Kayıt artık şifre zorunlu (min 8); login şifre doğrulamalı. Yeni endpoint: `POST /api/buyer/logout`, `POST /api/buyer/change-password`. Eski hash'siz kayıtlar için geçiş istisnası var.
- **Yeni users kolonları (migration 0014 + 0015, her iki DB'de):** `employee_range, certificates, tax_number, phone, trade_name, address, password_hash`. `GET/PUT /api/buyer/profile` bunları işler; profil_tamlama **10 alan** üzerinden.
- **Yeni admin API'ler:** `GET/POST /api/admin/categories` (product_categories CRUD; 409 code çakışması) — `require_admin`.
- **Bugfix'ler:** toggleWatchDetail anahtar tutarsızlığı (watchKeyOf), task_board.json BOM (utf-8-sig okuma), isletmemAccountTab tip parametresi.
- **UI:** İşletmem 4 sekme (Firma Profili/Bilgiler/Eşleştirme/Hesap) + görünür kısa bilgi kartları + "Notlar" tek-tuş kapatma; topbar İşletmem butonu kaldırıldı → Paket/Tier rozeti; Son güncelleme CANLI chip'ine taşındı; match paneline "Arama Yönü" (Y22).
- **Admin'ler:** admin@huginn.local (şifre: Admin2026!) + yassuacohen@gmail.com (11223344) — `scripts/set_admin_password.py add|set|--list` ile yönetilir.
- **Panel revizesi:** X01–X05 eklendi (aşağıda), Y24/Y26 revize edildi. Dashboard canlı: `http://localhost:8000` (Docker) / 8010 (yerel uvicorn).
- Ajanlar users tablosuna doğrudan yazacaksa yeni kolonları dikkate alsın; DB yazan scriptler `password_hash`'e dokunmamalı.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum |
|-------|--------|-------|---------|-------|
| X01 | ARASTIRMA: GIB VKN dogrulama (acik API + KVKK) | arastirmaci | P1 | plan |
| X02 | BUG: VKN zenginlestirme (MERSIS + web footer) pipeline tamamlama | gelistirici | P1 | blocked |
| X03 | MATCH v3: buyer profili skorlari (olcek uyumu + sertifika + amac yonu) | gelistirici | P2 | plan |
| X04 | UYELIK: sifre sifirlama + kurumsal e-posta dogrulama + Telegram hosgeldin | gelistirici | P2 | plan |
| X05 | Y26: API key yonetimi - rotasyon + kullanim metrikleri + tier rate limit | gelistirici | P2 | plan |
| P3-2 | VKN web kazima genisle (sadece footer de | web_kazima | plan | blocked |
| P7-1 | DB Migration 0007 - Job Intelligence tab | gelistirici | P0 | plan |
| P7-2 | Job Intelligence modul yapisi olusturma | mimar | P0 | plan |
| P7-5 | Ä°SKUR Scraper | web_kazima | P1 | blocked |
| P7-6 | Kariyer.net Scraper | web_kazima | P2 | blocked |
| Y21 | ARASTIRMA: ISKUR kurumsal eslestirme ver | arastirmaci |  | plan |
| Y23 | Odeme entegrasyonu (iyzico/Stripe) - oto | gelistirici |  | plan |
| P8-5 | Is ilani takip motoru: teknoloji donusum | arastirmaci | P2 | plan |
| P8-7 | Is ilani takip motoru: cografi genisleme | backend | P2 | plan |

## Tamamlananlar (Son 10)

| Gorev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| X00 | (dashboard) Sifreli oturum + Isletmem sekmeleri + Y22/Y25 tamamlandi | gelistirici | 2026-09-10 |
| Y18 | ARASTIRMA: Telegram musterisi icin abone | arastirmaci | 2026-09-09 |
| Y19 | ARASTIRMA: V9 smart matching (musteri-fi | gelistirici | - |
| Y20 | BUG: connection.py DATABASE_URL env over | gelistirici | - |
| Y22 | MATCH v2: eslestirme yonu secimi (tedari | gelistirici | 2026-09-09 |
| Y25 | product_categories yonetim arayuzu (admi | frontend | 2026-09-09 |
| P8-1 | Is ilani takip motoru: kaynak onceliklem | web_kazima | 2026-09-09 |
| P8-2 | Is ilani takip motoru: firma eslestirme  | gelistirici | 2026-09-09 |
| P8-3 | Is ilani takip motoru: buyume sinyali sk | arastirmaci | 2026-09-09 |
| P8-4 | Is ilani takip motoru: risk sinyali skor | arastirmaci | 2026-09-09 |

## Son Handoff'lar

- **X00 (dashboard)**: Şifreli oturum (PBKDF2) + İşletmem 4 sekme + Y22 eşleştirme yönü + Y25 kategori admin paneli + admin-only görev tahtası tamam; X01-X05 revize görevler eklendi. Canlı test akışları: üyelik 7/7, auth 8/8, layout 8/8 PASS.
- **P1-2**: Başkent scraper implementasyonu tamam (kod hazir)
- **P4-1**: Kalite skoru 27.5 -> ~64 tamamlandi
- **P8-8**: Kurumsal rapor ve medya entegrasyonu tasari tamaml
