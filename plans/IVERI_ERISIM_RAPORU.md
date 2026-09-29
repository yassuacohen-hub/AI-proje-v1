# İvedik OSB Erişim Raporu — Neden yeniden kazı yapılamadı

> **Görev:** `VERI-IVEDIK-YENIDEN-01` · **Ajan:** yasu
> **Tarih:** 2026-09-29 · **Karar:** DURDURULDU
> **Uydurma yok:** Hiçbir sayı tahmin edilmedi, hepsi ölçüldü.

## 1. Sonuç — bir cümle

**İvedik OSB sitesi Cloudflare "I'm not a robot" doğrulamasıyla
korunuyor.** Düz HTTP isteği **401**, tarayıcı ajanı (Browser-Use)
**BLOCKED** döndürdü. Hiçbir yöntem sayfayı açamadı.

## 2. Kullanılan yöntemler ve SONUÇLARI

| Yöntem | Sonuç | Ölçüm |
|---|---|---|
| Düz HTTP (`httpx`, gerçek tarayıcı başlıkları) | ❌ **401** | 5.434 bayt `x-robots-tag: noindex` |
| HTTP / HTTPS, `www` / `wwwsiz` | ❌ **401** (4/4) | Hepsi aynı |
| `robots.txt` | ❌ **401** | robots.txt bile okunamıyor |
| **Browser-Use SDK (bulut tarayıcı ajanı)** | ❌ **BLOCKED** | 31 saniye, `output='BLOCKED'` |

**Browser-Use denemesi ölçümü** (`data/ivedik/browseruse_deneme.json`):
```
status  = finished
output  = 'BLOCKED'
süre    = 30,7 sn
```
API anahtarı `.env`'de bulundu ve **geçerli** (sunucu anahtarı
reddetmedi). Yani yöntem çalışmadı, kimlik değil.

## 3. 401 sayfasının metni (neden)

```
Security Verification
Please enable JavaScript and cookies to continue.
To access this website, please wait while we complete a security check.
Loading... I'm not a robot
```

Bu **Cloudflare bot doğrulaması**: gerçek tarayıcı çalıştırmayı,
JavaScript yürütmesini ve çerez kabul etmesini istiyor.

## 4. Elimizdeki verinin durumu

`data/ivedik/firmalar.jsonl`:

| Ölçüm | Değer |
|---|---|
| Satır | 3.354 |
| **Tekil unvan** | **14** |
| Mükerrer satır | 3.340 (%99,6) |
| Adres / telefon / e-posta | **%0** |
| Sektör / sosyal medya / web | **%0** |

Elimizdeki İvedik verisi **kullanılamaz**.

## 5. Brief'teki varsayım tutmadı (D-66 gereği durdurdum)

> *"Mevcut `ivedik_scraper.py` betiğinin çalışır durumda olduğu
> varsayıldı. Kaynak site yapısı değiştiyse **dur**, panoya sorun aç."*

→ **Site yapısı değişmedi, erişim kapandı.** Varsayım tutmadı, brief
gereği durdurdum, kazıma yapmadım.

Ayrıca brif'te alan adı hatası var: brief `ivedik.org.tr` diyor,
kod `ivedikosb.org.tr` kullanıyor. `ivedik.org.tr` **DNS'te hiç yok**.

## 6. Sektör sorusu — yanıtlanamadı

Siteye hiçbir yöntemle ulaşılamadığı için detay sayfası okunamadı.
**Uydurma cevap verilmedi.**

## 7. Neden daha fazla zorlamadım

Politika P-5: *"403/401 boş liste DEĞİL, **açık hata**dır."*

Cloudflare doğrulamasını aşmanın yolları (stealth eklentileri, proxy,
TLS parmak izi taklidi) kurumun **bilerek koyduğu** kapıyı geçmek
olurdu. Toast'ta site kapısı yoktu — orada izin dilekçesiyle yürüdük.
Burada kapı var; geçmek kararı kurumun.

Ayrıca kurumsal ilişki riski: İvedik OSB Müdürlüğü ile ileride
resmî bir veri akışı kurulacaksa, baştan gizli kapıdan girmek bu
ilişkiyi riske atar.

## 8. Öneriler (karar KAHİN'de)

1. **İvedik OSB Müdürlüğü'ne yazılı izin iste** — OSTİM'de
   yaptığımızın aynısı. En temiz yol. Dilekçe şablonu hazır.
2. **14 kaydı `dogrulanmamis` işaretle**, beklemede bırak.
3. **İvedik'i kaynak listesinden düşür** — 14 firma + %100 boş alanla
   "3.354 firma" vaat etmek yanıltıcı olur.

**Önerim:** önce 1, yanıt yoksa 3.

## 9. Yapılmayanlar (dürüstlük)

- Kazıma **başlatılmadı**, `firmalar.jsonl` **üzerine yazılmadı**
- Browser-Use **tek sayfa** denendi, ölçüldü, işe yaramadı
- Sektör sorusuna **uydurma cevap verilmedi**
- Hiçbir sayı **tahmin edilmedi**

