# Brief — ALTYAPI-TEST-HERMETIK-01 (P1)

## Kural (PO onayı 2026-09-23)
**Testler üretim verisine dokunmaz.** Test çalıştırması `data/orchestrator/`
altındaki canlı pano, kilit ve tetik dosyalarını okumaz/yazmaz; `tmp_path` +
`monkeypatch` ile izole edilir.

## Kök Neden
`tests/test_d87_atama_otomasyonu_fixed.py` canlı depoya `gorev_at.py` çağırıyor:
- `data/orchestrator/triggers/olmayan.jsonl` artığı bırakıyor.
- `test_brifsiz_atama_reddedilir` canlı panodaki COP-26 kaydına bağlı; brief
  geri-doldurulunca testin önkabulü bayatladı -> kalıcı kırmızı.

## Yapılacaklar
1. `test_d87_atama_otomasyonu_fixed.py` izole edilsin: `tmp_path` pano/kilit,
   `monkeypatch` ile `task_board.STATE_DIR` yönlendirilsin.
2. Testin önkabulü canlı görev kimliğine değil, test içinde kurulan sabit
   fixture'a bağlansın.
3. Artık dosya bırakmadığı doğrulansın.
4. Bekçi testi: test oturumu sonunda `data/orchestrator/` altında yeni dosya
   oluşmadığını kanıtlayan basit kontrol.

## Dosyalar
- `tests/test_d87_atama_otomasyonu_fixed.py`
- `tests/test_uretim_verisi_dokunulmaz.py`

## Kabul
- `test_brifsiz_atama_reddedilir` yeşil.
- Tam regresyon sonrası `data/orchestrator/triggers/` içinde artık yok.

## Sahibi
ihsan — mod: code
