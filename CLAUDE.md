# CLAUDE.md

AI için proje kılavuzu burada tutulur.



## Ana referanslar



- Proje anayasası: `AGENTS.md`

- Kasa kuralları: `V10/09_kurallar_ve_promptlar/01_kasa_kurallari.md`

- Çalışma kuralları: `V10/09_kurallar_ve_promptlar/02_calisma_kurallari.md`

- Prompt kütüphanesi: `V10/09_kurallar_ve_promptlar/03_prompt_kutuphanesi.md`

- Token ve dil politikası: `V10/09_kurallar_ve_promptlar/04_token_verimliligi_ve_dil_politikasi.md`

- Kasa giriş noktası: `V10/00-Home.md`



## LLM Wiki Katmanlar



Bu projede Obsidian vault, LLM Wiki deseninin **bilgi merkezi (wiki)** katmanıdır. Hedef, her an için bilgiyi yeniden üretmek yerine, bilgileri bir kez toplayıp sürdürülebilir bir yapıda tutmaktır.



### 1. Katman: Raw Sources (Ham Kaynaklar)

- **Tanım:** Kullanıcının sağladığı, değiştirilemez kaynak dokümanlar.

- **Örnek:** `V10/01_gereksinimler/`, `V10/03_mimari/`, `.agents/references/`, clipped web makaleler.

- **Kural:** LLM ham kaynakları okur ama değiştirmez. Bilgi sadece wiki'ye entegre edilir.



### 2. Katman: The Wiki (Bilgi Grafiği)

- **Tanım:** LLM tarafından oluşturulup sürdürülen markdown dosyaları kümesi.

- **İçindekiler:** `00-Home.md` (index), `project_state.md`, `TODO.md`, `CHANGELOG.md`, entity/concept sayfaları, karşılaştırmalar.

- **Dosyalar:** `[[00-Home]]`, `[[project_state]]`, `[[TODO]]`, `[[CHANGELOG]]`.

- **Kural:** LLM wiki'yi oluşturur, günceller ve tutar. Kullanıcı kaynak sağlar, sorular sorar.



### 3. Katman: The Schema (Yapı ve Kurallar)

- **Tanım:** Wiki'nin nasıl organize edildiğini, isimlendirme kurallarını ve iş akışını tanımlayan belge.

- **Dosyalar:** `AGENTS.md`, `CLAUDE.md`, `V10/09_kurallar_ve_promptlar/`.

- **Kural:** LLM ve kullanıcı bu dosyalarla birlikte evrim geçirir. Yeni domain için schema güncellenir.



### Operations (İş Akışları)



#### Ingest (Giriş / Kaynak İşleme)

- Bir kaynak eklendiğinde: `V10/00-Home.md` bölümlerine bak, anahtar kavramları çıkar, ilgili wiki sayfalarını güncelle, `CHANGELOG.md`'e kayıt ekle.

- Akış: Kaynak okundu → özetlendi → entity sayfaları güncellendi → index güncellendi → log kaydı eklendi.



#### Query (Sorgu)

- Kullanıcı sorusu alındığında: Önce `[[00-Home]]` (index) oku, ilgili entity/kavram sayfalarına git, bulguları birleştir ve cevapla.

- Cevap formatı: markdown sayfa, tablo veya grafik olabilir. Değerli cevaplar wiki'ye geri kaydedilir (yeni sayfa veya güncelleme).



#### Lint (Sağlık Kontrolü)

- Belirli aralıklarla wiki taranır: çelişkiler (iki sayfada farklı veri), eskimiş iddialar (yeni kaynakla çelişen), yetim sayfalar (bağlantısı olmayan), eksik çapraz referanslar.

- LLM sağlık kontrolü yapar ve "sorunlu X sayfası var, kon Y'yi incele" gibi öneriler sunar.



### Kural Seti (CLAUDE.md'den devralınmıştır)



1. **Mevcut dosyalar silinmez.** Kullanıcının hiçbir belgesi gerekçe açıklanmadan ve onay alınmadan silinmez veya üzerine yazılmaz.

2. **Mevcut dosyalar taşınmaz.** Klasör değişikliği bağlantıları bozacağı için ancak kullanıcı onayıyla yapılır.

3. **Geliştirme üstüne yapılır.** Yeni yapı, mevcut temelin üzerine eklenir; var olan düzen korunur.

4. **Tüm belgeler Türkçe yazılır.**

5. **Her yeni belge `V10/09_kurallar_ve_promptlar/01_kasa_kurallari.md` içindeki adlandırma ve bağlantı standartlarına uyar.**

6. **Yeni belge eklendiğinde `[[00-Home]]` ve ilgili bölüm README'si güncellenir.**

7. **Bir kural değiştiğinde eski metin silinmez; güncelleme tarihiyle not düşülür.**

8. **Operasyonel tüm promptlar `V10/09_kurallar_ve_promptlar/03_prompt_kutuphanesi.md` içinde toplanır.**

9. **Kullanıcının verdiği tekrarlanabilir talimatlar, oturum sonrasında kural olarak bu bölüme işlenir.**

10. **Hardcoded secret yok.** API anahtarları `.env` / ortam değişkenlerinde tutulur.

11. **Test edilmemiş iş teslim edilmez.** Değişiklikler doğrulanmadan tamamlandı sayılmaz.



---

Kullanıcı: Projeyi başlarken önce `V10/00-Home.md`, `V10/09_kurallar_ve_promptlar/01_kasa_kurallari.md` ve `V10/09_kurallar_ve_promptlar/02_calisma_kurallari.md` dosyalarını oku.

Agent: Anla ve kurallara uyar.