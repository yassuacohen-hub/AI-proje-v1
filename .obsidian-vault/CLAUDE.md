# CLAUDE.md

## Proje Amacı
Bu proje, kurumsal veri güvenliği ve sentetik veri tasarım alanında çalışan bir AI destekli platformdur.

## Temel İlkeler
- Her yeni çalışmada önce bağlamı oku: amaç, hedef, kısıtlar, kullanım senaryosu.
- Kod yazmadan önce problemi net tanımla.
- Her değişiklik için kısa açıklama yaz.
- Çözüm üretirken kullanıcı deneyimi, güvenlik ve sürdürülebilirlik önceliklidir.
- Güvenli veri, sahte/uyumlu sentetik veri ve kalite kontrolü birlikte düşünülür.

## Proje Mimarisi
- `src/` uygulama kodlarını içerir.
- `tests/` doğrulama testlerini içerir.
- `AGENTS.md` proje kurallarını tanımlar.
- `.obsidian-vault/` proje hafıza ve not yönetimi için kullanılır.

## Çalışma Yöntemi
1. Hedefi netleştir.
2. Mevcut bağlamı ve dosyaları oku.
3. Kısa plan çıkar.
4. En küçük doğru çözümü uygula.
5. Test et ve raporla.

## Not Yönetimi
- Özellik planları `03-Specifications/` içinde tutulur.
- Mimari kararlar `04-ADR/` içinde tutulur.
- Hatalar `05-Bugs/` içinde kaydedilir.
- Araştırmalar `06-Research/` içinde saklanır.

## Sık Kullanılan Komutlar
- `python -m unittest`
- `python src/main.py`

## Sonraki Adım
Yeni projelerde bu yapı korunur: proje hafızası + kod + kurallar + şablonlar birlikte çalışır.
