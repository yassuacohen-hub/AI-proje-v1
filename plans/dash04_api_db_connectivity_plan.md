# DASH-04 Baglanti Katmani Uygulama Plani

## Ama
- Streamlit app.py dashboardinin web_app.py REST API uzerinden haberlesmesini saglamak; API erisilemediginde src/company_master/db/connection.py uzerinden DB fallback ine gecmek.

## On Kosullari
- DASH-01/DASH-02/DASH-03 tamamlamis olmali.
- docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md tasarimina uygun olacak.
- data/orchestrator/task_board.json uzerinden DASH-04 gorevini olusturulacak ve dosya kilitleleri uygulanacak.

## Dosyalar ve Kilitlere
- Olusturulacak: scripts/dash04_api_client.py
- Olusturulacak: scripts/dash04_db_reader.py
- Okunacak: app.py, web_app.py, src/company_master/db/connection.py, docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md
- Kilitlelenecek: scripts/dash04_api_client.py, scripts/dash04_db_reader.py, tests/test_dash04_connectivity.py (varsa)

## Uygulama Adimlari
1. DASH-04 gorevini task_board.gorev_ekle(...) ile olustur, ilgili dosyalari kilitle.
2. gorev_guncelle(DASH-04, durum="aktif") ile basla.
3. scripts/dash04_api_client.py olustur:
   - get_api(endpoint, token=None) fonksiyonu
   - .streamlit/config.toml veya ortam degiskenerinden API URL ve anahtar okumasi
   - requests ile /api/... endpointlerine GET/POST istekleri
   - Yonetimi: zaman asimi, 401/403, 500 gibi durumlar icin APIError ozel durum sinifi
4. scripts/dash04_db_reader.py olustur:
   - read_only_query(query, params=None) fonksiyonu
   - src/company_master/db/connection.py get_engine() kullanimi
   - Yalnizca SELECT/guvenli sorgular; yazima izin verme
5. app.py Streamlit sayfasina entegrasyon:
   - Once get_api ile web_app.py APIinden veri cekmeyi dene
   - Basarisiz olursa read_only_query ile DB fallback ine gec
6. Smoke testleri calistir:
   - API basarili path
   - API basarisiz path (DB fallback)
   - DB okuma sorgusu dogrulamasi
7. DASH-04 u gorev_guncelle(DASH-04, durum="done") ile tamamla ve lock_birak(...) ile kilitlere ac.

## Dogrulama
- pytest tests/test_dash04_connectivity.py -v (varsa) veya manuel smoke test
- app.py Streamlit dashboardinin API uzerinden ve DB fallback uzerinden calistigini gozlemlemek
- task_board.json ve AGENT_SYNC.md guncelleme kontrolu

## Kisiyaltilar
- Test suiteini degistirmez (dogrudan ilgili olmayan)
- Turkce kullanici iletisimi
- .env disinda gizli anahtar kullanilmaz
