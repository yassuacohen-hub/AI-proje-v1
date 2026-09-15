# Odin AI RAG İskeleti

## Ne İşe Yarar?
Odin AI RAG, metinleri yerel ve deterministik vektörlere dönüştüren, metinleri parçalayan (chunking) ve birleştiren hafif bir Python kütüphanesidir. Harici API anahtarı gerektirmez.

## Bileşenler

### Embedder
- `Embedder(boyut=16)` — SHA-256 hash tabanlı deterministik embedding
- `.embed(text: str) -> list[float]` — Aynı metin her zaman aynı vektörü üretir

### Chunk (dataclass, frozen)
- `icerik: str` — Parça metni
- `baslangic: int` — Orijinal metindeki başlangıç indeksi
- `bitis: int` — Orijinal metindeki bitiş indeksi
- `boyut: int` — Parça uzunluğu
- `ozet: str` — İlk 60 karakter

### chunk_metin(metin, boyut=200)
Metni örtüşen parçalara böler. `adim = boyut // 2` örtüşme sağlar.

### chunk_bol(metin, ayrac="\n\n")
Metni verilen ayraca göre böler, boş parçaları atlar.

### chunk_topla(chunklar)
Chunk'ları sıra ile birleştirir, örtüşen bölgeleri tekilleştirir.

## Nasıl Birlikte Çalışır?
1. `chunk_metin` ile metni parçalara ayır
2. Her `Chunk.icerik` için `Embedder.embed` ile vektör üret
3. Sorgu vektörü ile chunk vektörlerini karşılaştır (benzerlik)
4. İlgili chunk'ları `chunk_topla` ile birleştir

## Kısıtlamalar
- Harici API anahtarı yok — tamamen yerel
- Deterministik — aynı girdi her zaman aynı çıktı
- Embedding boyutu 16 (basitlik için)
- psutil gibi opsiyonel bağımlılık yok

## Kullanım Örneği
```python
from company_master.odin_ai.rag import Embedder, chunk_metin, chunk_topla

embedder = Embedder()
metin = "Uzun bir belge metni buraya gelir..."
chunks = chunk_metin(metin, boyut=200)
vektorler = [embedder.embed(c.icerik) for c in chunks]
# Benzerlik arama...
sonuc = chunk_topla(chunks[:3])
```
