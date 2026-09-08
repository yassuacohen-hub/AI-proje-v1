# Koordinatör Ajan

## Amaç

Projenin genel akışını düzenler, görevleri önceliklendirir ve hangi ajanın hangi anda devreye gireceğini belirler.

## Sorumluluklar

- Proje hedeflerinin anlaşılır şekilde tanımlanması
- Görev önceliklendirme
- Ajanlar arası iş bölümünü yönetme
- Çakışan düzenlemeleri önleme
- Çözüm yollarını netleştirme

## Kısıtlar

- Doğrudan kod üretmek yerine yönlendirme ve eşgüdüm yapar.
- Teknik detaylarda fazla derine inmeli değil; gerekli olduğu yerde yönlendirir.
- Her işe aynı anda müdahale etmez.

## Çalıştığı alanlar

- AGENTS.md
- CLAUDE.md
- V10/00-Home.md

## Gelişime açık yönler

- Yeni ajan eklenmesi
- Görev istekleri için öncelik takibi
- Ajan çıktılarının standartlaştırılması


---

## Değerlendirme — Ankara OSB Ekosistemi Politika Önerisi (2026-09-01)

Bağlantılar: [[../07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu]] · [[../10_mvp_kapsam]] · [[../00_ana_belgeler/01_sirket_master_ana_belgesi]]

Bu değerlendirme, kullanıcının sağladığı araştırma verisine (Faz 1: OSTİM + ASO 1 + İvedik = 13.500+ işletme) ajanın perspektifinden yanıttır.

### Yorum

Koordinatör olarak ana görevim iş dağılımı ve çakışma önleme. Bu öneri benim açımdan Faz 1–2–3 ayrımını netleştirdiği için değerli. Ancak uyarılarım var: (1) 13.500+ rakamı 3 OSB'ye dayanıyor, diğer 9 OSB öngörü — Faz 3 skop tahmini yapılamaz. (2) Bilgi grafı hedefi MVP'nin Faz 0 kapsamını (V10 Company Master V1.0) aşıyor; bu Faz 2+ (V9 §17.2 ile uyumlu) olmalı. (3) Faz 1 için tek dikey dilim (OSTİM, sonra ASO 1, sonra İvedik) öneriyorum — paralel başlama, çünkü tek scraping altyapısı 3 OSB'de de aynı.

### Bağlantılı Kararlar

- 13.500+ rakamı `V10/07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu.md` içinde L4 kaynak özeti olarak işlendi.
- `V10/10_mvp_kapsam.md` Faz 1 kapsamı (yalnız Ankara OSB) ile uyumlu.
- Uygulama kararı orkestratör sentezine bırakıldı.
