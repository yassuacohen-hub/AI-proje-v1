[[Huginn Data Insights/data/orchestrator/VAULT-BIRLESTIME-PLAN-01_strateji_2026-09-20_orkestrator.md]]

# Vault Birleştirme & Bakım Planı

**Tarih:** 2026-09-20  
**Durum:** Tarama tamamlandı, strategi raporu (silme yok, öneri modunda)  
**Karar Beklemede:** Kullanıcı onayı

---

## Tarama Sonuçları

| Metrik | Öncesi (gürültülü) | Sonrası (filtered) |
|--------|-------------------|-------------------|
| Toplam `.md` | 4442 | 1114 |
| Duplike grup | 424 | 332 |
| Duplike dosya | 3506 | 955 |
| Orphan nod | ? | 916 |

`.obsidian/app.json` userIgnoreFilters ayarı **aktif** (`.kilo/.agents/.claude/venv/node_modules/...`). Graph'ta gözüküyor: 1114 dosya.

---

## 3 Katman Sorun Tespiti

### 1️⃣ Vendor & venv Kontaminasyonu (~80 dosya)

**Sorun:** `.venv/Lib/site-packages/` içindeki 3. taraf Python paketleri `README.md`, `LICENSE.md`, `CHANGELOG.md` ile vault taranıyor.

- 41 × `readme.md` — plotly, altair, pyarrow, httpx, numpy, ...
- 19 × `license.md` — pip, numpy, starlette, uvicorn
- ~12 × vendor-specific (skipped)

**Sebep:** `.venv` OS-agnostic glob pattern içine göremez. Obsidian `.venv\Lib\site-packages\*` şeklinde açılı path bakıyor, `*.venv\...` değil.

**Strateji:**
- [ ] `.obsidian/app.json` içine `"venv"`, `"site-packages"`, `.dist-info` ekle (path component bazında)
- [ ] Sonrası: ~80 dosya graph'tan düşecek

---

### 2️⃣ "AI proje v1" Duplikası (~200-300 dosya)

**Sorun:** Repo kökünde 2 ayrı git branch yönetimi var — `Huginn Data Insights/` ve `worktree klasoru/`. İçeriği birebir. Ek olarak:
- `Huginn Data Insights/AI proje v1/`
- `worktree klasoru/AI proje v1/`

Her klasörde:
```
AGENTS.md ✓ (2x)
CLAUDE.md ✓ (2x)
CHANGELOG.md ✓ (2x)
docs/plans/*.md ✓ (10x)
data/skills/supabase-postgres-best-practices/ ✓ (5x aynı referans)
```

**Sebep:** Git worktree veya branch merge geçmişi. Aktif çalışma `worktree klasoru/`'de, eski `Huginn Data Insights/AI proje v1/` arşiv olabilir.

**Strateji:**

| Seçenek | Detay | Risk |
|---------|-------|------|
| **A) Arşiv Kapatma** | `Huginn Data Insights/AI proje v1/` tümüyle `.obsidian/app.json` ignore et | Tarama geçmişine ihtiyaç yoksa güvenli |
| **B) Symlink Birleştirmesi** | `Huginn Data Insights/AI proje v1/` → `worktree klasoru/AI proje v1/` (git submodule/symlink) | Git state kompleks olabilir |
| **C) Tutuştur** | Her iki branch da aktif sayıl, manual cross-reference yönlendir | Bakım yükü yüksek |

**Tavsiye:** **A) Arşiv Kapatma** — Sprint 2'de aktif git branch sadece `worktree klasoru/` olacak, eski V10 referanslar D-169 karar olarak AGENTS.md'ye yazılmalı.

---

### 3️⃣ Orphan Nodlar (916 dosya)

**Sorun:** 916 dosya hiçbir başka nod tarafından link alınmıyor.

**Analiz:**
- **Beklenilen orphan:** Kök notlar (`README.md`, `AGENTS.md` — başkası onları link almasa da "giriş" sayılıyor)
- **Gerçek orphan:** Eski döküman, arşiv, yanlış isim (typo), yüksekliğe erişilemeyen notlar

**Örnek Orphan Taraması:** Raporda ilk 30:
```
Huginn Data Insights/.venv/.../*.md   (~50 vendor)
worktree klasoru/AI proje v1/docs/... (eski branch)
... (detaylı liste raporunun 171-200 satırları)
```

**Strateji:**
- [ ] **Manuel İnceleme İlk 20 Orphan:** Silecek mi, vault haritasına ekleyecek mi?
- [ ] **"Arşiv" Klasörü İçi:** `_archive/`, `old/`, `deprecated/` klasörlerdeki orphan'lar natural, saklı tutulabilir
- [ ] **Silme Yasağı:** Bu turda hiç silme yok; silme görev olarak açılmalı, kontrolör (YASU) onaysız çalışmaz (D-162)

---

## Adım Adım Uygulama Planı (ONAY SONRASI)

### Tur 1: Gürültü Temizleme (Rung 1: Ayar)

1. `.obsidian/app.json` genişlet:
   ```json
   {
     "userIgnoreFilters": [
       ".kilo/", ".agents/", ".claude/", ".cursor/", ".continue/",
       ".kombai/", ".vscode/", ".pytest_cache/", "node_modules/",
       ".git/", "venv/", "site-packages/", ".venv/", ".dist-info/",
       "Huginn Data Insights/AI proje v1/"
     ]
   }
   ```

2. Sonrası graph: 1114 → ~800 dosya (vendor+arşiv düşer)

### Tur 2: Duplike Strateji (Rung 6: Kod)

3. Her duplike grup için (JSON rapordan):
   - `agents.md` (5 dosya) → master: `worktree klasoru/AGENTS.md`, yönlendir: `Huginn Data Insights/AGENTS.md` → masterine link yap
   - `brief_dashboard-01.md` (10 dosya) → master: `worktree klasoru/workspace/external/*/brief_DASHBOARD-01.md`, konsolide et
   - `_contributing.md` (5 dosya) → skill referansı, yalnız mastera link yap

4. Birleştirme sonrası cross-reference düzeltme (internal link `[[...]]` ve `[...](...)` regex ile güncelle)

### Tur 3: Orphan Kararı (D-169 yeni karar)

5. İlk 20 orphan elle incelenecek (yeni karar D-169)
6. Kalan orphan'lar otomatik kural ile sınıflandırılacak (arşiv vs silinecek)

---

## Yedek Durumu

**Git:** `git status` temiz, tüm değişiklikler tracked. Revert komutu hazır.

**Off-disk Yedek:** Gerekli değil — `.kilo/` ve `.agents/` zaten git-excluded, `.venv/` ignored. Ana notlar `worktree klasoru/` içinde git-tracked.

---

## Risk & Mitigasyon

| Risk | Olasılık | Mitigation |
|------|----------|-----------|
| Cross-reference bozulması | Yüksek | Regex test scriptini yazıp dry-run et, sonra manuel review |
| Yanlış dosya silmesi | KONTROL: silme YOK bu turda | İzin istenmeden silme yok |
| Graph'ta hala gürültü | Orta | userIgnoreFilters tam path bazında, glob değil — test sonrası elden geçir |

---

## Kullanıcı Kararı Gerekli

**Bu rapor öncesi sorulan sorular:**

1. **Vendor/venv Kapatma:** `Huginn Data Insights/.venv/` + `.dist-info/` klasörleri vault dışı mı sayılsın? → **YES/NO**
   
2. **AI proje v1 Arşivlemesi:** `Huginn Data Insights/AI proje v1/` tütünü arşiv mı sayılsın? Yoksa her iki branch da etkin tutulunsun? → **ARCHIVE/KEEP**

3. **Orphan İşlemi:** İlk 20 orphan'ı bu turda inceleyip klasifiye etmek mi, yoksa sonraki turda? → **INSPECT_NOW/LATER**

**Onay Sonrası:** D-169 kararı AGENTS.md'ye yazılır, uygulama başlanır.

