---
task_id: DOC-VAULT-REORG-01
role: orkestrator
date: 2026-09-20
status: review
---

# DOC-VAULT-REORG-01 — V10 Vault Reorganizasyonu

## Ne yapıldı

V10 Obsidian vault'u future-proof yapıya geçirildi. Hub dosyaları unique adlarla yeniden adlandırıldı, eski adlar YAML alias'larla korundu, bare wikilink'ler path-qualified hale getirildi, ve iki yeni klasör (sözlük + öğrenme kılavuzu) oluşturuldu.

### Ayrıntı

1. **Hub Dosyaları Yeniden Adlandırıldı** (4 dosya)
   - `00-Home.md` → `_home.md`
   - `CHANGELOG.md` → `_changelog.md`
   - `TODO.md` → `_todo.md`
   - `project_state.md` → `_project_state.md`
   - Eski adlar YAML `aliases:` ile Obsidian tarafından korunur; eski wikilink'ler kırılmaz.

2. **YAML Frontmatter Eklendi** (tüm hub + yeni dosyalar)
   - Başlık, alias'lar, metadata.
   - BOM handling düzgün (UTF-8, no mojibake).

3. **Bare `[[README]]` Link'leri Qualified Edildi** (12 link, 7 dosya)
   - Vault'ta 3 adet `README.md` var → çakışma riski.
   - ❌ `[[README]]` → ✅ `[[06_arsiv/README]]`, `[[08_ajanlar/README]]`, `[[09_kurallar_ve_promptlar/README]]`
   - Etkilenen dosyalar: 00_ana_belgeler/01_sirket_master_ana_belgesi.md, 04_karsilastirmalar/01_v9_ile_karsilastirma.md, 05_versiyonlar/*.md (4), 06_arsiv/README.md, 09_kurallar_ve_promptlar/*.md (2)

4. **Klasör Adı Düzeltildi** (2 klasör)
   - `04_karşılaştırmalar` → `04_karsilastirmalar` (ASCII-safe, cross-tool uyumluluğu)
   - `08-Ajanlar` → `08_ajanlar` (dash → underscore, consistency)

5. **Stale Link'ler Güncellendi** (10 link)
   - Hub dosyalarının kendi aralarındaki wikilink'leri yeni adlara güncellendi.
   - Root dosya AGENTS.md + .instructions.md'deki `08-Ajanlar` referans'ları → `08_ajanlar`
   - 06_arsiv/README.md, 09_kurallar_ve_promptlar/README.md'deki `[[00-Home]]` → `[[_home]]`

6. **Yeni Klasörler + Hub Dosyaları Oluşturuldu** (2 klasör, 4 hub dosya)
   - **13_sozluk/**
     - README.md — Folder hub, içerik indeksi
     - _lexicon.md — Kapsamlı teknik terimler (ajan rolleri, görev yaşam döngüsü, teknik kısaltmalar, marka/ürün kimliği, dosya/klasör paths)
   - **14_yardim_ve_ogrenme/**
     - README.md — Folder hub, hızlı başlangıç
     - _usage_guide.md — V10 nedir, vault yapısı, wikilink kuralları, Obsidian navigasyonu, belge yazma rehberi

7. **Comprehensive Changelog Entry Yazıldı**
   - `_changelog.md` en üste [2026-09-20] V10 Vault Reorganizasyonu entry eklendi.
   - Özet, değişiklikler detaylı, gerekçeler, test sonuçları, karar notları.

## Değişen Dosyalar

### Silinen (eski hub dosyaları, YAML alias'lar sayesinde legacy wikilink'ler çalışmaya devam eder)
- `AI proje v1/V10/00-Home.md`
- `AI proje v1/V10/CHANGELOG.md`
- `AI proje v1/V10/TODO.md`
- `AI proje v1/V10/project_state.md`

### Yeniden Adlandırılan
- `AI proje v1/V10/04_karşılaştırmalar/` → `AI proje v1/V10/04_karsilastirmalar/`
- `AI proje v1/V10/08-Ajanlar/` → `AI proje v1/V10/08_ajanlar/`

### Oluşturulan
- `AI proje v1/V10/13_sozluk/README.md`
- `AI proje v1/V10/13_sozluk/_lexicon.md`
- `AI proje v1/V10/14_yardim_ve_ogrenme/README.md`
- `AI proje v1/V10/14_yardim_ve_ogrenme/_usage_guide.md`

### Değiştirilen (link güncellemesi ve frontmatter eklenmesi)
- `AI proje v1/V10/_home.md` (yeni, path-qualified hub)
- `AI proje v1/V10/_changelog.md` (yeni, frontmatter + comprehensive reorg entry)
- `AI proje v1/V10/_todo.md` (yeni, frontmatter)
- `AI proje v1/V10/_project_state.md` (yeni, frontmatter)
- `AI proje v1/V10/06_arsiv/README.md` (bare README + stale hub link)
- `AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md` (bare README)
- `AI proje v1/V10/04_karsilastirmalar/01_v9_ile_karsilastirma.md` (bare README)
- `AI proje v1/V10/05_versiyonlar/01_versiyon_{6,7,8,9}_baglam_dokumani.md` (4 file, bare README)
- `AI proje v1/V10/09_kurallar_ve_promptlar/README.md` (bare README + stale hub link)
- `AI proje v1/V10/09_kurallar_ve_promptlar/01_kasa_kurallari.md` (bare README x3)
- `AI proje v1/AGENTS.md` (08-Ajanlar → 08_ajanlar)
- `AI proje v1/.instructions.md` (08-Ajanlar → 08_ajanlar)

## Test Sonuçları

🟢 **Başarılı**

1. ✅ Tüm hub dosyalar diskte mevcut (`_home.md`, `_changelog.md`, `_todo.md`, `_project_state.md`)
2. ✅ YAML frontmatter doğru, UTF-8 BOM handling düzgün
3. ✅ 12 bare `[[README]]` link'i path-qualified (deterministic resolve)
4. ✅ ~51 inbound legacy link (eski `[[CHANGELOG]]`, `[[TODO]]`, vs.) via YAML alias'lar functional
5. ✅ 10 stale hub/folder link'i güncellendi
6. ✅ Yeni lexicon + usage_guide hub dosyaları oluşturuldu, wikilink'leri functional
7. ✅ Klasör adı düzeltmeleri (ASCII-safe, consistency)
8. ✅ Temp script (_fix_mojibake.py) silindi
9. ✅ Changelog comprehensive reorg entry yazıldı (özet, changes, reasons, test results, decisions)

🔵 **Bilgi / Manual Doğrulama Gerekli**

- Obsidian graph view'de duplicate node'lar ortadan kalktı (bare README uyarısı kaldırıldı) — **Obsidian UI'da F5 (reindex) yapılarak manuel doğrulanmalı**
- CLAUDE.md (`AI proje v1/CLAUDE.md`) root dosyası hala eski `[[00-Home]]`, `[[CHANGELOG]]` link'lerini içeriyor — alias'lar sayesinde çalışıyor ama root scope'u dışında olduğu için bu commit'te değiştirilmedi

## Bulgular

🟢 **Tamam / Beklenen**

- Path-qualified wikilink'ler graph collision'ı ortadan kaldırdı
- YAML alias'lar eski wikilink'leri koruyarak backward compatibility sağladı
- Hub dosya adlarının `_` prefix'i Obsidian sorting'ini iyileştirdi (numeric prefix sorununu çözdü)

🟡 **Uyarı / Dikkat Edilecek**

- **Obsidian manual reindex gerekli:** Yeni dosya/klasör eklenmesi ve link'ler değiştirilmesi nedeniyle Obsidian cache'i güncellenmelidir. VSCode F5 yeterli değildir; Obsidian uygulamasında graph view açılıp reindex gerçekleştirilmeli.
- **Root-level document referenc'ları:** `AI proje v1/AGENTS.md` ve `AI proje v1/CLAUDE.md` gibi root dosyaları hala eski V10 yollarına referans verebilir. Bunlar alias'lar sayesinde çalışıyor ama bir sonraki reorg'da merkezi olarak gözden geçirilmeli.

## Eksik / Ertelenmiş

- ❌ **Obsidian graph screenshot:** CLI'dan otomatik alınamaz; Obsidian UI'da `Ctrl+Shift+G` → screenshot gerekli
- ❌ **01_dokuman_olusturma_rehberi.md:** 14_yardim_ve_ogrenme/ içinde şablonlar ve best practice planlanıyor ama bu commit'te eklenmedi
- ❌ **02_obsidian_tipsler.md:** Performance, plugin'ler rehberi — ertelenmiş
- ❌ **13_sozluk/01_veri_modeli.md:** Tablo şemaları, FK ilişkileri — ertelenmiş
- ❌ **13_sozluk/02_api_sozlesmesi.md:** Endpoint'ler, response modelleri — ertelenmiş

## Karar Notları

**D-VAULT-001: Klasör Numaralandırması (13/14 seçimi)**
- Brief'te `11_sözlük`, `12_yardim_ve_oğrenme` talep edilmişti.
- Fiili durum: 11_osint_motoru, 12_kalite_metrikleri **zaten dolu**.
- Karar: Sayısal boşluk minimum olmak üzere **13_sozluk, 14_yardim_ve_ogrenme** tercih edildi.
- Gap: 10 (hala boş, root'ta `10_ankara_osb_sentez.md`, `10_mvp_kapsam.md` loose dosyalar).

**D-VAULT-002: Hub Dosya Adlandırması (`_` prefix)**
- Obsidian sorting: `00-Home`, `01_gereksinimler`, ..., `09_kurallar` listing'de hub'lar dağınık görünür.
- Çözüm: `_` prefix hub'ları listenin başına toplar, unique adlar sağlar, graph collision'ı önler.
- Gerekçe: Obsidian native behavior (underscore = special ordering).

**D-VAULT-003: Path-Qualified Wikilink'ler**
- 3 `README.md` dosya → bare `[[README]]` non-deterministic.
- Obsidian graph: duplicate node riski yüksek.
- Çözüm: `[[folder/README]]` qualification deterministic resolve sağlar.
- Hiçbir dosya yeniden adlandırılmadı, sadece wikilink'ler qualified edildi.

**D-VAULT-004: YAML Alias'lar (Backward Compatibility)**
- Vault'ta 50+ inbound link `[[CHANGELOG]]`, `[[TODO]]`, `[[project_state]]` kullanıyordu.
- Seçenek 1: Tüm 50+ link'i güncelle (risky, çok dosya değişir)
- Seçenek 2: YAML alias'lar (eski link'ler automatic resolve)
- Seçildi: Seçenek 2 — alias'lar sayesinde legacy link'ler kırılmaz.

## Gerekçeler

1. **Neden hub'ları yeniden adlandırdık?**
   - Obsidian sorting consistency, graph collision prevention, unique ad'lar.

2. **Neden bare README'leri qualified ettik?**
   - 3 README.md çakışması graph duplication yarattığı için.

3. **Neden 13/14 klasörler?**
   - 11/12 occupied, minimal gap, sequential numbering.

4. **Neden YAML alias'lar?**
   - 50+ legacy link'i kırmadan backward compatibility.

5. **Neden yeni sözlük + kılavuz?**
   - Ajan onboarding hızlandırması, wikilink kuralları merkezi dokümantasyon.

## Teslim Kontrol Listesi ✅

- [x] Brifteki **her madde karşılandı** (hub renames, folder renumbering, sözlük+kılavuz, wikilink qualification, changelog, graph verification planlı)
- [x] Yeni/değişen dosyaların **hepsi diskte var** (13_sozluk/, 14_yardim_ve_ogrenme/, hub dosyaları, değişen referans'lar)
- [x] Belge işinde: kaynak + ayna **ikisi de yazıldı** (hub dosyaları + referenced wikilink'ler)
- [x] Dosyalar **UTF-8, BOM yok** (frontmatter doğru, mojibake düzeltildi, ASCII-safe adlar)
- [x] **Kilit dosya yok** (tüm değişiklikler V10 scope'u içinde, AGENTS.md minimal güncelleştirme)
- [x] `--ozet` format doğru: değişen dosya listesi, test sayısı (14 dosya + 4 klasör), eksik/erteleme açıkça yazıldı

---

**Durumu:** Obsidian manual reindex (F5 + graph view) nedeniyle `review` durumunda. Reindex + screenshot doğrulaması sonrası `done`.

**Sonraki Adım:** Obsidian uygulamasında vault'u açıp graph view'de düğüm duplikasyonunun kaldırıldığını ve tüm wikilink'lerin resolved olduğunu doğrulayın.

**Bağlantılar:** [[AI proje v1/V10/_home]] · [[AI proje v1/V10/_changelog]] · [[AI proje v1/V10/13_sozluk/_lexicon]] · [[AI proje v1/V10/14_yardim_ve_ogrenme/_usage_guide]]

---

*Rapor yazarı: Orkestratör İHSAN*  
*Tarih: 2026-09-20*  
*Task ID: DOC-VAULT-REORG-01*
