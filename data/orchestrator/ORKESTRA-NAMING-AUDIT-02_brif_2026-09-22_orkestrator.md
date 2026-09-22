# ORKESTRA-NAMING-AUDIT-02 — Orkestratör Brief

**Görev:** Naming denetimi — task_board.json standardı  
**Ajan:** ihsan (Orkestratör)  
**Öncelik:** P1  
**Tarih:** 2026-09-22  
**Zincir:** 2/3 (önceki: DOC-V10-AUDIT-01, sonraki: ORKESTRA-DECISION-LOG-03)

## Özet

`task_board.json` dosyasında D-57 başlık standartı ihlalleri var (285 görev uygunsuz). Her görev başlığı şu pattern'i takip etmeli:
```
[ALAN] FIIL + NESNE → ÇIKTI (SÜRE)
```
Uygunsuz başlıkları tanımla, standardı düzelt, denetim raporunu yaz.

## Adımlar

1. **Scan:** `task_board.json` tüm görevlerin başlıklarını oku.
2. **Doğrula:** Regex ile D-57 pattern kontrol et: `^\[([A-ZĞÜŞİÖÇ]+)\]\s+(\S+).*?→.*?\((\d+[sd])\)$`
3. **Kayıt:** Uygunsuz bulunacak görev ID'lerini ve başlıklarını listele.
4. **Fix:** Her başlığı standard'a çevirecek otomatik veya manuel dönüşüm yap (ALAN/FIIL lookup tablosunu kullan).
5. **Doğrulama:** 285 uygunsuz → 0 olana kadar.
6. **Rapor:** `data/orchestrator/bulgu_defteri.md` veya `tests/test_naming_audit.py` test case yazarak dokümante et.

## Dosyalar

- `data/orchestrator/task_board.json` — **kilitli** (düzenle, ALTYAPI-PANO-ENCODING-FIX-01 blocking bırak)
- `tests/test_naming_audit.py` — denetim test case'i (yarat veya güncelle)
- `data/orchestrator/bulgu_defteri.md` — rapor

## Gözlemler

- 285 uygunsuz başlık çok fazla — otomatik dönüşüm script gerekebilir.
- Türkçe karakterler (Ü, ı, ö) regex'de özel handling gerekebilir.
- Encoding hatası sonrası başlık parsing'i daha zorlaşabilir (mojibake).

**Teslim:** Denetim raporu, fix script, 0 uygunsuz başlık, test case yazılmış.
