# AI Second Brain - Project Memory

Bu proje için kullanılacak hafıza yapısı ve çalışma akışı:

## Klasör yapısı

- `00-Home.md` - Ana giriş notu
- `01-Context/` - Proje bağlamı, hedefler, kullanıcı ihtiyaçları
- `02-Architecture/` - Mimari kararlar, tasarım notları
- `03-Specifications/` - Özellikler, gereksinimler, spesifikasyonlar
- `04-ADR/` - Architecture Decision Records
- `05-Bugs/` - Hata/bug kayıtları
- `06-Research/` - Araştırma ve referans notları
- `07-Tasks/` - Yapılacaklar / backlog
- `templates/` - Şablon notlar

## Akış

1. Her yeni özellik için `templates/Spec-template.md` kullan.
2. Mimari karar değişikliklerinde `templates/ADR-template.md` kullan.
3. Bug/yanlış davranış için `templates/Bug-template.md` kullan.
4. Çalışma esnasında notları güncelle, AI’a bağlam sağla.
5. Her projede aynı zihinsel model kullan: Context → Spec → Architecture → ADR → Tasks → Bugs.

## Kullanım

- Obsidian üzerinden proje hafızasını yönet.
- VS Code içinde Copilot ile aynı notlar üzerinden çalış.
- Aynı şablon seti her yeni projede kopyalanıp kullanılır.
