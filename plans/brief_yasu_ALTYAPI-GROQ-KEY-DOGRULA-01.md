# Brief: GROQ-KEY-CANLI-DOGRULA-01

**Ajan:** yasu
**Öncelik:** P2
**Mod:** code

## Bağlam

D-195 (`data/orchestrator/D-195-GROQ-DIRECT-CLIENT_2026-09-23.md`) Groq için NineRouter bypass eden doğrudan client (`src/company_master/gateway/groq_client.py`) yazdı. Unit testler geçti (27/27) ama canlı API testi D-195 yazıldığında 403 vermişti (eski/geçersiz key).

`.env` içindeki `GROQ_API_KEY` o tarihten sonra güncellenmiş görünüyor ama hâlâ doğrulanmadı. Ayrıca mevcut `test_groq_direct.py` script'i `GroqClient`'ı hiç çağırmıyor — NineRouter zinciri üzerinden `meta-llama/*` ve `mistralai/*` model adlarıyla gidiyor ve 404 "No active credentials" alıyor. Bu, `GroqClient` doğrudan-çağrı yolunun hiç canlı test edilmediği anlamına geliyor.

## Görev

1. `src/company_master/gateway/groq_client.py::GroqClient.chat()` fonksiyonunu doğrudan (NineRouter'sız) `groq/llama-3.3-70b-versatile` modeliyle canlı çağır.
2. Sonucu doğrula: 200 + içerik mi, yoksa 403/401 mı?
3. Eğer key hâlâ geçersizse: hatayı D-195 dokümanına ekle, yeni key gerektiğini not et (üretme — sadece bulguyu raporla).
4. Eğer başarılıysa: `ai_chat.py::sohbet()` zincirinde `groq/*` modelin gerçekten `GroqClient` yolunu kullandığını doğrulayan hızlı bir entegrasyon kontrolü yap (mevcut unit testler mock kullanıyor, canlı değil).
5. `data/orchestrator/D-195-GROQ-DIRECT-CLIENT_2026-09-23.md` "Sonraki Adımlar" bölümünü sonuçla güncelle (Durum: kod tamamlandı → doğrulandı/çalışmıyor).

## Kabul Kriteri

- `GroqClient` doğrudan canlı çağrıldı (NineRouter değil).
- Sonuç (başarı/hata) D-195 dokümanına yazıldı.
- Yeni test dosyası/kalıcı script gerekmiyor — mevcut `test_groq_direct.py` düzeltilebilir veya tek seferlik çalıştırılıp silinebilir.
