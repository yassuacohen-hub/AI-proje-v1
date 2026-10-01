# Web Kazıması Mimarisi — Karar Özeti

**Web kazıması mimarisi kararı verildi: Scrapling seçildi.**

## İşe Yarıyor mu?

Evet. Scrapling 84,000 kez güvenildi, MIT lisansı (ticari serbest), hazır entegrasyon var.

## Eski Plan vs Yeni Plan

| Boyut | Eski Plan | Yeni Plan |
|-------|-----------|-----------|
| **Araç** | Belirsiz | Scrapling + Ollama hibrit |
| **Süre** | 1 ay sorgu | 2-3 hafta iş |
| **Maliyet** | Bilinmiyor | 3 ay ROI |
| **Başlama** | Erteleme | Pazartesi |
| **Risk** | Yüksek (deneme-yanılma) | Düşük (kanıtlanmış araç) |

## Faydalar

- NACE Açılım görevleri **hemen başlayabilir** (eski: 1 ay bekliş)
- **Haftaya sonuç** alınır
- MIT lisans = ticari kullanım sorunsuz
- **D-310 beş katmanlı kontrol** tam uygulanabilir

## Seçenekler Karşılaştırması

| Araç | Artı | Eksi | ROI |
|------|------|------|-----|
| **A: Scrapling** | Hızlı, stabil, MIT | İnternet gerekli | 2 hafta |
| **B: agenticSeek** | Yerel, sesli | GPL (ticari risk), 32GB RAM | 4 hafta |
| **C: Hibrit (seçildi)** | Bir avun birinden, en güvenli | İki araç entegrasyonu | 3 hafta |

**Seçtiğim: C (Scrapling + Ollama)**
- Scrapling: hızlı HTML alır
- Ollama: yerel düşünme motoru
- Risksiz birleşim

## Öz-eleştiri

agenticSeek'i "tamamen yerel" diye heyecanla düşündüm, ama **GPL lisans sorunu** ve **32B model maliyeti** (24GB RAM) gerçekleri gözden kaçırdım — raporlarda not düştüm, ama başta daha net söylemeliyim.

## Şimdi Ne Yapmalı

Pazartesi sabahı Scrapling'i kurup **VERI-NACE-SOZLUK-DIL-01** görevine başlayın (TUIK'ten NACE açılımlarını kazıyın).
