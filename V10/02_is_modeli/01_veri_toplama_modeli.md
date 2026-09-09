# Veri Toplama Modeli

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[01_veri_kaynagi_envanteri]] · [[06_web_kazima_uzmani]]

Bu belge, [[01_sirket_master_ana_belgesi]] (Company Master V1.0) §9'dan türetilmiş veri toplama iş modelidir.

## Kaynak önceliği (Ankara)

1. OSB'ler
2. OSTİM
3. İvedik
4. ASO OSB'leri
5. diğer sanayi bölgeleri
6. oda/kuruluş kaynakları
7. kamuya açık şirket kayıtları
8. şirketlerin resmi web siteleri

## Temel ilkeler

- Ham veri silinmez; yeniden işleme ve denetim için `source_records` altında saklanır.
- Eksik alanlar tahmin edilmez; kanıt yoksa `Unknown` kalır (UNKNOWN Prensibi, master §6).
- Çelişkili kaynak bilgisi silinmez; güvenilirlik → güncellik → kanıt gücü sırasıyla çözülür (master §5).
- Her kritik alan için `first_seen_at`, `last_seen_at`, `verified_at` tutulur.

## Roller

- Veri temini: [[06_web_kazima_uzmani]] (hedefli, izinli, kontrollü)
- Kaynak envanteri ve doğrulama: [[01_veri_kaynagi_envanteri]] altındaki envanter belgeleri
- Nihai karar ve doğrulama katmanı: web kazımadan ayrı tutulur

## Yasal ve etik sınır

- robots.txt, rate limit ve kaynak kullanım koşullarına uyulur.
- Yasal sınırların dışında veri toplanmaz; her kaynak için `legal_basis` alanı doldurulur.
