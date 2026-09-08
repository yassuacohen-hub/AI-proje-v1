# Çalışma Kuralları

Bağlantılar: [[09_kurallar_ve_promptlar/README]] · [[01_kasa_kurallari]] · [[03_prompt_kutuphanesi]] · [[00-Home]]

Bu belge, bu kasada çalışan tüm yapay zeka ajanlarının (ve kullanıcının verdiği oturum talimatlarının) uyması gereken kalıcı çalışma kurallarını toplar. Proje genelindeki mühendislik ilkeleri için kökteki `AGENTS.md` bağlayıcıdır; buradaki kurallar kasa yönetimi özelindedir.

## 1. Koruma kuralları

1. **Mevcut dosyalar silinmez.** Kullanıcının hiçbir belgesi gerekçe açıklanmadan ve onay alınmadan silinmez veya üzerine yazılmaz.
2. **Mevcut dosyalar taşınmaz.** Klasör değişikliği bağlantıları bozacağı için ancak kullanıcı onayıyla yapılır.
3. **Geliştirme üstüne yapılır.** Yeni yapı, mevcut temelin üzerine eklenir; var olan düzen korunur.

## 2. Belgeleme kuralları

1. Tüm belgeler Türkçe yazılır.
2. Her yeni belge [[01_kasa_kurallari]] içindeki adlandırma ve bağlantı standartlarına uyar.
3. Yeni belge eklendiğinde [[00-Home]] ve ilgili bölüm README'si güncellenir.
4. Bir kural değiştiğinde eski metin silinmez; güncelleme tarihiyle not düşülür.

## 3. Prompt yönetimi

1. Operasyonel tüm promptlar [[03_prompt_kutuphanesi]] içinde toplanır.
2. Kullanıcının verdiği tekrarlanabilir talimatlar, oturum sonrasında kural olarak bu bölüme işlenir.
3. Her prompt; isim, amaç, kullanım ve çıktı formatı alanlarıyla kaydedilir.

## 4. Davranış kuralları (AGENTS.md özeti)

1. **Öğretici mod:** Kod ve belge üretirken mantık adım adım Türkçe açıklanır.
2. **Açıklamasız silme yok.** (bkz. AGENTS.md §3)
3. **Hardcoded secret yok.** API anahtarları `.env` / ortam değişkenlerinde tutulur.
4. **Test edilmemiş iş teslim edilmez.** Değişiklikler doğrulanmadan tamamlandı sayılmaz.

## 5. Bu belgenin uygulanması

- Bir ajan bu kasada işe başlarken önce bu belgeyi ve [[01_kasa_kurallari]] belgesini okur.
- Kural ile kullanıcının doğrudan talimatı çelişirse, kullanıcının güncel talimatı geçerlidir ve çelişki kullanıcıya bildirilir.
