# MERVE-GOREV-03 — Admin Giriş Modalı Uzun Analiz (danışman, panoya girmez)

> Merve dosya yazmaz, komut çalıştırmaz. Yalnız Continue sohbetinde cevap verir.
> KAHİN (Ürün Sahibi) aşağıdaki bloğu kopyalayıp Continue'ya yapıştırır.

---

## Kopyalanacak prompt

Merve, uzun bir iş var. Acele etme, sırayla git.

Şu 3 dosyayı oku:
- `web_dashboard/tabs/admin_auth.py`
- `web_dashboard/charts.py` (yalnız `kpi_stil_css` ve `tema_paleti`)
- `src/company_master/ui/tokens.py`

Sonra şu 6 soruyu cevapla:

1. **Giriş formu neden modal gibi durmuyor?** Streamlit'in `st.form` sınırları neler? Gerçek modal için hangi yol daha sağlam: `st.dialog` mi, elle CSS overlay mi? Birini seç ve nedenini yaz.

2. **Arka plan bulanıklığı (`backdrop-filter: blur`)** Streamlit'in iframe/DOM yapısında hangi seçiciye uygulanmalı? Tarayıcı desteği ve Safari tuzağı var mı?

3. **Marka kimliği.** `tokens.py` içindeki Indigo `#6366f1` modalda nerelerde görünmeli? Kenarlık, başlık, buton, odak halkası — her biri için somut değer öner. Karanlık/aydınlık tema ikisinde de çalışsın.

4. **Tekrar kullanılabilirlik.** KAHİN "başka yerlerde de kullanırız" dedi. Modal bileşeninin imzası nasıl olmalı? Kaç parametre? Hangi durumlar dışarıdan gelmeli, hangileri içeride kalmalı? Aşırı mühendislik yapma, en az parametre.

5. **Erişilebilirlik.** Modal açıkken klavye tuzağı (focus trap), ESC ile kapatma, ekran okuyucu etiketi — Streamlit'te bunlardan hangileri mümkün, hangileri mümkün değil? Mümkün olmayanlar için ne yapılmalı?

6. **Şifremi unuttum.** Bağlantı modalın neresinde durmalı? Tıklayınca aynı modal mı değişmeli, yeni modal mı açılmalı? Kullanıcı kaybolmadan geri dönebilmeli.

## Bitiş kuralları

- Cevabın sonunda **tablo** olsun: soru numarası, kararın, tek cümle gerekçe.
- KAHİN'e teknik kelime kullanma. Sade anlat.
- Eleştirin varsa (kod kötü, karar yanlış, eksik var) çekinme, yaz.
- Kod yazma. Sadece karar ve gerekçe.
