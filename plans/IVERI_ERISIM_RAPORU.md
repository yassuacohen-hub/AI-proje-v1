# İvedik OSB Erişim Raporu — Neden yeniden kazı yapılamadı

> **Görev:** `VERI-IVEDIK-YENIDEN-01` · **Ajan:** yasu
> **Tarih:** 2026-09-29 · **Karar:** DURDURULDU (erişim engeli)
> **Uydurma yok:** Hiçbir sayı tahmin edilmedi, hepsi ölçüldü.

## 1. Sonuç — bir cümle

**İvedik OSB'nin sitesi `HTTP 403` döndürüyor.** Sunucu ayakta ama
bot koruması tüm istekleri reddediyor. Bu bir hata değil, **erişim
engeli**; aşmak için kurumdan izin gerekir.

## 2. Ölçümler

| Denetim | Sonuç |
|---|---|
| DNS `www.ivedikosb.org.tr` | ✅ Çözülüyor → `185.151.30.153` |
| DNS `ivedikosb.org.tr` | ✅ Çözülüyor → `185.151.30.153` |
| HTTP(S) `https://www.ivedikosb.org.tr/firmalar/` | ❌ **403** (nginx) |
| HTTP `http://www.ivedikosb.org.tr/firmalar/` | ❌ **403** (nginx) |
| `robots.txt` | ❌ **403** — robots.txt bile okunamıyor |

Sunucu **gerçek yanıt veriyor** (nginx başlıkları, HTTP 403 gövdesi
geliyor). Yani "site kapalı" değil, "bize izin vermiyor".

## 3. Elimizdeki verinin durumu

`data/ivedik/firmalar.jsonl`:

| Ölçüm | Değer |
|---|---|
| Satır | 3.354 |
| **Tekil unvan** | **14** |
| Mükerrer satır | 3.340 (%99,6) |
| Adres / telefon / e-posta | **%0** |
| Sektör / sosyal medya / web | **%0** |

Yani elimizdeki İvedik verisi **kullanılamaz**: 14 gerçek firma,
üzerinde 3.340 mükerrer, hiçbir alan dolu değil.

## 4. Brief'teki varsayım tutmadı (D-66 gereği durdurdum)

Brief şunu varsayıyordu:
> *"Mevcut `ivedik_scraper.py` betiğinin çalışır durumda olduğu
> varsayıldı. Kaynak site yapısı değiştiyse **dur**, panoya sorun aç."*

→ **Site yapısı değişmedi, erişim kapandı.** Varsayım tutmadı, brief
gereği durdurdum, kazıma yapmadım.

Ayrıca brif'te alan adı hatası var: brief `ivedik.org.tr` diyor,
kod `ivedikosb.org.tr` kullanıyor. `ivedik.org.tr` **DNS'te hiç yok**
(`gaierror`).

## 5. Sektör sorusu — yanıtlanamadı

Brief'in ek sorusu: *"Sitede sektör bilgisi var mı? Varsa kazıyıcı
neden almıyor?"*

**Yanıt: ölçemedim.** Siteye ulaşılamadığı için detay sayfası hiç
okunamadı. Bu soruya tahminle cevap vermedim — brief'teki uydurma
yasakı burada da geçerli.

## 6. Neden 403'e karşı ek istek atmadım

Politika P-5: *"403/401 boş liste DEĞİL, **açık hata**dır."* Ve
genel kural: erişim engelini aşmak için tekrar tekrar istek göndermek
kurumun bot korumasını zorlamak olurdu.

OSTİM ile fark: OSTİM'de izin **dilekçeyle** alınıyor ve politika
P-1..P-10 çerçevesinde yürüyor. İvedik'te böyle bir izin yok; sadece
bot koruması var. İkni kırmaya çalışmadım.

## 7. Öneriler (karar KAHİN'de)

1. **14 kaydı `dogrulanmamis` işaretle, beklemede bırak.**
   Alternatif kaynak zaten kapalı (MERSİS/e-Devlet — D-281).
2. **Kurumdan özel erişim iste** (İvedik OSB Müdürlüğü) — OSTİM
   için yaptığımız izin sürecinin aynısı.
3. **Kaynak olarak İvedik'i tamamen çıkar.** Elinde 14 firma ve
   %100 boş alan var; üründe "İvedik OSB firmaları" diye gösterip
   **3.354 satır vaat etmek yanıltıcı** olur.

## 8. Yapılmayanlar (dürüstlük)

- Kazıma **başlatılmadı**, `firmalar.jsonl` **üzerine yazılmadı**
- Sektör sorusuna **uydurma cevap verilmedi**
- Hiçbir sayı **tahmin edilmedi**
