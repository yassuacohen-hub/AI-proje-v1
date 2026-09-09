# Token Verimliliği ve Dil/Dokümantasyon Politikası

Bağlantılar: [[09_kurallar_ve_promptlar/README]] · [[02_calisma_kurallari]] · [[CLAUDE]]

Bu belge, bu kasada çalışan tüm yapay zeka ajanlarının bilgi işleme, token verimliliği ve dil kullanımı konusundaki bağlayıcı politikalarını toplar. Proje anayasası olan `[[AGENTS]]` ve `CLAUDE.md` ile birlikte okunur.

---

# BÖLÜM 1 — Token Verimliliği ve Bilgi İşleme Politikası

## Amaç

Sistemin amacı yalnızca bilgi depolamak değildir. Amaç:

- Bilgiyi işlemek
- Sentezlemek
- Kalıcı hale getirmek
- Tekrar işlenmesini engellemek

ve bunu minimum token maliyetiyle yapmaktır.

## Temel Prensip

Ham kaynaklar pahalıdır. Wiki ucuzdur. Bu nedenle sistem:

1. Önce Wiki'den öğrenir.
2. Gerekirse ilgili Wiki sayfalarını açar.
3. En son çare olarak ham kaynaklara döner.

Ham kaynaklar sürekli yeniden okunmamalıdır.

## Bilgi İşleme Hiyerarşisi

Öncelik sırası:

1. İlgili Wiki Sayfaları
2. İlgili Sentez Sayfaları
3. İlgili Varlık Sayfaları
4. İlgili Kaynak Özetleri
5. Ham Kaynaklar

Ham kaynaklar son başvuru noktasıdır.

## Wiki Öncelikli Yaklaşım

Yeni bir soru geldiğinde:

- ❌ Önce kaynakları tarama
- ✅ Önce Wiki'yi tara

Çünkü Wiki daha önce işlenmiş bilgidir.

## Soruya Göre Bağlam Seçimi

Her soruda aşağıdaki soru sorulmalıdır:

> Bu soruyu cevaplamak için minimum hangi sayfalar gerekli?

Yalnızca o sayfalar okunmalıdır.

## Akıllı Sayfa Yükleme

Bir soru için:

- ❌ Tüm klasör okunmaz
- ❌ Tüm konu ağacı okunmaz
- ✅ İlgili düğümler okunur

**Örnek:**

Konu: "Kullanıcı doğrulama sistemi"

Okunacaklar:
- Kimlik Doğrulama
- JWT
- Güvenlik Modeli

Okunmayacaklar:
- Dashboard
- Analitik
- Muhasebe

## Wiki Sayfa Türleri

Her bilgi aynı seviyede tutulmamalıdır.

### L1 — Genel Bakış Sayfaları
En kısa katman. Konuya hızlı giriş. 100-500 kelime.

### L2 — Sentez Sayfaları
Birden fazla kaynağın birleşimi. Asıl çalışma katmanı budur. Soru cevaplamada öncelikli okunur.

### L3 — Varlık Sayfaları
Kişiler, projeler, ürünler, kurumlar, teknolojiler hakkındaki kalıcı bilgiler.

### L4 — Kaynak Özetleri
Ham kaynağın işlenmiş özeti. Tam kaynak yerine önce bunlar okunur.

### L5 — Ham Kaynaklar
Son çare. Yalnızca eksik bilgi olduğunda açılır.

## Yeni Kaynak İşleme Politikası

Yeni kaynak geldiğinde:

1. Oku
2. Özet çıkar
3. Varlıkları güncelle
4. İlgili sentezleri güncelle
5. Bağlantıları güncelle
6. Kaynağı arşivle

Aynı kaynak tekrar tekrar okunmamalıdır.

## Bilgi Biriktirme Politikası

Amaç belge biriktirmek değildir. Amaç bilgi yoğunluğunu artırmaktır.

- ❌ 100 benzer not
- ✅ 10 güçlü sentez notu

## Özetleme Politikası

Büyük sayfalar zamanla şişer. Bu nedenle her büyük sayfa şu şekilde katmanlandırılmalıdır:

- Yönetici Özeti
- Temel Bulgular
- Detaylar

Varsayılan olarak yalnızca üst katman okunmalıdır.

## Oturum Birikimi

Önemli sohbetler kaybolmamalıdır. Fakat sohbet geçmişi de taşınmamalıdır. Prensip:

```
Sohbet → Karar → Wiki Güncellemesi → Sohbet Silinebilir
```

## Yanıtların Kalıcılaştırılması

Değerli analizler yalnızca sohbet içinde bırakılmamalıdır. Aşağıdakiler Wiki'ye dönüştürülmelidir:

- Karşılaştırmalar
- Araştırmalar
- Stratejik analizler
- Mimari kararlar
- Önemli bulgular

Bilgi tekrar üretileceğine saklanmalıdır.

## Lint Politikası

Belirli aralıklarla Wiki denetimi yapılmalıdır. Kontrol edilecekler:

- Yetim sayfalar
- Kırık bağlantılar
- Tekrarlanan bilgiler
- Güncelliğini yitiren bilgiler
- Eksik varlık sayfaları
- Eksik çapraz bağlantılar

Amaç Wiki boyutunu değil, Wiki kalitesini artırmaktır.

## Token Verimliliği Altın Kuralı

Bilgiyi tekrar üretme. Bilgiyi tekrar bulma. Bilgiyi tekrar okuma. Bilgiyi işle, Wiki içinde sakla, gerektiğinde yalnızca ilgili kısmı kullan.

> Wiki büyüsün, bağlam küçülsün.

---

# BÖLÜM 2 — Dil ve Dokümantasyon Politikası

## Temel Kural

Token optimizasyonu amacıyla dil değiştirilemez. Sistem token maliyetini dil değiştirerek değil, bağlam yönetimini iyileştirerek azaltmalıdır.

İnsanların okuyacağı tüm içerikler Türkçe oluşturulmalıdır.

## Türkçe Oluşturulacak İçerikler

Aşağıdaki tüm içerikler zorunlu olarak Türkçe oluşturulacaktır:

### Obsidian Wiki Sayfaları
- Genel Bakış Sayfaları
- Sentez Sayfaları
- Varlık Sayfaları
- Konsept Sayfaları
- Karşılaştırma Sayfaları
- Araştırma Sayfaları
- Kaynak Özetleri
- Analiz Sayfaları
- MOC (Map of Content) Sayfaları

### Proje Yönetim Belgeleri
- TODO.md
- project_state.md
- CHANGELOG.md
- Teknik Borçlar
- Sprint Notları
- Karar Kayıtları
- Risk Analizleri
- Etki Analizleri

### Bilgi Yönetimi Belgeleri
- index.md açıklamaları
- log.md kayıtları
- Wiki özetleri
- Kaynak değerlendirmeleri
- Çapraz referans açıklamaları
- Lint raporları

### Operasyonel Belgeler
- Toplantı notları
- Görev notları
- Araştırma notları
- İş akışları
- Süreç dokümanları
- Mimari açıklamalar

## Dosya Adları

Dosya adları da varsayılan olarak Türkçe oluşturulmalıdır.

Örnek:
- Kullanıcı Yönetimi.md
- Kimlik Doğrulama Sistemi.md
- Teknik Borçlar.md
- Haftalık Durum Raporu.md
- Mimari Kararlar.md

## Bağlantılar

Wiki bağlantıları Türkçe sayfa isimleri üzerinden kurulmalıdır.

Örnek:
- [[Kullanıcı Yönetimi]]
- [[Kimlik Doğrulama Sistemi]]
- [[Mimari Kararlar]]

## Teknik Terimler

Sektörde yerleşmiş teknik kavramlar çevrilmek zorunda değildir.

Örnek:
- JWT
- PostgreSQL
- Redis
- API
- Backend
- Frontend
- Docker

Ancak açıklamalar Türkçe yazılmalıdır.

Örnek: "JWT tabanlı kimlik doğrulama sistemi kullanılmaktadır."

## Öncelik Sırası

Öncelik:

1. İnsan okunabilirliği
2. Bilgi kalitesi
3. Obsidian bilgi ağı bütünlüğü
4. Token optimizasyonu

Token tasarrufu için doküman dili değiştirilmez. Asıl tasarruf:

- Daha az bağlam yüklemek
- Daha iyi özetler oluşturmak
- İlgili node'ları seçmek
- Bilgiyi tekrar işlememek

ile sağlanır.

## Altın Kural

Wiki insan içindir. LLM bakımını yapar. İnsan okur. Bu nedenle insan tarafından okunacak tüm bilgi katmanları Türkçe üretilmelidir.

---

# BÖLÜM 3 — Orkestrasyon Modülü v2: Token Verimlilik Kriterleri

> Tarih: 2026-09-03 · Sahip: Orkestratör Ajan (Inkling)

## Amaç

Orkestrasyon sistemi (task_board + watch_agent + iç ajan yönetimi) kuruldu.
Bu bölüm, sistemin **token bütçesini korumasını ve azaltmasını** sağlayan
kriterleri tanımlar.

## Eski Sistem vs Yeni Sistem: Token Kıyaslaması

| Metrik | Eski (orkestratorsız) | Yeni (Orchestrator v2) | Tasarruf |
|--------|----------------------|------------------------|----------|
| Başlangıç maliyeti/oturum | 5100-8100 token | ~1600 token | **-3500 to -6500** |
| Çakışma kaybı (ortalama) | +3000 token | 0 token | **-3000** |
| Başarısız retry maliyeti | +4000 token | +1500 token | **-2500** |
| Keşif/exploration token'ı | +2500 token | +200 token | **-2300** |
| Board overhead (yeni) | 0 | +300 token | +300 |
| **Net oturum başına** | **~18000** | **~7000** | **~-11000 (%60)** |

## Token Tasarruf Kriterleri (7 Önlem)

### K1 — Delta-Only Board Okuma (EN KRİTİK)

```python
# YANLIŞ: Her oturumda tüm board'u oku (100 görev → 2000 token)
board = task_board.gorev_listesi()

# DOĞRU: Sadece ilgili görev + aktif lock'lar
gorev = task_board.gorev_getir(task_id)        # 1 görev → 50 token
locks = task_board.locklar()                   # sadece aktif → 100 token
```

**Kural:** Agent başına maksimum 1 görev + lock listesi okunur. Tam board
ancak `donem-raporu` veya `pano` komutunda okunur.

**Tasarruf:** -1500 to -2000 token/oturum.

### K2 — Görev Brief (Önceden Hazırlanmış Bağlam)

Agent başlamadan önce board, agent'ın okuması için minimal brief üretir:

```python
brief = f"""
Görev: {gorev.baslik}
Sahip: {gorev.sahip}
Dosyalar: {gorev.dosyalar}
Önceki deneme: {gorev.attempts}
Başarı kriteri: {gorev.success_criteria}
"""
```

**Kural:** Agent kodu keşfetmez; sadece brief'teki dosyaları açar.
Keşif token'ı sıfırlanır.

**Tasarruf:** -2000 to -3000 token/oturum.

### K3 — Session Handoff (Agentlar Arası Devir)

Agent bitirince sadece "sonraki adım" yazılır:

```python
handoff = {
    "tamamlandı": "ivedik_scraper.py implementasyonu",
    "sonraki_adım": "ASO scraper'a geç",
    "dikkat_edilmesi": "rate_limit 2.5s yapılmalı"
}
```

**Kural:** Bir sonraki agent tüm geçmişi değil, sadece handoff'u okur.

**Tasarruf:** -2000 to -4000 token/devir.

### K4 — Sıkıştırılmış AGENT_SYNC

```markdown
# Eski (tam log, 50 satır) → ~1500 token
| Kilo Code | 2026-09-03 | scripts/enrich_... | 4 adım... |

# Yeni (özet, 5 satır) → ~200 token
| Kilo Code | 09-03 | enrich_alternative_sources | done |
```

**Kural:** AGENT_SYNC.md otomatik üretilir (watch_agent), satır başına
maksimum 80 karakter. Detaylar task_board.json'da.

**Tasarruf:** -1000 to -1500 token/oturum.

### K5 — Tool Call Çıktısını Kısalt

- `run_commands`: Sadece son 20 satır + exit code
- `read_files`: Sadece ilgiyi fonksiyon/blok, tüm dosya değil
- `search_codebase`: Maksimum 10 sonuç

**Kural:** Tool call başına maksimum 500 token çıktı.

**Tasarruf:** -1000 to -2000 token/tool-call.

### K6 — Otomatik "Ne Okunmalı" Listesi

Agent başlamadan board, okunması gereken dosyaları söyler:

```python
okunacak = [
    "src/company_master/etl/scrapers/ivedik_scraper.py",
    "tests/company_master/test_ivedik.py"
]
```

**Kural:** Agent bu listeden fazla dosya açamaz (exploration yasak).

**Tasarruf:** -1500 to -3000 token/oturum.

### K7 — Retry/Backoff Token Optimizasyonu

Başarısız görev retry edilirken:
- İlk deneme: Tam context (3000 token)
- 2. deneme: Sadece hata mesajı + değişen dosyalar (1000 token)
- 3. deneme: Sadece handoff (500 token)

**Kural:** Her retry'de context %50 azalır (exponential context decay).

**Tasarruf:** -1500 to -2500 token/başarısız görev.

## Toplam Token Etki Projeksiyonu

| Senaryo | Eski/Orkestratorsız | Orchestrator v2 | Net |
|---------|---------------------|-----------------|-----|
| Günde 1-2 oturum, sıralı | 18000/gün | 19000/gün | **+1000 (hafif artış)** |
| Günde 3-5 oturum, paralel | 54000/gün | 21000/gün | **-33000 (%60)** |
| Çakışma > %30 | +15000 kayıp | 0 | **-15000** |
| Başarısız oranı > %20 | +8000 | +3000 | **-5000** |

## Kritik Eşik

```
Sıralı çalışma (1 agent):     ~+500 token/oturum  → KÜÇÜK ZARAR
Paralel çalışma (2+ agent):   ~-3000 token/oturum → BÜYÜK KAZANÇ
Çakışma sıklığı > %30:        ~-5000 token/gün   → ÇOK BÜYÜK KAZANÇ
```

## Uygulama Öncelikleri

| # | Kriter | Tasarruf | Uygulama Durumu |
|---|--------|----------|-----------------|
| 1 | K1 Delta-only board | -1500 to -2000 | ⏳ Bekliyor |
| 2 | K2 Görev brief | -2000 to -3000 | ⏳ Bekliyor |
| 3 | K3 Session handoff | -2000 to -4000 | ⏳ Bekliyor |
| 4 | K4 Sıkıştırılmış AGENT_SYNC | -1000 to -1500 | ⏳ Bekliyor |
| 5 | K5 Tool call kısaltma | -1000 to -2000 | ⏳ Bekliyor |
| 6 | K6 Otomatik okuma listesi | -1500 to -3000 | ⏳ Bekliyor |
| 7 | K7 Retry context decay | -1500 to -2500 | ⏳ Bekliyor |

## Uyarılar

1. **Board okuma overhead'i:** task_board.json büyüdükçe tam okuma
   maliyeti artar. Delta-only okuma şart.
2. **Workspace izolasyonu:** İç ajanlar köke erişiyor; gerçek worker
   çalıştırılırsa workspace izolasyonu (K2 brief + K6 okuma listesi) şart.
3. **watch_agent SPOF:** watch_agent tek nokta arıza; kilitlenirse retry
   ve enforce durur. Sağlık kontrolü gerekir.

## Altın Kural

> Token tasarrufu "daha az çalışmak" değil, "aynı işi daha az token ile
> yapmak"tır. Orkestrasyon sistemi agent'ın ne yapacağını bilir yapar;
> keşfetmez, çakışmaz, yeniden yapmaz.
