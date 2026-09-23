# ALTYAPI-D66-BYPASS-TETIKLEME — D-65 İş Durmaz Mekanizması Uygulaması

## Özet

D-65 kuralı kodda yok. Görevler blokajda 3+ gün hareketsiz kalıyor. **Seçenek (a) uygula:** pano_denetim 24h blocked tespit → exit 2 → tetik_senk rapor → KAHİN elle tetikle.

## Hedefler

1. `pano_denetim.tara()` — blocked + 24h+ tespit, `{"type": "blocked_bypass", "task_id": "X", "gun": N}` döner
2. Exit kod 2 (bypass gerekli sinyali) ekleme
3. `tetik_senk.py` — exit 2 aldığında AGENT_SYNC.md'ye rapor satırı ekle
4. Tests: 4 test (24h+, <24h, P0/P1 oncelik, rapor format)
5. AGENTS.md — D-66 karar kaydı ekle

## Bağımlılıklar

- ORKESTRA-D65-ISDURMAZ-01 (ölçüm raporu tamamlandı)
- D-65 kuralı (AGENTS.md:167-175)

## Çıktı

- `pano_denetim.py` — güncellenmiş tara() + main() exit 2
- `tetik_senk.py` — exit 2 handling + rapor
- `tests/test_d66_bypass_tetikleme.py` — 4 test
- `AGENTS.md` — D-66 karar (D-68'den sonra)

## Kurallar

- D-65: Blokajda iş durmaz (prensibi, sabit)
- **D-66:** Bypass tetikleme mekanizması (seçenek a, 24h, exit 2)
- D-73/D-74: KAHİN anahtar protokolü (D-66 rapor KAHİN'e gider)

## Teslim

Rapor + testler tamamlandığında:
```
python -m pytest tests/test_d66_bypass_tetikleme.py -v
```
Tüm testler yeşil, AGENTS.md güncellenmiş, rapor dosyası hazır.

