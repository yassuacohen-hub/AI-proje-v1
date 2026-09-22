# GRAPH-KOPRU-01 / GRAPH-ARSIV-01 — Uygulama Raporu

**Tarih:** 2026-09-21 · **Uygulayan:** Orkestratör · **Durum:** ✅ TAMAMLANDI (test suite bilerek çalıştırılmadı)

---

## 1. GRAPH-KOPRU-01 — Karar ↔ Kod ↔ Test Wikilink'leri (D-182 örneği)

**Not:** Brief'te D-182 rapor dosyasının adı `D-182_mimir_anahtar_donusumu_raporu.md` olarak yazılıydı; `list_files` ile doğrulandı, dosya bu adla mevcuttu (planın belirttiği `D-182_MIMIR_UYGULAMASI_RAPOR_2026-09-21.md` adı **yanlıştı**, gerçek dosya kullanıldı).

### Değiştirilen Dosyalar

| Dosya | Eklenen |
|---|---|
| [`src/company_master/ai_chat.py`](worktree klasoru/src/company_master/ai_chat.py:8) | `Karar: [[D-182]]`, `Test: [[tests/test_d182_mimir.py]]` |
| [`scripts/gorev_at.py`](worktree klasoru/scripts/gorev_at.py:12) | `Karar: [[D-182]]` |
| [`web_dashboard/tabs/abrakadabra.py`](worktree klasoru/web_dashboard/tabs/abrakadabra.py:17) | `Karar: [[D-182]]`, `Test: [[tests/test_d182_mimir.py]]` |
| [`tests/test_d182_mimir.py`](worktree klasoru/tests/test_d182_mimir.py:6) | `Karar: [[D-182]]` + 3 implementasyon wikilink (`ai_chat.py`, `trigger.py`, `gorev_at.py`) |
| [`data/orchestrator/D-182_mimir_anahtar_donusumu_raporu.md`](worktree klasoru/data/orchestrator/D-182_mimir_anahtar_donusumu_raporu.md:307) | `**Referanslar:**` bloğu — 6 wikilink (4 kod dosyası + test + `AGENTS.md#MIMIR`) |

### Doğrulama
`search_files` ile `\[\[D-182\]\]` taraması: **11 eşleşme**, 4 kod dosyasında (ai_chat.py, gorev_at.py, abrakadabra.py, test_d182_mimir.py) + rapor dosyasında + plan/brief referans dosyalarında. Beklenen 4 kod dosyası eşleşmesi ✅ sağlandı.

---

## 2. GRAPH-ARSIV-01 — Graph Gürültü Filtresi (düşük öncelik, opsiyonel)

D-177 kararına göre graph **Huginn Data Insights** vault'undan okunuyor; asıl düzenlenen dosya [`Huginn Data Insights/.obsidian/app.json`](Huginn Data Insights/.obsidian/app.json:1).

**Envanter çıkarımı:** `data/orchestrator/` altında `list_files` ile gerçek dosya listesi tarandı (150+ dosya): `*_result.json`, `*_rapor_*.md`, `*_bulgular_*.md`, `.backup_*`, `.log`, `.key`, `.pid` gibi kalıplar tespit edildi.

**Önemli düzeltme (öneri):** Obsidian `userIgnoreFilters` **glob (`*`) desteklemez** — yalnız düz path-prefix substring veya `/regex/` (yavaş satır ile sarılı regex) kabul eder. Brief'teki `"*.json"` gibi kalıplar **çalışmaz**; bu yüzden regex formuna çevrildi:

```json
"/data\\/orchestrator\\/.*\\.(json|jsonl)$/",
"/data\\/orchestrator\\/_.*/",
"/_rapor_.*\\.md$/",
"/_bulgular_.*\\.md$/",
"/\\.(backup|yedek)_\\d+/",
"/\\.log$/",
"/\\.(pid|key|db|coverage)$/"
```

Mevcut filtreler (`.venv/`, `.git/` vb.) korundu, tekrar eklenmedi. `.obsidian/app.json` (root vault) değiştirilmedi — sadece HDI mirror'ı güncellendi (D-177 uyumu).

---

## 3. AGENTS.md Güncellemeleri

D-182 bölümünün hemen altına, aynı formatta (`## Başlık (D-XXX — KAHİN kararı 2026-09-21)`) iki yeni bölüm eklendi — hem [`worktree klasoru/AGENTS.md`](worktree klasoru/AGENTS.md:75) hem [`Huginn Data Insights/AGENTS.md`](Huginn Data Insights/AGENTS.md:84) dosyasında (mirror):

- **Dosya Adlandırma Kuralı (D-183)** — Türkçe amaç-tanımlayıcı ad zorunluluğu, istisnalar
- **Graph Köprü Kuralı (D-184)** — karar↔kod↔test wikilink zorunluluğu, kapsam

---

## 4. Yapılmayanlar / Bilinçli Atlananlar

- **Test suite çalıştırılmadı** — kullanıcı talimatı ("şimdilik testi yapmıyorum").
- **TEST-GRAPH-KOPRU (bonus görev)** — plana göre isteğe bağlıydı, uygulanmadı.
- **Eski kararlara (D-1…D-183) geriye dönük wikilink** — D-184 kararınca isteğe bağlı/düşük öncelik, kapsam dışı bırakıldı.
- **Root `.obsidian/app.json`** — D-177 gereği graph zaten HDI'dan okunduğu için dokunulmadı.

---

## Sonuç

GRAPH-KOPRU-01: D-182 için karar↔kod↔test 3-nod zinciri wikilink'lerle tamamlandı, grep doğrulaması geçti. GRAPH-ARSIV-01: HDI vault'unda gerçek dosya envanterine dayalı regex filtreler eklendi (brief'teki glob hatası düzeltilerek). AGENTS.md her iki kopyada D-183/D-184 bölümleriyle güncel.
