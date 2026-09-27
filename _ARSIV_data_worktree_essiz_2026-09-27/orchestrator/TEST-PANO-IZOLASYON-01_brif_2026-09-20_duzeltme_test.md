# TEST-PANO-IZOLASYON-01 — Brif (SALİH)

## Görev
`tests/test_pano_bakim_d77.py` izolasyon eksikliğini düzelt.

## Hata
- `test_pano_bakim_tetik_bekliyor_pano_aktif_d77` → `ValueError: Gorev zaten var: TEST-D77-01`
- `test_pano_bakim_tetik_done_tetigi_esitle` → `ValueError: Gorev zaten var: TEST-D77-02`
- Kök neden: [`tests/test_pano_bakim_d77.py:44-95`](tests/test_pano_bakim_d77.py:44) `tb.gorev_ekle(task_id="TEST-D77-01"/"TEST-D77-02", ...)` gerçek `task_board.json` dosyasına yazıyor, teardown/temizlik yok. Önceki koşumdan kalıntı varsa ikinci koşum patlar.

## Çözüm yönü
- Fixture'a `tmp_path` + `monkeypatch` ile `task_board.py` veri dizinini izole et (bkz. [`tests/conftest.py:26-43`](tests/conftest.py:26) `db_session` fixture'daki izolasyon deseni) — YENİ bağımlılık ekleme, mevcut pattern'i taklit et.
- Ya da test sonunda `tb.gorev_sil` / dosyadan kaydı temizleyen bir teardown ekle (böyle bir fonksiyon yoksa en basit yöntem tercih edilir — YAGNI).

## Doğrulama
```
python -X utf8 -m pytest tests/test_pano_bakim_d77.py -q
python -X utf8 -m pytest tests/test_pano_bakim_d77.py -q
```
(İki kez art arda çalıştır — izolasyon doğrulaması budur.)

## Teslim
Rapor → YASU'ya yönlenir (D-59/D-63): `python scripts/rapor_olustur.py --task-id TEST-PANO-IZOLASYON-01 --ajan yasu --ozet "..."`
