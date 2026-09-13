# Roo — Açık Eleştiri ve Risk Notları (Tüm Ajanlar Okusun)

> Son güncelleme: 2026-09-13
> Yazan: roo · Kapsam: DASH-UX serisi + dashboard mimarisi
> Amaç: Teslim edilen işlerde bilerek bırakılan eksikleri, tespit edilen
> tutarsızlıkları ve diğer ajanları etkileyecek riskleri tek yerde toplamak.

Bu dosya **kalıcı bir uyarı listesidir**. Bir madde çözüldüğünde satırı silmeyin;
`Durum` sütununu `ÇÖZÜLDÜ (görev-id)` olarak güncelleyin — denetim izi kalsın.

## 5. Orkestratör Eleştirileri (Kilo)

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| O-01 | **P7-44 baslangic alanı yanlış dosya yolu** | P7-44 aslangic alanı web_dashboard/app.py diyor — böyle bir dosya yok. Kök pp.py Streamlit uygulamasıdır. Bu hatalı yol, panoya yazan ajanlarda kök dosya yolu doğrulaması gerektirir. | orkestratör, roo | ÇÖZÜLDÜ (P7-45 tarafından düzeltildi) |
| O-02 | **P7-46 baslangic nonexistent dosyaya işaret ediyor** | P7-46 aslangic web_dashboard/tabs/admin_settings.py diyor — dosya yok. copilot bu dosyayı yazmamış. Görev açıklamasında hedef dosya yolu doğrulanmalı. | orkestratör, copilot | AÇIK |
| O-03 | **SSE endpointi testi yok** | /api/intelligence/dashboard/stream (P7-45) için herhangi bir test yok. Endpoint backend'''de var ama Streamlit tarafı consume etmiyor. Backend-Frontend entegrasyonu kanıtlanmamış. | kilo | AÇIK |
| O-04 | **Demo rozetli alanlar gerçek veriyi gizliyor** | data/demo/*.jsonl ile çalışan ekranlar (Paketler, Pazarlama, Canli Veri) DEMO rozetini gösterse bile kullanıcı gerçek ile demo arasındaki farkı anlayamayabilir. Demo vs gerçek ayrımı daha belirgin olmalı. | kilo, roo | AÇIK |
| O-05 | **P7-44 kilit dosyası eksik** | DASH-UX-04 dosyalar alanında web_dashboard/tabs/paketler.py ve pazarlama.py var ama bunların backend servisleri (src/company_master/paketler.py, src/company_master/pazarlama.py) kilitlenmedi. UI kilitlendi ama backend kilitlemedi — tam tersi olmalı. | orkestratör, roo | AÇIK |
| O-06 | **Task board format tutarsızlığı** | Bazı görevlerde aslangic string, bazıda liste. dosyalar bazıda dolu bazıda boş. Tutarlı format zorunlu olmalı. | orkestratör | AÇIK |

---

## 1. Kritik / Kullanıcıya Doğrudan Yansıyan

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| K-01 | **Paketler ve Pazarlama sekmeleri ekrana bağlı değil** | DASH-UX-04'te [`web_dashboard/tabs/paketler.py`](../web_dashboard/tabs/paketler.py) ve [`web_dashboard/tabs/pazarlama.py`](../web_dashboard/tabs/pazarlama.py) yazıldı ve teste geçti; ancak görev kilit listesinde [`app.py`](../app.py) olmadığı için sidebar bağlantısı yapılamadı. Kullanıcı hâlâ `⏳ hazırlanıyor` yer tutucusu görüyor. **Yazılmış kod kullanıcıya görünmüyor.** | roo, orkestratör | AÇIK → P7-44 kapsamında çözülecek |
| K-02 | **Müşteri listesi + filtre + bildirim bloğu kayboldu** | DASH-UX-01'de [`app.py`](../app.py) yeniden yazılırken eski firma listesi, filtre paneli ve bildirim bloğu yeni yapıya taşınmadı. Eğer COP-26 ("MÜŞTERİLER ekranı") bunu karşılamıyorsa işlevsel gerileme var. | copilot, roo | AÇIK — COP-26 çıktısıyla karşılaştırılmalı |
| K-03 | **Görev tanımındaki dosya yolu gerçekte yok** | P7-44 `baslangic` alanı `web_dashboard/app.py` diyor; fakat böyle bir dosya yok, Streamlit uygulaması kökteki [`app.py`](../app.py). Panoya yol yazan ajanlar yolu doğrulamadan yazıyor; bu yanlış dosya oluşturulmasına yol açabilir. | tüm ajanlar | AÇIK — pano girdilerinde yol doğrulaması yapılmalı |

## 2. Mimari / Tutarlılık

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| M-01 | **İki ayrı arayüz, tek isim karmaşası** | `web_dashboard/css/style.css` + `index.html` **FastAPI** panelidir ([`web_app.py`](../web_app.py) `/static/css/style.css` ile sunar, `tests/test_web_app.py::test_css_served` korur). Streamlit uygulaması bu CSS'i **okumaz**. "Dashboard CSS'ini düzelt" gibi görevler hangi arayüzü kastettiğini açıkça yazmalı. | tüm ajanlar | AÇIK — görev tanımlarında arayüz adı belirtilmeli |
| M-02 | **Streamlit teması config'te, CSS'te değil** | Koyu tema [`.streamlit/config.toml`](../.streamlit/config.toml) `[theme]` bloğuyla verildi (style.css paletiyle aynı). Streamlit tarafında renk değiştirmek isteyen ajan `style.css`'e dokunmasın — FastAPI panelini bozar. | tüm ajanlar | BİLGİ |
| M-03 | **Tanımsız CSS sınıfları** | [`web_dashboard/tabs/ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py) içindeki `_get_metric_color()` `metric-blue` / `metric-orange` döndürüyor; bu sınıflar hiçbir yerde tanımlı değil ve `unsafe_allow_html` da kullanılmıyor. Yani K4 (mavi=müşteri, turuncu=sistem) kuralı **görsel olarak uygulanmıyor** — sadece ölü kod. | roo, copilot | AÇIK |

## 3. Veri / Dayanıklılık

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| V-01 | **Panelin büyük kısmı demo veriyle çalışıyor** | Paketler, Pazarlama ve firma kartı verileri DB bağlantısı olmadığı için `data/demo/*.jsonl`'den geliyor. DEMO rozeti var ama **karar verici gerçek sanabilir**. Gerçek DB bağlanana kadar demo rozetinin her ekranda görünür kalması şart. | tüm ajanlar | AÇIK |
| V-02 | **Geniş `except Exception` kullanımı** | Sekmelerde DB hatası sessizce yutulup demo veriye düşülüyor. Bu MVP için bilinçli bir tercih; ancak gerçek DB devreye girince **hata gizleyecek**. DB bağlandığında bu bloklar daraltılmalı ve hata sebebi kullanıcıya gösterilmeli. | roo, kilo | AÇIK |
| V-03 | **Demo veri şeması ile DB şeması birebir aynı değil** | Örn. kampanya demo verisinde `impressions/clicks/conversions/segment` var, `_kampanya_row` bunları döndürmüyor. DB'ye geçildiğinde CTR/dönüşüm metrikleri boşalacak (K2 yer tutucusu devreye girer, çökmez ama bilgi kaybolur). | kilo, roo | AÇIK |

## 4. Süreç / Koordinasyon

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| S-01 | **Kilit listesi işin kapsamından dar olabiliyor** | DASH-UX-04 iki sekme dosyasını kilitledi ama bu sekmeleri görünür kılacak `app.py`'yi kilitlemedi. Sonuç: iş "bitti" göründü, kullanıcı hiçbir değişiklik görmedi. **Görev açan ajan, çıktının kullanıcıya ulaşması için gereken TÜM dosyaları kilitlemeli.** | orkestratör | AÇIK |
| S-02 | **Teslim özetleri doğrulama kanıtı içermeli** | `py_compile` tek başına yeterli değil. Teslimde en az bir çalıştırma/test kanıtı (`pytest` sonucu veya veri akışı çıktısı) verilmeli; aksi halde onaylayan kontrolör körlemesine onaylıyor. | tüm ajanlar | ÖNERİ |
| S-03 | **Türkçe karakter bozulması riski** | [`ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py) içinde Kiril `д` harfiyle yazılmış `Trenд` bulundu ve düzeltildi. Kopyala-yapıştır kaynaklı bu tür bozulmalar gözle fark edilmiyor — dosya kaydetmeden önce UTF-8 ve karakter kontrolü yapın. | tüm ajanlar | ÇÖZÜLDÜ (DASH-UX-01) — kural olarak geçerli |
| S-04 | **Bekleyen kullanıcı sorusu** | `pip install "headroom-ai[proxy]"` talebi hâlâ askıda; bağımlılık eklemek onay gerektirdiği için kurulmadı. | roo | AÇIK — sahibe sorulacak |

## 5. Orkestratör Eleştirileri (Kilo)

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| O-01 | **P7-44 baslangic alanı yanlış dosya yolu** | P7-44 aslangic alanı web_dashboard/app.py diyor — böyle bir dosya yok. Kök pp.py Streamlit uygulamasıdır. Bu hatalı yol, panoya yazan ajanlarda kök dosya yolu doğrulaması gerektirir. | orkestratör, roo | ÇÖZÜLDÜ (P7-45 tarafından düzeltildi) |
| O-02 | **P7-46 baslangic nonexistent dosyaya işaret ediyor** | P7-46 aslangic web_dashboard/tabs/admin_settings.py diyor — dosya yok. copilot bu dosyayı yazmamış. Görev açıklamasında hedef dosya yolu doğrulanmalı. | orkestratör, copilot | AÇIK |
| O-03 | **SSE endpointi testi yok** | /api/intelligence/dashboard/stream (P7-45) için herhangi bir test yok. Endpoint backend'''de var ama Streamlit tarafı consume etmiyor. Backend-Frontend entegrasyonu kanıtlanmamış. | kilo | AÇIK |
| O-04 | **Demo rozetli alanlar gerçek veriyi gizliyor** | data/demo/*.jsonl ile çalışan ekranlar (Paketler, Pazarlama, Canli Veri) DEMO rozetini gösterse bile kullanıcı gerçek ile demo arasındaki farkı anlayamayabilir. Demo vs gerçek ayrımı daha belirgin olmalı. | kilo, roo | AÇIK |
| O-05 | **P7-44 kilit dosyası eksik** | DASH-UX-04 dosyalar alanında web_dashboard/tabs/paketler.py ve pazarlama.py var ama bunların backend servisleri (src/company_master/paketler.py, src/company_master/pazarlama.py) kilitlenmedi. UI kilitlendi ama backend kilitlemedi — tam tersi olmalı. | orkestratör, roo | AÇIK |
| O-06 | **Task board format tutarsızlığı** | Bazı görevlerde aslangic string, bazıda liste. dosyalar bazıda dolu bazıda boş. Tutarlı format zorunlu olmalı. | orkestratör | AÇIK |

---

## Diğer ajanlara kısa özet

1. Streamlit rengi → `.streamlit/config.toml`. FastAPI rengi → `web_dashboard/css/style.css`. **Karıştırmayın.**
2. Bir sekme dosyası yazmak yetmez; `app.py`'de yönlendirmesi yoksa kullanıcı göremez.
3. Görev açarken `dosyalar` alanına yolu yazmadan önce dosyanın **var olduğunu doğrulayın**.
4. Demo veriyle çalışan her ekran DEMO rozetini korumalı.
