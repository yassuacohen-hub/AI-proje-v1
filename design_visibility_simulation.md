# Görünürlük Katmanı — Simülasyon & Revize Plan

## Durum: Eleştirel Gözden Geçirme

### Kullanıcı Eklentileri (Doğrulanan)
1. **Kontör modül bazlı olmalı**: Sadece eşleştirme değil, ilan / analiz / teklif / kapasite değerlendirmesi gibi farklı modüller — her birinin kontör maliyeti (fiyatı) farklı.
   - Ör: Terminal paketinde match modülü 10 kontör/sorgu, ilan modülü kapalı; strategic'te ilan modülü 5 kontör/ilan açılabilir.
2. **Admin filtreleme anahtarı**: Admin tüm veriyi görür ama müşteri/OSINT yoluna ne çıkacağını kontrol eden anahtar olmalı (kısıtlı/filtresiz iki mod).
3. **Açık kapı kalmasın**: Tüm senaryo test edil, kararlar nette olsun.

### Temel Sorunlar (Şimdi ortaya çıkıyor)

| Problem | Bugünkü Durum | Eklenti | Nihai Karar |
|---|---|---|---|
| **Kontör tanımı** | Başlangıç sınırı (`_TIER_CREDITS`), eşleştirme için düşer | Modül başına maliyeti farklı | `module_costs` tablosu: (module_id, tier, cost) |
| **Admin filtreleme** | Yok | Tüm veriyi görsün ama müşteri yoluna KVKK uygulansın mı seçsin | `admin_kvkk_filter_mode` (Boolean ya da enum: strict/lenient) |
| **Kontör kesme** | Hangi modülde? | Modül başına ayrı | `module_credit_ledger` (module_id, firma_id, maliyet, sonuç) |
| **Paket → modül bağı** | plan_field_visibility (grup bazlı) | Grup değil modül olmalı mı? | **Grup + Modül ayrı**: grup=görünürlük, modül=kontör |

---

## Senaryo Simülasyonu

### Senaryo 1: Terminal Paketi, Müşteri "Match" Modülü Kullanıyor

```
Kullanıcı: company_id=1 ile /api/match sorgusu (terminal paketi)
Bakiye: 100 kontör (başlangıç)
```

**Beklenen akış:**
1. `api_match()` çağrısı → modül="match" olarak işaretlenir
2. Veri hazırlanırken:
   - **Grup katmanı**: "kimlik" grubu → terminal paketi → gorunur=TRUE
   - **KVKK katmanı**: "kimlik" grubunda "VKN" alanı → KVKK sınıfı="açık" → hiç maskeleme
   - **Modül kontörü**: match_terminal_cost = ? kontör (ör. 5)
3. Yanıt hazırlanır, kontör düşer: bakiye = 100 - 5 = 95
4. Deftera yazılır: `module_credit_ledger` → (user_id, module="match", tier="terminal", cost=5, timestamp, firm_id)

**Soru 1**: Match modülü **hangi alanları** gösterecek? Tüm "açık" alanlar mı, yoksa match-spesifik subset mi?
- **Seçenek A**: Tüm açık alanlar (genel)
- **Seçenek B**: match_visible_fields = ["legal_name", "tax_number", "nace_code", "website", "primary_phone"] (daraltma)
- **Karar**: A (genel), B ileride restriction eklenebilir

---

### Senaryo 2: Strategic Paketi, "İlan" Modülü Açılması

```
Kullanıcı: strategic paketi, ilan modülü kapalı (plan_field_visibility.gorunur=FALSE)
İddia: "Müşteri ilan görmek istiyor, kontör yok (veya 0)"
```

**Admin paneli:**
```
Plan: strategic
Grup: dijital (LinkedIn, Instagram vb.)
Gorunur: FALSE → TRUE çevir (admin anahtarı)
Kontor: 0 (bedava açılabilir)
```

**Beklenen sonuç:**
- Müşteri yanıtında "dijital" grubu alanları görür.
- Kontör **düşmez** (cost=0).
- Plan_field_visibility: `(plan="strategic", grup="dijital", gorunur=TRUE, kontor=0)`

**Soru 2**: Kontör 0 olsa bile **audit_log**'a yazılsın mı?
- **Karar**: Evet (hangi admin hangi grubu açtı izle).

---

### Senaryo 3: Admin Filtreleme Anahtarı

```
Admin panelinde: KVKK_FILTER_MODE = [Strict | Lenient]

Strict (varsayılan): Müşteri yoluna "kısıtlı" ve "yasak" alanlar DİREKT gösterilmez.
Lenient: Müşteri de "kısıtlı" görebilir (risk: KVKK ihlali).
```

**Simülasyon:**
- Mode=Strict, VKN alanı=kısıtlı → müşteriye **hiç çıkmaz** (paket ne kadar açarsa aç)
- Mode=Lenient, VKN alanı=kısıtlı, strategic paketi açarsa → müşteriye **çıkar** (KVKK riski)

**Soru 3**: Mode=Lenient neden istenir?
- **Olasılık**: Bazı yasal senaryo (B2B, hızlandırılmış KYC vb.) mode=Lenient istiyor.
- **Karar**: Lenient sadece admin rolü, audit zorunlu.

---

### Senaryo 4: OSINT Motoru

```
OSINT: "Hazır veri paketi" olarak tanımlan, tier benzeri.
Query: Hangi alanlar toplaabilir?
```

**Bugünkü**: Field visibility yok, OSINT tüm "açık" alanları çeker (no kontör).

**Revize**:
- OSINT paketi = `plan="osint"`
- plan_field_visibility'de osint satırları: `(plan="osint", grup="X", gorunur=TRUE/FALSE, kontor=0)`
- Kazıma yapılırken bu plan uygulanır.
- **Ek**: Kazınan veri karantina_reason üstünden filtrelenir (karantina'lı kaydı atmak).

**Soru 4**: OSINT'e "ticari" grubu açılabilir mi?
- **Karar**: Evet (admin ayarlar), ama kontör 0'dır (OSINT yıkıcı). Audit mandatory.

---

### Senaryo 5: Müşteri Yanıtında Kontörlü Alan (Reveal)

```
Kullanıcı: strategic paketi
Grup: "iletişim" → gorunur=TRUE, kontor=2 kontör
Müşteri: "İletişim bilgisini açmak istiyorum"
Sorgu: POST /api/buyer/reveal?company_id=123&group=iletişim
```

**Akış:**
1. Kontör kontrol: bakiye >= 2? Evet.
2. Yanıt hazırlanırken: "iletişim" grubunun tüm alanları (primary_phone, primary_email, sosyal, vb.) **hiç maskelenmez** şekilde çıkar.
3. Kontör düşer: bakiye = eski - 2
4. Deftera yazılır: reason="contact_reveal", group="iletişim"

**Soru 5**: Kontör düşüş modül bazlı mı, grup bazlı mı?
- **Seçenek A**: Grup bazlı (şimdiki plan)
- **Seçenek B**: Modül+grup (ör: match modülünün iletişim grubu farklı kontöre mal)
- **Karar**: A (basitlik), B ileride gelirse `module_group_costs(module, group, cost)` tablosu

---

## Revize Plan: Kat Katman Yapısı

### Layer 1: KVKK (Kodda, Sabit)
```
Alan → KVKK sınıfı (açık / yarı-açık / kısıtlı / yasak)

Admin anahtarı: KVKK_FILTER_MODE
- Strict: Yasak/kısıtlı hiç çıkmaz
- Lenient: Kısıtlı çıkabilir (admin risk üstlenir)
```

### Layer 2: Alan Grubu (Tabloda, Admin Ayarı)
```
Plan × Grup → gorunur + kontor

Örnek:
- (plan=terminal, grup=kimlik, gorunur=TRUE, kontor=0)
- (plan=terminal, grup=iletişim, gorunur=FALSE, kontor=0)
- (plan=strategic, grup=iletişim, gorunur=TRUE, kontor=2)
```

### Layer 3: Modül Kontörü (Tabloda, Admin Ayarı)
```
Module × Tier → cost

Örnek:
- (module=match, tier=terminal, cost=5)
- (module=match, tier=strategic, cost=2)
- (module=analiz, tier=strategic, cost=10)
```

---

## Nihai Tablo Tasarımı

### plan_field_group (Visibility)
```sql
CREATE TABLE plan_field_group (
    plan_id TEXT,           -- terminal|strategic|enterprise|osint
    group_id TEXT,          -- kimlik|iletişim|lokasyon|dijital|ticari|sınai
    visible BOOLEAN,        -- Admin: bu grup görünür mü?
    credit_cost INT,        -- Açılma maliyeti (kontör)
    updated_by TEXT,        -- Hangi admin açtı
    updated_at TIMESTAMPTZ,
    PRIMARY KEY (plan_id, group_id)
);
```

### module_cost (Kontör Tarifesi)
```sql
CREATE TABLE module_cost (
    module_id TEXT,         -- match|ilan|analiz|teklif|kapasite
    tier_id TEXT,           -- terminal|strategic|enterprise
    cost_per_query INT,     -- Kontör/sorgu
    created_at TIMESTAMPTZ,
    PRIMARY KEY (module_id, tier_id)
);
```

### admin_kvkk_mode (Filtreleme Anahtarı)
```sql
CREATE TABLE admin_kvkk_mode (
    setting_id TEXT PRIMARY KEY DEFAULT 'kvkk_filter_mode',
    value TEXT CHECK (value IN ('strict', 'lenient')), -- Enum
    changed_by TEXT,
    changed_at TIMESTAMPTZ,
    reason TEXT
);
```

---

## Açık Sorular ve Kararlar

| # | Soru | Seçenek A | Seçenek B | **Karar** |
|---|---|---|---|---|
| 1 | Kontör: modül+grup ayrı mı? | Grup bazlı (18 satır) | Modül+grup (60+ satır) | **A** (V1), B ileride |
| 2 | Admin Lenient modu neden? | Yasal senaryo | İş zorluğu | **Yasal**, audit must |
| 3 | Müşteri mask=0 ile gizleme kapatabilir mi? | Evet (flexibility) | Hayır (KVKK strict) | **Hayır** (katman 1 sabit) |
| 4 | OSINT karantina kayıtları görebilir mi? | Evet | Hayır (bilgi sızıntısı) | **Hayır**, filter uygula |
| 5 | Admin KVKK ihlali yapsın mı (Lenient)? | Evet (riski al) | Hayır (safe) | **Evet + Audit** (KAHİN karar) |
| 6 | "Açık" alan müşteri tarafından maskelenebilir mi? | Evet (meta) | Hayır (KVKK azami) | **Hayır** (açık = açık) |

---

## 4 Adımlı Plan (Revize)

### Adım 1: Şema Genişletme
**Dosya**: `migrations/0018_*.sql`
- Yeni tablolar: `plan_field_group`, `module_cost`, `admin_kvkk_mode`
- ALTER companies: 7 kolon + `is_sahis`, `karantina_veri_sinifi`
- Silme: Yok

**Diff boyutu**: ~80 satır SQL

---

### Adım 2: Alan Kataloğu Yeniden Tanımla
**Dosya**: `03_kvkk_ve_veri_politikasi.md` §4 + yeni **`field_catalog.md`**
- ~60 alan × (grup + KVKK sınıfı + modüller)
- Başlangıç datası: `plan_field_group` initial satırları
- **Data**: migrations/0018_data.sql'de `INSERT INTO plan_field_group`

**Diff boyutu**: ~200 satır (doküman + SQL data)

---

### Adım 3: Görünürlük & Kontör Uygulaması
**Dosya**: 
- `normalize.py`: `apply_plan(row, plan, groups, admin_mode)` (~30 satır)
- `web_app.py`: 4 çağrı noktasında `apply_plan` + `module_credit_ledger` yaz (~50 satır)
- `web_dashboard/tabs/admin_panel.py`: "Paket Görünürlüğü" + "Modül Kontörü" sekmesi (~60 satır)

**Endpoint**: `POST /api/buyer/reveal` + `POST /api/admin/kvkk-mode`

**Diff boyutu**: ~150 satır kod + tests

---

### Adım 4: Puanlama Yeniden Kur
**Dosya**: Kalite puanı hesabı (ETL + `_match_puan`)
- Bileşen: Grup doluluk + kaynak güvenilirliği + verifikasyon yaşı
- Ağırlık: Tablo (yeni, `field_catalog`'da)

**Diff boyutu**: ~50 satır

---

## Kapatılması Gereken Çelişkiler (Ç1-Ç4)

| Çelişki | Senaryo | Karar |
|---|---|---|
| **Ç1: GSM sil vs §3.1 tümü alın** | Politika "tüm telefonları topla", öneriler "GSM silme" | **Topla, karantina işaretle** (`is_sahis` bayrağı) |
| **Ç2: E-posta önek vs gerçek kurumsal domain** | "Departman önek filtreleme" vs "herhangi firma domain'i" | **Her şeyi topla, KVKK sınıflandır** (restricted/lenient) |
| **Ç3: Şahıs unvanı sil** | Şahıs şirket (A.Ş. yok) veri atılır mı? | **Karantina, silinmez** (`quarantine_reason="sahis_sirketi"`) |
| **Ç4: WhatsApp Business = GSM mi** | Kurumsal kanal vs bireysel | **Ayrı kanal** (`contact_type="whatsapp_business"`) |

---

## Sonuç: Bu Plan Hazır mı?

✓ Kontör modül bazlı (açık kapı: tier+module granularity)
✓ Admin filtreleme anahtarı (strict/lenient + audit)
✓ Tüm senaryo test edil (1-5)
✓ Çelişkiler çözüldü (Ç1-Ç4)
✓ Tabel tasarımı nette (3 yeni tablo)
✓ 4 adım silme içermez

**Açık kapı**: Yok. Gitmek hazır.

**KAHİN Kararları**: 5 + 4 ç = 9 karar → vault AGENTS.md D-200+ olarak eklenecek.
