# Architecture Decision: Hybrid Admin Panel (Streamlit)

**Status:** Accepted (2026-09-12) — Güncellendi (2026-09-12): Panel Konumlandırma Mimarisi
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

## Panel Konumlandirma Mimarisi (2026-09-12 Eklendi)

**Karar:** Iki ayri panel, iki ayri hedef kitle. Admin islemleri musteri arayuzune asla sizmez.

| Panel | Teknoloji | Port | Hedef Kitle | Icerik |
|-------|-----------|------|-------------|--------|
| **Musteri Paneli** | FastAPI + statik web_dashboard | 8000 | Abone firmalar | Firma listesi, eslestirme, sinyal dashboard, NACE, kaynaklar, kredi/uyelik |
| **Admin Paneli** | Streamlit | 8501 | Operasyon ekibi | Sistem sagligi, kullanici onayi, API key yonetimi, webhook izleme, performans |

**P7-19/20/21 Konumlandirmasi:**

| Ozellik | Konum | Gerekce |
|---------|-------|---------|
| **P7-19a** Operasyonel webhook bildirimleri (basarili/hatali/DLQ) | Admin Paneli (Streamlit) | Operasyonel izleme verisi; musteriye gosterilmez |
| **P7-19b** Musteriye yonelik gercek zamanli sinyal bildirimleri (yeni sinyal, yeni firma, eslesme onerisi) | Musteri Paneli (FastAPI + SSE) | Musteri deger onerisinin parcasi; SSE ile canli akis |
| **P7-20** Admin paneli (kullanici yonetimi, API key, kategori) | Admin Paneli (Streamlit) | Yetki siniri: admin API'leri backend'de kalir, Streamlit tuketir |
| **P7-21** Performans metrikleri (db_time, query_count, cache hit, slow_queries) | Admin Paneli (Streamlit) | Operasyonel izleme; `/api/performance` endpoint'i SSOT olur |

**Kurallar:**
1. Admin API'leri (`/api/admin/*`) yalnizca `require_admin` ile korunur; musteri paneli bu endpoint'leri cagirmaz.
2. Musteri panelinde admin UI render edilmez (mevcut JS admin fonksiyonlari backend uyumlulugu icin durur, UI'a baglanmaz).
3. Performans metriklerinin tek kaynagi `/api/performance` endpoint'idir; Streamlit bu endpoint'i cagirir, kendi olcumunu uretmez.
4. SSE yalnizca musteri panelinde kullanilir; admin paneli polling ile calisir.

**Referans:** V9 baglam dokumani 16.4 Panel Konumlandirma Mimarisi

## Bir sonraki adimlar
- [ ] api_client.py olustur
- [ ] db_reader.py olustur (read-only connection)
- [ ] st.session_state ile auth sagla
- [ ] P7-19b: Musteri SSE'sini FastAPI panosuna ekle (yeni sinyal bildirimleri)
