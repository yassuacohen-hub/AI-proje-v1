# Brief: TEST-PLAN-COVERAGE-03 — Test Kapsam Planı & Otomasyon

**Görev ID:** TEST-PLAN-COVERAGE-03  
**Sahip:** SALİH (Test Danışman)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `tests/`, `docs/TEST_PLAN.md`

---

## DURUM
Zincir adımı 3 (son, SALİH). Önceki: **ALTYAPI-PROXY-CONFIG-02** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Proje genelinde test kapsamı tanımla:
- Unit test hedefi: % 70+ coverage (kritik modüller)
- Integration test senaryoları (3+ endpoint)
- E2E workflow (login → işlem → logout)
- Test plan belgesi (raporlanabilir)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Unit Test Hedefleri (Coverage)
- `src/company_master/ui/` → %70+
- `src/company_master/orchestrator/` → %75+
- `src/company_master/auth/` → %80+
- `src/company_master/db/` → %70+

### 2. Test Yapısı
- `tests/unit/` — birim testler
- `tests/integration/` — entegrasyon (DB + API)
- `tests/e2e/` — end-to-end (browser automation, opsiyonel)
- `tests/conftest.py` — shared fixtures

### 3. Fixture'lar
- `auth_user` — test kullanıcısı (admin, moderator, guest)
- `db_session` — test DB (SQLite/PostgreSQL in-memory)
- `api_client` — FastAPI TestClient
- `streamlit_session` — Streamlit session state mock

### 4. Integration Test Örneği
```python
def test_user_login_workflow(api_client, auth_user):
    # 1. Login
    resp = api_client.post("/auth/login", json={"email": auth_user["email"], "pass": "..."})
    assert resp.status_code == 200
    token = resp.json()["token"]
    
    # 2. GET /api/profile
    resp = api_client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    
    # 3. Logout
    resp = api_client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
```

### 5. Test Plan Belgesi
- Dosya: `docs/TEST_PLAN.md`
- Bölümler:
  - Test Coverage Hedefleri (% tablo)
  - Test Kategorileri (Unit, Integration, E2E)
  - Kritik User Journey'ler (3+)
  - CI/CD Entegrasyonu
  - Rapor Şeması (pass/fail oranı)

### 6. CI/CD Entegrasyonu
- GitHub Actions: `.github/workflows/test.yml`
  - `pytest tests/ -v --cov=src --cov-report=term-missing`
  - Geçme kriteri: Coverage %65+, tüm testler yeşil
- Slack notification (opsiyonel)

### 7. Test Dosyası
- `tests/test_plan.py` — 10 test
  - `test_coverage_target_unit_ui` (2 test)
  - `test_integration_workflow_login` (3 test)
  - `test_e2e_basic_flow` (3 test)
  - `test_ci_github_actions_config` (2 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_plan.py -v`

---

## DOSYALAR
- Yaz: `docs/TEST_PLAN.md`
- Yaz: `tests/conftest.py` (update)
- Yaz: `tests/unit/test_example.py` (örnek)
- Yaz: `tests/integration/test_example.py` (örnek)
- Yaz: `.github/workflows/test.yml`
- Düzenle: `tests/test_plan.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ Coverage hedefleri tanımlı (unit/integration/e2e)  
✅ Fixture'lar (`auth_user`, `db_session`, `api_client`)  
✅ Integration workflow örneği (login test)  
✅ Test Plan belgesi (% tablo, workflow'lar)  
✅ GitHub Actions CI config  
✅ Test sayısı: 10 (tümü yeşil)  
✅ UTF-8 temiz

---

## ZINCIR TAMAMLANIŞI
✅ Tüm 3 görev (ALTYAPI-WEB-MONITOR-01, ALTYAPI-PROXY-CONFIG-02, TEST-PLAN-COVERAGE-03) bitmişse zincir kapanır. SALİH rapor yazıp teslim eder.
