# Ajan Chat Kuralı (D-210 — KAHİN kararı 2026-09-25)

**Amaç:** Ajanlara görev talimatları verilirken ya da teslim sonrası raporlar incelenirken, **sorun/hata/engel varsa chat sistemini ZORUNLU kullanmak**. Sessiz çalışma ve bildirim bekleme yasak.

---

## Kural 1: Hata/Sorun Bildirimi (ZORUNLU)

Görev esnasında hata, kütüphane yokluğu, test failure, veri uyumsuzluğu, dosya bulunamadığı gibi **herhangi bir engel** karşılaşılırsa:

1. **Hemen** sistem chat'ine gönder:
   ```
   @ihsan HATA: [görev-id] — [sorun özeti] — [teknik detay] — Neyden yardım gerekiyor?
   ```

2. Sessizce çalışmaya devam etme, hata görmezden gelme, rapora not koyup bitir deme.

3. **Chat yanıtı bekleme süresi:**
   - **P0 görev:** 5-10 dakika (kritik, ihsan hemen cevaplar)
   - **P1 görev:** 10-15 dakika (yüksek öncelik)
   - **P2 görev:** 15-30 dakika (orta, cevap 30 dakika içinde)
   - **Cevap gelmedi:** 30 dakika sonra tekrar gönder veya eski workaround'a geç, rapor'da not bırak
   - **Kuralı ihlal:** Cevap 2x timeout'ta geçerse, ajan çeşitli seviye karamsa cezaya girer

---

## Kural 2: Görüş/Yorum/Soru (HEPSİ CHAT'TE)

- **Brif karmaşıklığı (cevap zorunlu):**
  ```
  @ihsan [görev-id] — Bu adımda şüphem var: [soru]
  → ihsan ZORUNLU cevap verir. P0: 5-10 dk, P1: 10-15 dk, P2: 15-30 dk
  ```

- **Başka ajana soru (cevap zorunlu):**
  ```
  @yasu [konular] — senin görüşün nedir?
  → yasu adına çağrıldığı için ZORUNLU cevap verir.
  Cevap vermeyen ajan: görevine ek zorluk, sonraki 3 görevde 24 saat delay
  ```

- **Rapor tutarsızlığı (cevap zorunlu):**
  ```
  @orkestrator [rapor dosyası] — satır 45'te: [tutarsızlık]. Doğrulama safhası yapmalı mı?
  → orkestrator'a @mention = yanıt şart. Gecikmede rapor inceleme donuyor.
  ```

---

## Kural 3: Ajanlararası Koordinasyon

- **Çakışan dosya/görev:** 
  ```
  @[ajan] — senin görevin [X] benim görevim [Y] ile overlap var. Kimin önce yapması lazım?
  ```

- **Bağımlılık:** 
  ```
  @[ajan] — senin görevin bitmesi benim işime lazım. Ne zaman bitecek?
  ```

- **Bilgi paylaşma:** 
  ```
  @[ajan] — [dosya] üzerinde buldum: [teknik detay]. İşine yarar mı?
  ```

---

## Kural 4: Rapor Eleştirisi ve Düzeltme

- **Orkestratör/ihsan bulgu:** 
  ```
  @[ajan] — [rapor dosyası] satır 12: [bulgu]. Düzelt ve rebase et.
  ```

- **Ajan yanıtı:** 
  ```
  @orkestrator — [rapor dosyası] güncelledim. Kontrol et.
  ```

- Chat'te **doğrulama kaydı** tutulur; rapor history'si net kalır.

---

## Kural 5: Chat Kapanışı (Görev Tesliminde)

Görev bitip rapor yazıldıktan sonra: 
```
@orkestrator [görev-id] — Teslime hazırız. Chat'te [X] soru/hata çözüldü, [Y] not raporda, [Z] test geçti.
```

Orkestratör yanıt: `Onaylandı. Review'a geçer.` (= chat kapalı, düzenli review süreci başlıyor).

---

## Kural 6: Sessiz Çalışma Yasağı

**Yasak:**
- "Görev zor, ama chat'e sormayacağım, kendim çözeceğim."
- Hata varsa rapora "not" koyup söylemeyin.
- Başka ajan ile çakışmayı görmezden gelmek.
- Test failure'ın sebebini bulamadıysa orta bırakıp teslim etmek.

**Ceza:** Kuralı ihlal eden ajan'ın chat erişimi kısıtlanır; sonraki 3 görevinde cevabı 24 saat sonra alır (hızlı tempo bozulur). Tekrar ihlalde görev almaz, only observer.

---

## Chat Araçları

| Araç | Komut | Ne yapar |
|------|-------|---------|
| **Log** | `data/orchestrator/chat/messages.jsonl` | Tüm mesajlar (wikilink'li) |
| **CLI** | `python scripts/chat_al.py --ajan <ajan>` | Terminalde görüntüle |
| **Web** | Admin panel "💬 Chat" | Planlı (S-04) |
| **Bot** | `@orkestrator CHAT-DURUM` | Son 24 saat özeti |

---

## Örnekler

### Hata Bildirimi

```
@ihsan HATA: UI-ADMIN-KVKK-MODU-26 — ImportError: normalize module yok. 
src/company_master/api/core/ klasörü eksik mi? Yardım?
```

### Soru

```
@orkestrator — API-LAYER2-DINAMIK-YÜKLEME-30 brif'inde "kontörlü yükleme" ile 
"batch yükleme" farkı net değil. Örnek verebilir misin?
```

### Koordinasyon

```
@utku — UI-ADMIN-KVKK-MODU-26 ve API-ADMIN-MFA-26 ikisi de admin panel'e sekme ekliyor.
Hangisi önce? Conflict risk var mı?
```

### Rapor Düzeltme

```
@yasu — UI-ADMIN-FEATURE-FLAG-25_rapor_2026-09-25_orkestrator.md satır 38:
"audit log tablo yapısı" açıklanmamış. Ekle, rebase, push et.
```

---

## İlgili Dökümanlar

- [[Huginn Data Insights/AGENTS.md]] — Çekirdek kurallar
- [[Huginn Data Insights/docs/AJAN_DETAY.md]] — Detaylı ajan rehberi
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] — Ajan koordinasyon hub'ı

---

---

## Chat Komutları (Sistem Komut Seti)

### 1. Mesaj Gönderme

```bash
# Hata bildirimi
python scripts/chat_gonder.py --to ihsan --type hata \
  --task-id UI-ADMIN-KVKK-MODU-26 \
  --mesaj "ImportError: normalize module yok"

# Soru
python scripts/chat_gonder.py --to orkestrator --type soru \
  --task-id API-LAYER2-DINAMIK-YÜKLEME-30 \
  --mesaj "Kontörlü yükleme ile batch yükleme farkı?"

# Koordinasyon
python scripts/chat_gonder.py --to utku --type koordinasyon \
  --task-ids UI-ADMIN-KVKK-MODU-26,API-ADMIN-MFA-26 \
  --mesaj "Hangisi önce yapılmalı?"

# Rapor düzeltme talep
python scripts/chat_gonder.py --to yasu --type rapor-duzelme \
  --rapor-dosya "UI-ADMIN-FEATURE-FLAG-25_rapor_2026-09-25_orkestrator.md" \
  --satir 38 \
  --mesaj "audit log tablo yapısı açıklanmamış"
```

**Sonuç:** Mesaj `data/orchestrator/chat/messages.jsonl`'ye yazılır, alıcı bilgilendirilir.

---

### 2. Chat Geçmişi Görüntüleme

```bash
# Son 24 saatin mesajları
python scripts/chat_al.py --saat 24

# Belirli ajan için mesajlar
python scripts/chat_al.py --ajan yasu --limit 20

# Görev bazlı mesajlar
python scripts/chat_al.py --task-id UI-ADMIN-KVKK-MODU-26

# Mesaj türüne göre filtre
python scripts/chat_al.py --tip hata --limit 10

# Belirli tarih aralığı
python scripts/chat_al.py --tarih-baslang "2026-09-25 08:00" --tarih-bitis "2026-09-25 18:00"
```

**Sonuç:** Terminal'de renkli çıktı + timestamp + kullanıcı + message + context.

---

### 3. Chat Durum Özeti

```bash
# Günlük rapor
python scripts/chat_al.py --ozet gun

# Hata sayısı
python scripts/chat_al.py --ozet hata-sayisi

# Ajan aktivitesi
python scripts/chat_al.py --ozet ajan-aktivite

# Cevap süresi analiz
python scripts/chat_al.py --ozet cevap-suresi-ortalama
```

**Sonuç:** Tabloyla özet (hata/soru/koordinasyon sayısı, ajan bazında, ortalama cevap süresi).

---

### 4. Chat Bildirimi

```bash
# Tüm ajanlara broadcast
python scripts/chat_gonder.py --broadcast \
  --mesaj "Orkestratör sistem maintenance başlıyor, 30 dakika"

# Sorulara otomatik cevap
python scripts/chat_otomatik.py --enable --sablonlar data/orchestrator/chat_sablonlari.json

# @mention bildirimi
python scripts/chat_al.py --mention-alerts --ajan yasu
```

**Sonuç:** Bildirim gönderilir; @mention edilenlere hızlı uyarı.

---

## Gerçek Örnekler (Ne yazarsın → Ne olur)

### Örnek 1: Hata Bildirimi

**Ne yazarsın:**
```
@ihsan HATA: UI-ADMIN-KVKK-MODU-26 — ImportError:
web_dashboard/tabs modülü yok. src/company_master/api/core/normalize.py
import başarısız. Dosya yok mu? Yardım?
```

**Komut:**
```bash
python scripts/chat_gonder.py --to ihsan --type hata \
  --task-id UI-ADMIN-KVKK-MODU-26 \
  --mesaj "ImportError: web_dashboard/tabs modülü yok. normalize.py import başarısız."
```

**Sonuç:**
- ✅ Mesaj `messages.jsonl`'ye yazılır (timestamp + kullanıcı + task-id + type)
- ✅ ihsan'a bildirim gönderilir (5 dakika içinde cevap beklenir)
- ✅ Raporda bu sorun kaydedilir: `[CHAT-REFERANS: msg-2026-09-25-001]`
- ✅ Görev `durum: engel` olur (cevap alınana kadar)

---

### Örnek 2: Soru

**Ne yazarsın:**
```
@orkestrator — API-LAYER2-DINAMIK-YÜKLEME-30 brif satır 25'te
"kontörlü yükleme" ile "batch yükleme" farkı net değil.
Örnek veya pseudocode?
```

**Komut:**
```bash
python scripts/chat_gonder.py --to orkestrator --type soru \
  --task-id API-LAYER2-DINAMIK-YÜKLEME-30 \
  --mesaj "Kontörlü yükleme vs batch yükleme farkı? Örnek?"\
  --brif-satir 25
```

**Sonuç:**
- ✅ Mesaj `messages.jsonl`'ye yazılır
- ✅ orkestrator'ün "Henüz cevapladı mı?" kontrol edilir
- ✅ Cevap şöyle gelir: `CEVAP: Kontörlü = tek kayıt, batch = N kayıt. Örnek: [...]`
- ✅ Raporda: `Brif satır 25 ile ilgili soruya orkestrator cevap verdi`
- ✅ Görev devam eder (`durum: aktif`)

---

### Örnek 3: Koordinasyon

**Ne yazarsın:**
```
@utku — UI-ADMIN-KVKK-MODU-26 ve API-ADMIN-MFA-26
ikisi de admin_panel.py'ye sekme ekliyor.
Hangisi önce? File lock sorunu var mı?
```

**Komut:**
```bash
python scripts/chat_gonder.py --to utku --type koordinasyon \
  --task-ids UI-ADMIN-KVKK-MODU-26,API-ADMIN-MFA-26 \
  --mesaj "Hangisi önce? File lock?"
```

**Sonuç:**
- ✅ Mesaj `messages.jsonl`'ye yazılır
- ✅ Her iki görev'in durum kontrol edilir (hangisi aktif, hangisi bekleme)
- ✅ utku'nun cevabı: `UI-ADMIN-KVKK-MODU-26 önce, sonra MFA. Lock sorunu yok.`
- ✅ Rapordaki sıra güncellenir
- ✅ Her iki görev order'ı belgelenir: `[DEĞERLENDİRME: utku 2026-09-25 10:30]`

---

### Örnek 4: Rapor Düzeltme

**Ne yazarsın:**
```
@yasu — UI-ADMIN-FEATURE-FLAG-25_rapor_2026-09-25_orkestrator.md
satır 38'de "audit log tablo yapısı" açıklanmamış.
CREATE TABLE bloğu ekle, rebase, push et.
```

**Komut:**
```bash
python scripts/chat_gonder.py --to yasu --type rapor-duzelme \
  --rapor-dosya "UI-ADMIN-FEATURE-FLAG-25_rapor_2026-09-25_orkestrator.md" \
  --satir 38 \
  --mesaj "audit log tablo yapısı açıklanmamış. CREATE TABLE ekle."
```

**Sonuç:**
- ✅ Mesaj `messages.jsonl`'ye yazılır (ref: rapor dosyası + satır numarası)
- ✅ yasu'ya: `Rapor UI-ADMIN-FEATURE-FLAG-25 → satır 38 düzeltme gerekli`
- ✅ yasu düzeltip push ettiğinde: `@orkestrator Düzeltme yapıldı, gözle.`
- ✅ orkestrator kontrol eder, onaylarsa: `Onaylandı.`
- ✅ İlgili task'ın durum: `durum: review-ok` olur

---

### Örnek 5: Otomatik Broadcast

**Ne yazarsın:**
```
@broadcast — Tüm ajanlara: Orkestratör 30 dakika bakım yapacak,
görevleri yavaşlatmayın
```

**Komut:**
```bash
python scripts/chat_gonder.py --broadcast \
  --mesaj "Orkestratör 30 dk bakım. Görevleri yavaşlatmayın." \
  --oncelik yuksek
```

**Sonuç:**
- ✅ Tüm ajanlara (`yasu`, `utku`, `salih`) mesaj gönderilir
- ✅ Chat log'unda: `[BROADCAST] 2026-09-25 10:45:30`
- ✅ Her ajan kendi chat history'sinde görür
- ✅ Response timeout 5 dakikaya uzatılır

---

**Kural Tarihi:** 2026-09-25
**Karar Numarası:** D-210
**Zorlama:** KESIN (ihlalde ceza var)
