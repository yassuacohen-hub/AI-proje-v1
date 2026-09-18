# MERVE-GOREV-04 — Admin Panel Kalite Turu (uzun görev, danışman)

> Merve 👩‍💻 danışmandır: dosya yazmaz, görev almaz, komut çalıştırmaz, panoya girmez.
> Çıktısı yalnız sohbet yanıtı + ortak eleştiri defterine not önerisi.
> Not: MERVE-GOREV-03'teki "blur" ve "şifremi unuttum" soruları artık kodlandı, bu görevde tekrar sorulmaz.

## Kopyalanacak prompt (Continue sohbetine yapıştır)

```
Merve, uzun bir kalite turu var. Acele etme, sırayla git.

Okuyacağın dosyalar:
1. web_dashboard/tabs/admin_auth.py          (giriş + şifremi unuttum, yeni kod)
2. src/company_master/ui/components/modal.py (modal bileşeni)
3. src/company_master/ui/styles.py           (sadece _MODAL_CSS ve _TOOLTIP_CSS blokları)
4. tests/test_admin_sifre_unuttum.py         (yeni testler)

BÖLÜM A — Şifremi unuttum akışı (en önemli)
A1. Kullanıcı bu ekranda kaybolur mu? Kaç adım var, hangi adımda ne beklemesi gerektiğini anlıyor mu?
A2. Sıfırlama kodu şu an e-posta ile gitmiyor, kullanıcı elle yazıyor. Kullanıcı bu kodu nereden bulacağını anlar mı? Ne yazsak anlaşılır olur?
A3. Yanlış kod girildiğinde ne oluyor? Kullanıcı tekrar denemeyi bilir mi?
A4. Aynı ekranda iki ayrı form var (istek + onay). Bu kafa karıştırır mı? Alternatif düzen öner.

BÖLÜM B — Modal bileşeni tekrar kullanılabilirlik
B1. Bu modalı yarın "müşteri sil, emin misin?" için kullanmak istersem hazır mı? Eksik ne?
B2. Klavyeyle kullanan biri ESC ile kapatabiliyor mu, sekme tuşu modal içinde kalıyor mu? (kodda ara, varsayma)
B3. Modal başlığı, gövdesi ve düğmeleri arasında görsel hiyerarşi var mı? Göz nereye gidiyor?

BÖLÜM C — Test yeterliliği
C1. tests/test_admin_sifre_unuttum.py neyi test ediyor, neyi ATLAMIŞ?
C2. Sence hangi hata bu testlerden kaçar? Bir örnek senaryo yaz.

BÖLÜM D — Genel izlenim
D1. Bu admin paneli hangi ürüne benziyor? İyi mi kötü mü, neden?
D2. Tek bir şey düzeltebilseydin ne olurdu?

Bitiş kuralları:
- Her bölüm için kısa cümleler. Teknik kelime az.
- Sonunda TEK tablo: | Bulgu | Sınıf | Öneri |
- Sınıf sütunu: 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri
- Mümkünse oran/yüzde ver (örn. "4 adımdan 2'si belirsiz = %50").
- Eleştiriden çekinme. Kötüyse kötü de.
- Kod YAZMA, öner. Dosya değiştirme.
- Sonunda "Ortak deftere şu notu ekleyin:" diye 3 satır özet ver (docs/ROO_ELESTIRI_NOTLARI.md için).
```

## Neden bu görev faydalı
- Yeni yazılan şifre sıfırlama akışını insan gözüyle sınar (kod testi kaçırdığını yakalar).
- Modal'ın gerçekten tekrar kullanılabilir olup olmadığını KAHİN'in emrettiği gibi ("başka yerlerde kullanırız") ölçer.
- Test körlüğünü dışarıdan bakan biri arar.
