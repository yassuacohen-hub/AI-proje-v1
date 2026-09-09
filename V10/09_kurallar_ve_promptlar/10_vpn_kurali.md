# VPN Kullanım Kuralı

Bağlantılar: [[00-Home]] · [[project_state]] · [[CHANGELOG]]

**Tarih:** 2026-09-01
**Sürüm:** 1.0
**Karar referansı:** [[10_ankara_osb_sentez]] Karar 14 (yeni)

---

## 1. Genel

Kullanıcı VPN kullanmaktadır. Gelecekte bazı ağ İşlemleri (API Çağrıları, web scraping, kurumsal servis erişimi, veritabanı bağlantısı) VPN kaynaklı hata verebilir.

---

## 2. Şüpheli Durum Tespiti ve Bildirim

Aşağıdaki belirtiler görüldüğünde kullanıcıya VPN kaynaklı olabileceği bilgisi verilir:

| Belirti | Muhtemel Neden | Öneri |
|---|---|---|
| `Timeout`, `Connection reset`, `No route to host` | VPN sunucusu/sağlayıcı erişimi | VPN'i kapat veya sunucu değiştir |
| `DNS_PROBE_FINISHED_NXDOMAIN`, `Name resolution failed` | VPN DNS yönlendirmesi | VPN'i kapat veya DNS ayarla |
| `403 Forbidden`, `Access denied` | Erişilen site IP/milli restriction | VPN ülke/lokasyon değiştir |
| SSL/`certificate verify failed` | VPN ara katmanı | VPN'i kapat veya ssl doğrulamayı (gerekçeli) gevşet |
| API `401` / session kesilmesi | Kurumsal IP beyaz listesi | VPN'i kapat, kurumsal ağa bağlan |
| Web scraping boş/anlamsız HTML | Site bot/VPN koruması | VPN değiştir veya farklı IP |

---

## 3. Kullanıcı Onaylı Davranış

- Kullanıcı VPN'i kapatabileceğini bildirdi.
- Yukarıdaki şüpheli durumlarda kullanıcıya BİLGİ VERİLİR ve gerekirse VPN kapatması önerilir.
- **Kritik** (ödeme, kişisel veri, yasal risk) İşlemlerde VPN kapatmadan önce kullanıcı onayı ALINIR.
- Şüpheli durumda İşlem otomatik devam etmez; kullanıcıya danışılır.

---

## 4. Güvenlik / Yasal Risk Anında

Aşağıdaki durumlarda NORMAL ve açık dilde uyarılır (caveman stiline geçilmez):

- Ödeme / para İşlemleri
- Kişisel veri transferi
- Yasal veya idari made riski
- Geri dönüşü olmayan (silme, taşıma, yayınlama) İşlemler