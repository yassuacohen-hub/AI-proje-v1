# Brief: TEST-PLAN-COVERAGE-03 — Test Kapsam Planı & Otomasyon

**Görev ID:** TEST-PLAN-COVERAGE-03  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosyalar:** `tests/`, `docs/TEST_PLAN.md`

---

## DURUM
Zincir adımı 3 (son, UTKU'nun 4. zinciri). Önceki: **ALTYAPI-PROXY-CONFIG-02** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Proje genelinde test kapsamı planlama ve otomasyon kurgusu:
- Unit test hedefleri (coverage %)
- Integration test senaryoları
- Test fixture'ları ve mock'ları
- Test plan belgesi (raporlanabilir)

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Unit Test Hedefleri (Coverage)
```
- src/company_master/ui/         → %70+
- src/company_master/orchestrator/  → %75+
- src/company_master/auth/       → %80+
- src/company_master/db/         → %70+
```

### 2. Test Klasörü Yapısı
```
tests/
  unit/               — Birim testler (modüle bağımlı)
  integration/        — Entegrasyon testler (DB + API + Streamlit)
  e2e/                — End-to-end testler (browser automation, isteğe bağlı)
  conftest.py         — Shared fixtures
```

### 3. Fixture'lar (conftest.py)
```python
@pytest.fixture
def auth_user():
    """Test kullanıcısı (admin, moderator, guest)"""
    return {"email": "test@example.com", "role": "admin", "id": "uuid-123"}

@pytest.fixture
def db_session():
    """Test DB (SQLite in-memory)"""
    # SQLite in-memory engine, AsyncSession wrapper
    return session

@pytest.fixture
def api_client():
    """FastAPI TestClient"""
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def streamlit_session():
    """Streamlit session state mock"""
    return {"user": None, "auth_token": None}
```

### 4. Integration Test Örneği
```python
def test_user_login_workflow(api_client, auth_user):
    # 1. Login
    resp = api_client.post("/auth/login", 
                           json={"email": auth_user["email"], "password": "..."})
    assert resp.status_code == 200
    token = resp.json()["token"]
    
    # 2. GET /api/profile
    resp = api_client.get("/api/profile", 
                          headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    
    # 3. Logout
    resp = api_client.post("/auth/logout", 
                           headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
```

### 5. Test Plan Belgesi (docs/TEST_PLAN.md)
```markdown
# Test Planı — Huginn Data Insights

## Kapsam
- Birim testler: Authentication, Orchestrator, UI Components
- Entegrasyon testler: API workflows, Dashboard interactions
- E2E testler: Full user flows (isteğe bağlı)

## Coverage Hedefleri
- auth/: %80+
- orchestrator/: %75+
- ui/: %70+

## Regresyon Testi
- `pytest tests/ -v` — tüm suite
- `pytest tests/unit/ --cov=src/company_master/`

## Test Türleri
1. Unit: Fonksiyon bazlı, bağımsız
2. Integration: API + DB + Streamlit
3. E2E: Browser automation (Selenium/Playwright)
```

---

## TEST DOSYASI
- **Path:** `tests/test_plan_coverage.py`
- **Test sayısı:** 7
  1. `test_unit_test_directory_exists` — tests/unit/ dizini var mı
  2. `test_integration_test_directory_exists` — tests/integration/ dizini var mı
  3. `test_conftest_fixtures_defined` — conftest.py'de fixture'lar var mı
  4. `test_auth_fixture_creates_user` — auth_user fixture çalışıyor mu
  5. `test_db_session_fixture_works` — db_session fixture çalışıyor mu
  6. `test_api_client_fixture_works` — api_client fixture çalışıyor mu
  7. `test_plan_markdown_file_created` — docs/TEST_PLAN.md var mı ve valid markdown mi

- Komut: `python -X utf8 -m pytest tests/test_plan_coverage.py -v`
- Hedef: 7/7 passed

---

## DOSYALAR
- `tests/unit/` — Yeni dizin (birim testler)
- `tests/integration/` — Yeni dizin (entegrasyon testler)
- `tests/conftest.py` — Shared fixtures (var, güncellenecek)
- `tests/test_plan_coverage.py` — 7 test
- `docs/TEST_PLAN.md` — Test plan belgesi (yeni)

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ tests/unit/ ve tests/integration/ dizinleri mevcut
2. ✓ conftest.py'de 4+ fixture tanımlanmış (auth_user, db_session, api_client, streamlit_session)
3. ✓ Fixture'lar test edilebilir ve çalışıyor
4. ✓ docs/TEST_PLAN.md belgesi yazılmış (markdown, okunabilir)
5. ✓ Coverage hedefleri açık (ui: %70, orchestrator: %75, auth: %80)
6. ✓ Integration test örneği belgelendi
7. ✓ 7 birim test yeşil
8. ✓ Kodlama denetimi temiz

---

## SONRAKI GÖREV
Yok — Zincir sona erdi. UTKU ilk 3 görevini (UI-MENU-FORM-01, UI-FORM-VALIDATION-02, ALTYAPI-FORM-SETUP-03) tamamladıktan sonra bu zincir başlayacak.
