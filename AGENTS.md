# Çalışma Alanı Kuralları (Kök AGENTS.md)

Bu çalışma alanında birden fazla yapay zeka ajanı paralel çalışabilir
(örn. Kimi Code ve Kilo Code orkestratörü).

## Çoklu Ajan Koordinasyon Protokolü

- **Her işe başlamadan önce ana bağlam dokümanını ve `AGENT_SYNC.md` dosyasını oku.**
  Ana bağlam kaynağı: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- **Başka bir ajanın aktif işi varsa aynı dosyalara dokunma veya kullanıcıyla koordine et.**
- Büyük bir işe başlarken `AGENT_SYNC.md` → "Aktif İşler" bölümüne kaydını ekle.
- İş bitince aktif kaydını kaldırıp "Tamamlananlar" bölümüne özet yaz.
- **Yapılacak iş, ana bağlam dokümanındaki hedef/MVP/teknik sınırlarla uyumlu olmalıdır.**
- **Doküman hiyerarşisi:** `V9` aktif ana bağlamdır; `V8`, `V7`, `V6` ve benzeri sürümler referans devrelerdir. Karar ve iş akışı aktif `V9` kaynak üzerinden yürütülür.
- Kalıcı durum güncellemeleri için tek doğru kaynak:
  - Ana bağlam → `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
  - Görev listesi → `AI proje v1/V10/TODO.md` (görevler)
  - Proje durumu → `AI proje v1/V10/project_state.md` (durum ve kararlar)
  - Değişiklik geçmişi → `AI proje v1/V10/CHANGELOG.md`
- `AI proje v1/` altında çalışırken ayrıca `AI proje v1/AGENTS.md` kuralları geçerlidir
  (açıklamalı ilerleme, tip güvenliği, hardcoded secret yasağı vb.).
- **MVP kuralı:** Veri tabanı, temel temizleme ve iş akışı kanıtlanmadan kullanıcı odaklı web arayüzüne geçilmez. Hızlı iç görünüm için Streamlit gibi sade ara yüz seçilir.

## Görev Panosu ve Dosya Kilidi (Çakışma Önleme) — ZORUNLU

Bu çalışma alanında **canlı görev takibi ve dosya kilidi mekanizması** vardır. Birden fazla ajan aynı anda çalışırken kimin hangi dosyada, hangi görevde olduğunu görmeden dosya değiştirmeyin.

1. **İşe başlamadan önce mevcut durumu kontrol et:**
   - `data/orchestrator/task_board.json` (ham veri) veya `data/orchestrator/gorev_panosu.md` (okunabilir görünüm)
   - `AGENT_SYNC.md` → "Aktif İşler" tablosu
   - `data/orchestrator/file_locks.json` → değiştirmeyi planladığın dosyalar kilitli mi?
2. **Görev al / oluştur:** `src/company_master/orchestrator/task_board.py` içindeki `gorev_ekle(task_id, baslik, sahip, oncelik, dosyalar=[...])` fonksiyonunu kullan. `dosyalar` parametresi verdiğin dosyaları otomatik kilitler; başka bir ajan tarafından kilitliyse `PermissionError` fırlatılır — bu durumda o dosyaya dokunma, görevi farklı kapsamla aç veya kullanıcıya danış.
3. **Durum güncelle:** İş başladığında `gorev_guncelle(task_id, durum="aktif")`, bitince `durum="done"`, engellenince `durum="blocked"` + `not="..."`.
4. **Kilidi bırak:** İş bitince `lock_birak(dosya, sahip)` çağır (kalıcı kilit bırakma).
5. **Aynı dosyada paralel değişiklik yapma.** Kilit yoksa bile `file_locks.json`'u kontrol etmeden büyük/çok dosyalı değişikliğe girme.
6. `AGENT_SYNC.md` **otomatik üretilen bir dosyadır** (`sync.agent_sync_yaz()` / task_board kaynaklı). Elle büyük yeniden yazım yapmayın; yalnızca ilgili fonksiyonlarla güncelleyin veya küçük not eklemek için dosyanın sonuna ekleyin (üstteki tabloyu bozmayın).

## Ajan Kılavuzu (Tek Şablon)

1. **Ana bağlamı oku**: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
2. **Koordinasyonu kontrol et**: `AGENT_SYNC.md`, `data/orchestrator/gorev_panosu.md` ve `data/orchestrator/file_locks.json`
3. **Görev ve sınırı doğrula**: `AI proje v1/V10/TODO.md` + `AI proje v1/V10/project_state.md`
4. **Çakışma kontrolü yap**: `task_board.gorev_ekle(..., dosyalar=[...])` ile dosyaları kilitle; aynı dosyada paralel değişiklik yapma
5. **İşe başla**: yalnız hedef, MVP ve teknik sınırlarla uyumlu adım at
6. **Bitince güncelle**: `gorev_guncelle(..., durum="done")`, kilidi bırak, özet yaz, gerekli durum dosyalarını yenile
7. **Son kontrol**: hedef/MVP/sınır dışına çıkmadı mı?

## Genel

- Gizli bilgiler (API anahtarı, token, şifre) asla koda veya notlara yazılmaz; `.env` kullanılır.
- Kullanıcının dosyalarını gerekçe açıklamadan silme / üzerine yazma.
- Tüm dosyalar **UTF-8** kodlamasında oluşturulur/kaydedilir. Türkçe karakterlerin (ç, ğ, ı, İ, ö, ş, ü ve büyük halleri) bozulmadığından emin olmadan dosyayı kaydetme (bkz. `Token Verimliliği, Türkçe Dokümantasyon ve Karakter Kodlama Standardı ana kurallara eklenmesi.txt`).

## VPN Kullanım Kuralı (2026-09-01)

- Kullanıcı VPN kullanmaktadır; gelecekte bazı ağ işlemleri (API istekleri, web scraping, kurumsal erişim) VPN kaynaklı hata verebilir.
- Aşağıdaki durumlarda kullanıcıya açıkça bildir:
  - Ağ isteği timeout / connection / DNS hatası veriyorsa: "Olası neden: VPN. Gerekirse VPN'i kapatıp deneyebilirsin." notu ekle.
  - IP kısıtlamalı bir endpointe erişim engellendiyse: VPN değiştirmeyi veya kapatmayı öner.
  - Erişilen hedef site/API coğrafi kısıtlama gösteriyorsa: VPN'in konumunu değiştirmeyi öner.
- Kullanıcı VPN'i kapatabileceğini onayladı. Şüpheli/güvenilir olmayan durumlarda (özellikle ödeme, kişisel veri, yasal riske girebilecek işlemler) VPN'i kapatmadan önce kullanıcıya sor.
- Kritik güvenlik uyarıları, yasal/yönetmelik riskleri, geri dönüşü olmayan işlemler her zaman NORMAL ve açık dilde yazılır.
- Kural referansı: `V10/09_kurallar_ve_promptlar/10_vpn_kurali.md`

---

## Harici Ajan Entegrasyonu (External Agents)

Bu çalışma alanında iç ajanlara ek olarak dış yapay zeka ajanları (Cursor Grok, GitHub Copilot, Claude Code vb.) da kullanılabilir. Tüm harici ajan etkileşimi **orkestratör üzerinden** ve **yalnızca `workspace/external/{agent_id}/` workspace'i** üzerinden yürütülür.

### Temel Kurallar

- Harici ajanlar proje köküne doğrudan erişemez; yalnız kendi workspace'inde çalışır.
- `.env`, gizli anahtarlar, KVKK kapsamındaki veriler ve üretim şeması harici ajana **gönderilmez**.
- Her görev, orkestratör tarafından hazırlanan **JSON/Markdown brief + bağlam + kısıtlar** paketiyle başlatılır.
- Harici ajan çıktısı güvenilir değildir; orkestratör + kalite ajanı + insan onayı döngüsünden geçmeden ana dala alınmaz.
- Başarısızlık durumunda **maksimum 3 deneme**, sonrasında iç ajanlara reassign yapılır.
- Tüm hatalar `AGENT_SYNC.md` → "ErrorLedger" bölümüne kaydedilir.

### Görev Tipleri (Harici Ajanlara Özel)

1. **Code Review** — mevcut kodları gözden geçirme, iyileştirme önerileri.
2. **Refactoring** — kod optimizasyonu, design pattern uyumu.
3. **Test Üretme** — unit test, integration test senaryoları.
4. **Dokümantasyon** — README, yorum, API dökümanları.
5. **Veri Dönüşümü** — CSV/JSON dönüşümleri, migration helper.
6. **Araştırma** — teknoloji karşılaştırma, benchmark.

### Referanslar

- [[AI proje v1/V10/08-Ajanlar/07_harici_ajan_protokolu]]
- [[AI proje v1/V10/08-Ajanlar/08_harici_ajan_gorev_onerileri]]
- [[AGENT_SYNC]] (External Agent Registry + ErrorLedger)
- Ana bağlam: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
