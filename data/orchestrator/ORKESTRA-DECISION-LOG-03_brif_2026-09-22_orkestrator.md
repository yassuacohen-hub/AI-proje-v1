# ORKESTRA-DECISION-LOG-03 — Orkestratör Brief

**Görev:** Decision log UTF-8 hatalarını düzelt  
**Ajan:** ihsan (Orkestratör)  
**Öncelik:** P1  
**Tarih:** 2026-09-22  
**Zincir:** 3/3 (önceki: ORKESTRA-NAMING-AUDIT-02)

## Özet

`data/orchestrator/decision_log.jsonl` dosyasında satır 86 civarında UTF-8 encoding hatası var (byte 0x87 geçersiz karakter). Dosyayı oku, hatalı satırları bulup düzelt, tüm JSONL satırları parse edilebilir hale getir.

## Adımlar

1. **Hata lokalize:** `hexdump` veya `xxd` ile dosyanın 86. satırını inceле — byte 0x87 nerede?
2. **Oku:** Python `open(encoding='utf-8', errors='replace')` ile ve hatalı satırları kayıt et.
3. **Düzelt:** Hatalı karakter yerine uygun UTF-8 karakteri yaz (veya satırı sil/normalize et).
4. **Parse test:** `json.loads(line)` her satırı doğrula — tümü geçerli JSONL olana kadar.
5. **Teslim Not:** Hata türü, düzeltme yöntemi, doğrulama.

## Dosyalar

- `data/orchestrator/decision_log.jsonl` — **kilitli** (düzenle)
- `data/orchestrator/bulgu_defteri.md` — rapor

## Gözlemler

- JSONL yapı: her satır bağımsız JSON object. Bir satır bozuk ise silinebilir.
- Encoding: kimin nasıl yazıp bozduğunu trace et (hangi agent, ne zaman).

**Teslim:** decision_log.jsonl temiz UTF-8, tüm satırlar parse edilebilir, bulgu_defteri.md dosyaya.
