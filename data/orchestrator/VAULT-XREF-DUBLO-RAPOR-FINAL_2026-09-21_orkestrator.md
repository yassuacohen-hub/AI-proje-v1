# VAULT-XREF-DÜZELT + DUBLO-BIRLES: Nihai Rapor

**Tarih:** 2026-09-21  
**Dosya:** VAULT-XREF-DUBLO-RAPOR-FINAL_2026-09-21_orkestrator.md  
**Format:** D-55 (raporlama standardı)  
**Durum:** ✓ TAMAMLANDI  

---

## 1. Hedefler ve Kapsamı

**Ana Görev:** Obsidian vault referans bütünlüğü ve ikiz dosya birleştirmesi

| Madde | İçerik |
|-------|--------|
| **Başlangıç Sorunu** | 955 ikiz dosya (332 grup), 916 orphan, ~1114 taranılan dosya |
| **Kök Neden** | 3 paralel git ağacı (repo + worktree + eski snapshot) + 4. parti kodlar aynı vault'ta indeksleniyordu |
| **Strateji** | v1 (elle canonical seç + redirect) vs v2 (ignore filter + hub note) |
| **Seçim** | v2: yalın, sürdürebilir, %85 token tasarrufu |
| **Canonical Ağaç** | `worktree klasoru/` (kullanıcı onayı) |

---

## 2. Uygulanan Çözüm (v2 Strateji)

### 2.1 ADIM 1: Obsidian Native Ignore Filter (Ladder Rung 3)

**Dosya:** `.obsidian/app.json`

```json
{
  "userIgnoreFilters": [
    ".venv/", ".kilo/", ".agents/", ".claude/", ".cursor/", ".continue/",
    ".kombai/", ".vscode/", ".pytest_cache/", "node_modules/", ".git/",
    ".roo/", ".obsidian/", ".github/",
    "Huginn Data Insights/", "AI proje v1/", "data_worktree/"
  ]
}
```

**Ağaçlar:**
- `worktree klasoru/.obsidian/app.json` → Huginn Data Insights + diğer ağaçları ignore
- `Huginn Data Insights/.obsidian/app.json` → worktree klasoru + diğer ağaçları ignore

**Etki:** 1114 dosya → 408 dosya (%63 azalma), ikiz 955 → 25 (%97 azalma)

### 2.2 ADIM 2: Vault Sağlık Script

**Dosya:** `worktree klasoru/scripts/vault_saglik.py`

```python
# Tek geçişte:
# - Kırık referans (hedefi olmayan link) tespit
# - İkiz grup (isim çakışması) tespit
# - Orphan nod (referans almayan dosya) tespit
# - Rapor (JSON) üret
# - Hub note (VAULT_HARITA.md) üret
```

**Kritik Düzeltme:** Path normalizasyonu
- **Sorun:** `file_map` anahtarları Windows `\`, wikilink'ler posix `/` kullanıyor
- **Hata:** 455 sahte kırık link (harita linklerinin çoğu)
- **Fix:** `relative_to().as_posix().lower()` + çapası kesme (`[[file#section]]` → `file`)
- **Sonuç:** 455 → 46 kırık link (%90 düzelme)

**Argümanlar:**
```bash
--rapor       # JSON rapor üret (varsayılan)
--harita      # VAULT_HARITA.md hub note üret
--duzelt      # Düzeltme önerileri
--dry-run     # Yazmadan göster
--uygula      # Değişiklikleri uygula (TODO)
--kontrol     # Exit 1 if kırık link
```

### 2.3 ADIM 3: Hub Note (Dizin Bazlı)

**Dosya:** `worktree klasoru/VAULT_HARITA.md`

```markdown
# VAULT_HARITA
> Otomatik üretim: `python scripts/vault_saglik.py --harita`

Vault = ajanların ortak hafızası. Bu dosya tüm nodlara giriş noktasıdır.

## (kok) (14)
[[AGENTS]], [[CLAUDE]], [[README]], ...

## data (47)
[[data/orchestrator/...]], ...

## data/orchestrator (35)
[[data/orchestrator/decision_log]], ...

...
```

**Etki:** Orphan 388 → 2 (%99 azalma)

---

## 3. Sonuçlar

### 3.1 Ölçülen Metrikler

| Metrik | Başlangıç | Ara (Sadece Filter) | Son (Filter + Script) | İyileşme |
|--------|-----------|---------------------|----------------------|----------|
| **Tarandı** | 1114 | 408 | 408 | %63 ↓ |
| **İkiz Grup** | 332 | 7 | 7 | %98 ↓ |
| **İkiz Dosya** | 955 | 25 | 25 | %97 ↓ |
| **Orphan** | 916 | 388 | 2 | %99 ↓ |
| **Kırık Link** | ✗ | 65 | 46 | %29 ↓ |

### 3.2 Kırık Link Analizi (46 adet)

**Kaynaklar:**
- `CLAUDE.md` → `[[00-Home]]`, `[[project_state]]`, `[[TODO]]` (3 benzersiz, 5+ duplike)
- `data/orchestrator/ALTYAPI-DOCS-MIGRATE-01_rapor` → `[[K1]]`, `[[K2]]`
- `data/orchestrator/DOC-VAULT-REORG-01_rapor` → `[[06_arsiv/README]]`, `[[08_ajanlar/README]]`, `[[09_kurallar_ve_promptlar/README]]`
- Diğer rapor dosyaları: 30+ ek hedef eksikliği

**Neden:** Eski rapor notasyon, referans hedefler silinmiş veya taşınmış.

### 3.3 İkiz Dosya Sınıflandırması (7 grup, 25 dosya)

| Grup | Dosya Sayısı | Tür | Karar |
|------|--------------|-----|-------|
| `readme.md` | 9 | Modül-spesifik | Kasıtlı ikiz, birleştirme riski |
| `brief*.md` | 5 | Ajan-spesifik | Kasıtlı ikiz, müstakil tutulmalı |
| `agent_sync.md` | 2 | Root + `data/orchestrator/` | Senkron çıktısı, canonical seç |
| `gorev_panosu.md` | 2 | Root + `data/orchestrator/` | Senkron çıktısı, canonical seç |
| `night_shift_report.md` | 2 | Root + `data/orchestrator/` | Senkron çıktısı, canonical seç |

**Gerçek İkiz (3 çift):** Senkron script tarafından kopyalanan dosyalar → canonical seçimi + redirect gerekli.

### 3.4 Orphan (2 adet, %99 çözüldü)

| Dosya | Boyut | Tür |
|-------|-------|-----|
| `.instructions.md` | 4.6 KB | Konfigürasyon, linklenmeyen |
| `VAULT_HARITA.md` | 34.8 KB | Hub note, kendini linklemen (yapılmayacak) |

---

## 4. İlgili Kararlar

### D-174: VAULT Sağlığı Altyapısı
- **Tarih:** 2026-09-21
- **İçerik:** canonical ağaç + ignore filter + sağlık script
- **Durum:** ✓ Yürürlükte

### D-175: Elle Düzeltme Stratejisi (Beklemede)
- **Hedef:** 46 kırık link + 3 ikiz çift manuel çözüm
- **Yöntem:** Kullanıcı onayı sonrası `--duzelt --uygula` modunda otomatik fix

---

## 5. Dosyalar

| Dosya | İçerik |
|-------|--------|
| `worktree klasoru/scripts/vault_saglik.py` | Ana sağlık script |
| `worktree klasoru/VAULT_HARITA.md` | Hub note (407 nod, 49 dizin) |
| `data/orchestrator/VAULT-SAGLIK-01_rapor_2026-09-21_orkestrator.json` | Detaylı rapor (46 kırık, 7 grup, 2 orphan) |
| `worktree klasoru/.obsidian/app.json` | Canonical ağaç ignore filter |
| `Huginn Data Insights/.obsidian/app.json` | HDI ağaç ignore filter |
| `worktree klasoru/scripts/D174_vault_saglik_karar.py` | D-174 karar kaydı |
| `plans/VAULT-XREF-DUBLO-PLAN_2026-09-21.md` | v2 strateji planı |

---

## 6. Sonraki Adımlar

### İhmal edilen riskler (D-162 silme yasağı uyarı)
- Elle link düzeltme veya ikiz silme kontroller aşamasında `--kontrol` bayrağı kullan
- Yedek: `data/orchestrator/` raporunda 46 kırık link + 3 ikiz grup döküm var

### Devam eden işler
1. **D-175:** 46 kırık link elle fix (CLAUDE.md, rapor notalar)
2. **D-176:** 3 ikiz çift birleştirme stratejisi (senkron çıktıları)
3. **D-177:** Senkron script inceleme (`senkron_fark.py`, `senkron_append.py`) — hangi ağaç canonical olmalı

### Kazanç Özeti
- **Vault sağlık:** Ajan tek hub notadan tüm vault'a erişir
- **Bakım kolaylığı:** Yeni ağaç/araç eklenmesi ignore filter'a 1 satır ekleme (elle seçmek yerine)
- **Token tasarrufu:** v1 (955 redirect yazısı) vs v2 (1 ayar dosyası) → ~%85 maliyet azalması
- **Doğruluk:** Kırık link 455→46 (path normalizasyonu)

---

## 7. Teknik Notlar

**Path Normalizasyonu Hatasının Kökeni:**
```python
# Yanlış:
file_map = {str(p.relative_to(ROOT)).lower(): p}  # Windows: "data\orchestrator\x.md"
# Wikilink: [[data/orchestrator/x]]  # POSIX

# Doğru:
file_map = {p.relative_to(ROOT).as_posix().lower(): p}  # "data/orchestrator/x.md"
```

**Obsidian #Heading Çapası:**
```python
# Obsidian destekler: [[dosya#Başlık]]
hedef = hedef.split('#')[0].strip()  # Başlık kısmı kaldır
```

**Unicode Sorunları (Windows cp1254):**
```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # Emoji yazdırma
```

---

## İmza

**Hazırlayan:** orkestrator  
**Onay Beklemede:** (kullanıcı)  
**Dosya ID:** VAULT-XREF-DUBLO-RAPOR-FINAL_2026-09-21_orkestrator.md
