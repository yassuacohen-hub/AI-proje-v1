# 08 - Harici Ajan Görev Önerileri

Bu belge, harici ajanların ([[07_harici_ajan_protokolu]] kapsamındaki Cursor Grok, GitHub Copilot, Claude Code vb.) bu projede **en verimli** şekilde kullanılabileceği görev tiplerini listeler. Her öneri, ajanın güçlü yönleriyle projenin ihtiyacını eşleştirir.

> Harici ajanlar yalnızca `workspace/external/{agent_id}/` altında çalışır; öneriler bu kısıtla uyumludur.

---

## 1. Cursor Grok için Önerilen Görevler

Cursor Grok; hızlı kod analizi, çoklu dosya taraması ve Streamlit/Python ekosisteminde güçlüdür.

### 1.1 `app.py` Streamlit Performans Optimizasyonu
- **Kapsam:** `src/etl/app.py` (veya proje kökündeki `app.py`) — pagination + DB cache.
- **Beklenen çıktı:**
  - 50/sayfa pagination eklenmesi.
  - `@st.cache_data(ttl=300)` ile Supabase sorgularının önbelleklenmesi.
  - Filtrelerin DB seviyesine taşınması (örn. `is_ankara=TRUE AND is_osb_member=TRUE`).
- **Ölçüt:** İlk yükleme süresi < 1.5 sn, sayfa geçişi < 300 ms.

### 1.2 `src/company_master/` Test Kapsamı Genişletme
- **Kapsam:** Mevcut testlerin coverage analizi ve yeni unit/integration test senaryoları.
- **Beklenen çıktı:**
  - `tests/company_master/` altında eksik senaryolar için pytest modülleri.
  - `pytest --cov=src/company_master` çıktısı ve coverage raporu.
  - Edge case listesi: null VKN, Türkçe karakter normalize, corp_marker varyasyonları.
- **Ölçüt:** Coverage >= %85, tüm testler geçer.

### 1.3 ETL Pipeline Hata Loglarını Analiz ve İyileştirme
- **Kapsam:** `src/etl/pipeline.py` ve `logs/` çıktıları.
- **Beklenen çıktı:**
  - Tekrarlayan hata pattern'lerinin listesi.
  - Retry/backoff önerileri.
  - Yapılandırılmış log formatı (JSON) için patch önerisi.
- **Ölçüt:** Aynı hatanın tekrarlama sıklığında ölçülebilir düşüş.

---

## 2. GitHub Copilot için Önerilen Görevler

Copilot; küçük, tekrarlayan kod parçaları, boilerplate ve CI/CD şablonları için idealdir.

### 2.1 Kod Snippet'leri ve Boilerplate Üretme
- **Kapsam:** Tekrarlayan CRUD, validator, normalizer kalıpları.
- **Beklenen çıktı:** `workspace/external/copilot/output/snippets/` altında kullanıma hazır Python modülleri.
- **Ölçüt:** Her snippet tip güvenli (type hints), docstring içerir ve orijinal şablonla uyumludur.

### 2.2 Otomatik Tamamlama ve Refactoring Önerileri
- **Kapsam:** IDE içi inline öneri olarak kullanılır; orkestratör bu çıktıyı doğrudan commit etmez.
- **Beklenen çıktı:** PR review notu olarak `output/refactor_suggestions.md`.
- **Ölçüt:** Her öneri somut bir kod satırına referans verir.

### 2.3 CI/CD Workflow'ları için GitHub Actions Şablonları
- **Kapsam:** `.github/workflows/` eksik pipeline'lar.
- **Beklenen çıktı:**
  - `ci.yml` (lint + type-check + test)
  - `deploy-staging.yml` (Streamlit preview)
  - `nightly-etl.yml` (ETL job)
- **Ölçüt:** Her workflow, gizli anahtarı `secrets.` üzerinden okur; hardcoded secret içermez.

---

## 3. Claude Code / Diğer LLM Ajanlar için Önerilen Görevler

Claude Code; uzun bağlam okuma, mimari dokümantasyon ve güvenlik review gibi derin analiz görevlerinde güçlüdür.

### 3.1 Mimari Dokümantasyon Güncellemeleri
- **Kapsam:** `V10/02_mimari/`, `V10/04_dokumanlar/` klasörleri.
- **Beklenen çıktı:**
  - Modül bağımlılık diyagramı (metin/Mermaid).
  - Servis sorumluluk matrisi (kısa tablo).
  - ADR (Architecture Decision Record) taslakları.
- **Ölçüt:** Doküman, ana bağlam `01_versiyon_9_baglam_dokumani.md` ile çelişmez.

### 3.2 Teknik Borç Analizi ve Refactoring Planı
- **Kapsam:** Tüm `src/` ağacı.
- **Beklenen çıktı:**
  - `output/tech_debt.md` — kategorize edilmiş borç listesi (kritik/orta/düşük).
  - `output/refactor_plan.md` — önceliklendirilmiş, tahmini eforlu aksiyon planı.
  - `output/risk_register.md` — risk matrisi.
- **Ölçüt:** Her madde dosya:satır referansı içerir; en az 1 somut iyileştirme önerisi sunar.

### 3.3 Güvenlik Audit ve Dependency Güncellemeleri
- **Kapsam:** `requirements.txt`, `pyproject.toml`, `package.json` (varsa).
- **Beklenen çıktı:**
  - `output/security_audit.md` — bilinen CVE'ler, güncellenmesi gereken paketler.
  - `output/dependency_diff.md` — minor/patch güncellemelerin etki analizi.
  - `.env` / gizli anahtar sızıntısı için statik tarama özeti.
- **Ölçüt:** Kritik CVE'ler için upgrade önerisi net sürüm numarası içerir.

---

## 4. Görev Tipi -> Ajan Eşlemesi (Hızlı Tablo)

| Görev Tipi | Cursor Grok | GitHub Copilot | Claude Code |
|-----------|:-----------:|:--------------:|:-----------:|
| Code Review | +++ | + | +++ |
| Refactoring | ++ | ++ | +++ |
| Test Üretme | +++ | ++ | ++ |
| Dokümantasyon | + | + | +++ |
| Veri Dönüşümü | ++ | ++ | + |
| Araştırma | + | + | +++ |
| CI/CD Şablonu | + | +++ | ++ |
| Güvenlik Audit | + | + | +++ |

---

## 5. Öncelik Sırası (Önerilen Başlangıç Seti)

1. **Cursor Grok -> app.py performans optimizasyonu** (hızlı kazanım, ölçülebilir).
2. **Claude Code -> teknik borç analizi** (uzun vadeli yol haritası için girdi).
3. **GitHub Copilot -> CI/CD şablonları** (tekrarlayan işleri otomatikleştirme).
4. **Cursor Grok -> test coverage artırma** (kararlılık).
5. **Claude Code -> güvenlik audit** (release öncesi kontrol).

---

## 6. Kaynaklar

- [[07_harici_ajan_protokolu]]
- `AGENT_SYNC.md`
- `AI proje v1/AGENTS.md`
- Ana bağlam: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`