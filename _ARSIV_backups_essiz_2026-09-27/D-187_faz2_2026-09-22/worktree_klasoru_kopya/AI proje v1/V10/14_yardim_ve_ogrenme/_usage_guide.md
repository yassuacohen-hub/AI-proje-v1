---
aliases:
  - Usage Guide
  - Kullanım Kılavuzu
  - Wikilink Kuralları
title: V10 Kullanım Kılavuzu
---

# V10 Kullanım Kılavuzu

## V10 Nedir?

V10, proje bağlamı, mimari, özellikler, kararlar, araştırma, görevler ve ajan yapısını tek bir Obsidian vault'unda yöneten merkezi belge deposu.

**Ana Hub:** [[_home]]

## Vault Yapısı

V10 şu klasörleri içerir:

| Klasör | Amaç |
|--------|------|
| `00_ana_belgeler/` | Proje gereksinimi, mimari belgeler, ana kaynaklar |
| `01_gereksinimler/` | MVP gereksinimleri, kullanıcı hikayeleri |
| `02_is_modeli/` | İş mantığı, iş akışları, veri toplama modeli |
| `03_mimari/` | Sistem mimarisi, bileşen diyagramları, ETL mimarisi |
| `04_karsilastirmalar/` | Versiyon karşılaştırmaları, V9 vs V10 analizi |
| `05_versiyonlar/` | Versiyon bağlam belgeleri, sürüm notları |
| `06_arsiv/` | Eski/arşivlenmiş belgeler, geçmiş belgeler |
| `07_referanslar/` | Harici kaynaklar, envanterler, araştırmalar |
| `08_ajanlar/` | Ajan roller, protokoller, görev tanımları |
| `09_kurallar_ve_promptlar/` | Çalışma kuralları, prompt kütüphanesi, standartlar |
| `11_osint_motoru/` | OSINT scraper mimarisi, orkestratör, iş akışı |
| `12_kalite_metrikleri/` | Kalite skorları, metrikler, izleme |
| `13_sozluk/` | Teknik terimler, ajan rolleri, tanımlamalar |
| `14_yardim_ve_ogrenme/` | Rehberler, öğrenme kaynakları, şablonlar |

## Wikilink Kuralları

### Temel Kural

Obsidian wikilink'ler `[[filename]]` veya `[[folder/filename]]` formatında yazılır.

### Çakışan Adlar — Path Qualification

Birden fazla `README.md` var olduğunda (6_arsiv, 08_ajanlar, 09_kurallar, vs.), bare `[[README]]` belirsiz kalır. **Çözüm: path-qualified wikilink kullan.**

❌ Yanlış (belirsiz):
```
[[README]]
```

✅ Doğru (nitelikli):
```
[[06_arsiv/README]]
[[08_ajanlar/README]]
[[09_kurallar_ve_promptlar/README]]
```

### Eski Adlar ve Alias'lar

Hub dosyaları yeniden adlandırıldı, ancak eski adlar YAML `aliases:` ile korunur:

| Eski Ad | Yeni Ad | Alias Yönetimi |
|---------|---------|-----------------|
| `00-Home.md` | `_home.md` | `aliases: [00-Home, home, vault-hub]` |
| `CHANGELOG.md` | `_changelog.md` | `aliases: [CHANGELOG, changelog]` |
| `TODO.md` | `_todo.md` | `aliases: [TODO, todo]` |
| `project_state.md` | `_project_state.md` | `aliases: [project_state, project-state]` |

**Sonuç:** Eski `[[CHANGELOG]]` link'leri bile yeni dosyaya resolve olur.

### Link Örnekleri

**Hub dosyaları:**
```
[[_home]]         — Ana hub
[[_changelog]]    — Değişiklik günlüğü
[[_todo]]         — Görev panosu
[[_project_state]] — Proje durumu
```

**Klasör dosyaları (path-qualified):**
```
[[06_arsiv/README]]
[[08_ajanlar/README]]
[[13_sozluk/_lexicon]]
[[14_yardim_ve_ogrenme/_usage_guide]]
```

**Aynı klasördeki dosya (bare, çünkü unique):**
```
[[01_veri_kaynagi_envanteri]]    — 07_referanslar içinde unique ad
[[01_sirket_master_ana_belgesi]] — 00_ana_belgeler içinde unique ad
```

## Yeni Belge Yazma

1. Doğru klasörü seçin (`01_gereksinimler/` vs `03_mimari/`).
2. Dosyaya YAML frontmatter ekleyin:
   ```yaml
   ---
   aliases:
     - Alternatif Ad
   title: Uzun başlık
   ---
   ```
3. İlk satır: `# Başlık`
4. İkinci satır: `Bağlantılar: [[_home]] · [[14_yardim_ve_ogrenme/README]] · [[_changelog]]`
5. İçerik yazın.
6. Yeni wikilink'ler her zaman path-qualified yazın.

## Obsidian Vault Navigasyonu

### Graph View (Ctrl+Shift+G)
- Tüm dosyaları ve ilişkilerini görüntüler.
- Bare `[[README]]` yanlış kullanmak **duplicate node** yaratır.
- Path-qualified link'ler (örn. `[[06_arsiv/README]]`) unique node'lar oluşturur.

### Search (Ctrl+Shift+F)
- Metin ara.
- "wikilink:" prefix'i ile link arama: `wikilink:[[_home]]`

### Quick Open (Ctrl+P)
- Dosya adı yazarak aç.

## Eksik/Ertelenmiş Bölümler

Vault'un gelecek sürümleri şunları içerecektir:

- `01_dokuman_olusturma_rehberi.md` — Şablonlar ve best practice
- `02_obsidian_tipsler.md` — Plugin'ler, plugin'ler, performans
- `13_sozluk/01_veri_modeli.md` — Tablo şemaları, foreign key ilişkileri
- `13_sozluk/02_api_sozlesmesi.md` — Endpoint'ler, response modelleri

## Sorular ve Destek

- Wikilink kuralları hakkında: bu sayfayı (`_usage_guide.md`) okuyun.
- Teknik terimler: [[13_sozluk/_lexicon]] bölümüne bakın.
- Yaşanan sorunlar: [[_changelog]] ile eşleştirilmiş [[_todo]] kontrol edin.

---

**Bağlantılar:** [[_home]] · [[13_sozluk/README]] · [[_changelog]]
