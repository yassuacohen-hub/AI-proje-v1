# Architecture Decision: Hybrid Admin Panel (Streamlit)

**Status:** Accepted (2026-09-12)
**Deciders:** User, Cline
**Context:** Streamlit admin paneli hem iç veri okuması hem de kullanıcı yönetimi yapacak

## Kararsız Noktalar
1. Streamlit - web_app API mı, yoksa DB'ye mi baglanir?
2. Admin login sifre korumasi yeterli mi?

## Kararlar
1. **Streamlit web_app API'lerini kullanir** - fallback DB okuma (transaction safety)
2. **Admin login sifresi** - `.streamlit/secrets.toml` (prod icin)

## Gecici Cozum (ilk 24 saat)
- `st.session_state.password` ile basit auth
- `.streamlit/secrets.toml` -> `admin_password = "test123"`

## Uzun Vadeli Plan
- JWT token -> web_app API (Bearer header)
- Role-based yetkilendirme (admin/read-only)

## Konfigurasyon
### .streamlit/config.toml
```toml
[server]
port = 8501
enableCORS = false

[secrets]
admin_password = "test123"
api_url = "http://localhost:8000"
db_url = "postgresql://user:pass@localhost:5432/huginn"
```

## API Client Yapisi
### api_client.py
```python
def get_api(endpoint, token=None):
    """web_app API'sine GET request gonderir."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(f"{API_URL}{endpoint}", headers=headers)
    if resp.status_code == 401:
        st.warning("Yetkisiz erisim")
        st.stop()
    return resp.json()
```

## Fallback Mekanizmasi
API hatasi durumunda DB'ye gecis:
1. `try: api_result = get_api(...)`
2. `except: df = read_only_query("SELECT ...")`
3. `st.data_editor(df)` ile gostermeye devam et

## Riskler
- Streamlit sadece 8501 portunda, disa actiginda reverse proxy gerekir
- DB fallback sirasinda veri tutarsizligi riski var

## Bir sonraki adimlar
- [ ] api_client.py olustur
- [ ] db_reader.py olustur (read-only connection)
- [ ] st.session_state ile auth sagla
