# DOC-VISIBILITY-KATMANI-29 — Kullanıcı Dokümanı

**Task ID:** DOC-VISIBILITY-KATMANI-29  
**Sahip:** Utku  
**Öncelik:** P2  
**Dependency:** ALTYAPI-VERI-GORUNURLUK-01

---

## Amaç

Yeni dosya `docs/VISIBILITY_LAYER_GUIDE.md` yaz. İçerik: Layer 1 & 2 mimarı, Admin KVKK mode, Module kontör, Çelişki çözümü (Ç1-Ç4).

---

## Adımlar

### 1. Yeni Dosya Oluştur

**Dosya:** docs/VISIBILITY_LAYER_GUIDE.md

İçerik bölümleri:

#### 1.1 Giriş
- Amaç: KVKK uyumlu veri maskeleme
- 2-layer sistem (kod + tablo)

#### 1.2 Layer 1: Kod Sınıflandırması
- 33 field × 4 class: açık, yarı-açık, kısıtlı, yasak
- Örnekler: legal_name (açık), primary_phone (kısıtlı), quarantine_reason (yasak)
- _KVKK_FIELD_CLASS dict

#### 1.3 Layer 2: Tablo Görünürlüğü
- plan_field_group: 6 group × 3 tier
- Terminal tier: kimlik=açık, iletişim=kısıtlı
- Strategic tier: kimlik=açık, iletişim=yarı-açık
- Enterprise tier: kimlik=açık, iletişim=açık

#### 1.4 Admin KVKK Mode
- Strict: KVKK mutlak (kısıtlı → maskeli)
- Lenient: Yönetici riski (kısıtlı → açık, yasak hala maskeli)

#### 1.5 Module Kontör Sistemi
- 5 modul (match, ilan, analiz, teklif, kapasite)
- Terminal: match=10, ilan=0, analiz=5, teklif=0, kapasite=3
- Strategic: match=5, ilan=3, analiz=8, teklif=2, kapasite=2
- Enterprise: serbest (0)

#### 1.6 Çelişki Çözümü (Ç1-Ç4)
- Ç1: GSM silme → quarantine_reason="ç1_telefon", is_sahis=1
- Ç2: Email domain → quarantine_reason="ç2_email"
- Ç3: Kişi adı → quarantine_reason="ç3_isim", is_sahis=1
- Ç4: WhatsApp → quarantine_reason="ç4_whatsapp", is_sahis=1

#### 1.7 Scenario Örnekleri

**Örnek 1: Terminal User Match Sorgusu**
- Tier: terminal
- Query: /api/match
- Kontör: 10 kredi düş
- Görünürlük: legal_name açık, primary_phone maskeli (053***67)

**Örnek 2: Strategic Admin Lenient Mode**
- Admin mode: lenient değiştirildi
- Görünürlük: primary_phone açık (riski yönetici kabul etti)
- Audit: admin_kvkk_mode tablo'ya sebep kaydedildi

---

## Kabul Kriteri

- [x] docs/VISIBILITY_LAYER_GUIDE.md oluşturuldu
- [x] Layer 1 & 2 detaylı açıklandı
- [x] Admin mode (strict/lenient) örnekli
- [x] Module kontör matrisi
- [x] Ç1-Ç4 çelişki çözümü
- [x] 2-3 scenario örneği

---

## İlgili Nodlar

- [[Huginn Data Insights/src/company_master/api/core/normalize.py#27-82|_KVKK_FIELD_CLASS]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0018_visibility_layer.sql|0018 migration (3 tablo)]]
