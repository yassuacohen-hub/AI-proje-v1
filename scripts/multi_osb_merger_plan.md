# Multi-OSB Veri Birleştirme Planı

## Hedef
Tüm Ankara OSB firmalarını tekilleştirip temiz bir veri seti oluşturmak.

## OSB Listesi ve Durum
- OSTİM: 8.313 firma (data/ostim/firmalar_full.jsonl) - Devam eden scrape
- İvedik: ~3.000 firma (data/ivedik/) - Hazır değil
- ASO 1: ~2.000 firma (data/aso1/) - Hazır değil
- ASO 2-3: ~1.500 firma (data/aso23/) - Hazır değil
- Başkent: ~1.500 firma (data/baskent/) - Hazır değil
- Diğer OSB: ~2.000+ firma (Anadolu, HAB, vb.)

## Toplam Hedef
~19.000+ Ankara B2B firması

## Birleştirme Süreci
1. Veri Toplama: Tüm OSB lerden firma listelerini JSONL formatında topla
2. Temizleme: Duplicate kaldır (unvan + adres + web kombinasyonu)
3. Zenginleştirme: VKN/TC Kimlik No (footer scraping), telefon, e-posta, sektor
4. Kalite Skoru: Veri tamamlama oranına göre hesapla
5. Tekilleştirme: Fuzzy matching ile benzer unvanları birleştir

## Teknik Detaylar
- Anahtar: unvan (lowercase, trim) + adres (ilk 50 karakter)
- Benzerlik: difflib.SequenceMatcher ratio > 0.85
- Öncelik: Veri tamamlama orani yüksek olan kaydı tut

## Ajan Görevleri
- Web Kazıma Uzmanı: Her OSB için 30 dakikalık masa başı analizi (robots.txt, KVKK, rate limit)
- Geliştirici Ajan: JSONL birleştirici script yaz (multi_osb_merger.py)
- Kalite Ajan: Duplicate ve benzerlik tespiti için validator
- Mimar Ajan: Unified şema tasarımı

## Notlar
- İlk aşamada sadece OSTİM tamamlanacak (veri kalitesi %3.88 → hedef %50+)
- Footer VKN extraction ile vergi_no doluluk hedefleniyor
- Sonraki aşamada MERSİS/Ticaret Sicili API entegrasyonu

## Bağlantılar
- 08_gib_vergino_sorgu_stratejisi.md
- 06_web_kazima_uzmani.md (Yeni Strateji bölümü)
- data/ostim/firmalar_detayli.jsonl (Devam eden scrape)
