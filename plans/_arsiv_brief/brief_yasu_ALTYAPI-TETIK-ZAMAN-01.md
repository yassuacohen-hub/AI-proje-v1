# Brif — ALTYAPI-TETIK-ZAMAN-01 (yasu)

## Görev Özeti
`scripts/tetik_senk.py` elle çalıştırılıyor. Pano durumu ile tetik kuyruğu
arasındaki sapma, biri komutu hatırlayana kadar birikiyor. Senkronu bir
zamanlayıcıya bağla.

## Sorun (kanıt)
- `tetik_senk.py` çıktısı hiçbir yere yazılmıyor; sonuç kaybolur.
- Sapma tespit edilmediği için `pano_denetim.py` uyarıları birikiyor.

## Çıktı
1. `tetik_senk()` çağrısı bir giriş noktasına bağlanır:
   - `scripts/tetik_senk.py --gunluk` → sonucu
     `data/orchestrator/tetik_senk_log.jsonl` satırına ekler
     (`{"an": ISO, "senk": N, "sapma": M}`).
2. **Sessiz başarı yasak:** sapma bulunup düzeltilemezse çıkış kodu `!= 0`.
   Sıfır satır etkilendiğinde de sessizce 0 dönmesin.
3. `tests/test_tetik_senk_log.py` — 2 test:
   - log satırı yazılıyor ve JSON olarak okunabiliyor,
   - düzeltilemeyen sapmada exit kodu sıfır değil.

## Kurallar
- D-86: Windows cmd.exe; `→` ve `%errorlevel%` tuzakları. Doğrulamayı
  Python/`subprocess` üzerinden yap.
- Yeni bağımlılık ekleme. Zamanlama bağlaması stdlib + mevcut script yeterli.

## Süre Tahmini
2 seans.
