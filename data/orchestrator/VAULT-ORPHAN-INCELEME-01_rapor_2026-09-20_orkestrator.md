# VAULT-ORPHAN-INCELEME-01 — Orphan Nod Siniflandirmasi ve Yönetim Plani

**Tarih:** 2026-09-20  
**Kapsam:** Tüm proje kökü (vendor/.venv/.git filtreli, tam orphan listesi)

## Ne yapildi

Vault tarama v2 (VAULT-TARAMA-02) sonrasinda 3361 orphan dosya (hiçbir note'dan referans yok) 8 kategoriye ayrildi:
1. **worktree_ikizi** (keep) — Git worktree ikizi, silinmez
2. **gecici_yedek** (archive) — .bak/.tmp/_old türü, konsolidasyon adayi
3. **gelistirici_arac** (keep) — .roo/.kilo/.cursor/.vscode altinda, silinmez
4. **eski_proje_ikizi** (review) — AI proje v1 / data_worktree, inceleme gerekir
5. **arsiv_legacy** (archive) — Arşiv/legacy dizin altinda
6. **icerik_yedek** (archive) — *_backup / *_archive dosyalari
7. **aktif_belge** (review) — Aktif vault içeriği ama bağlantısız, inceleme gerekir

Her dosyaya atanan: kategori, boyut, son değişiklik tarihi, risk (low/medium/high), aksiyon önerisi.

## Degisen dosyalar

- `Huginn Data Insights/data/orchestrator/VAULT-ORPHAN-INCELEME-01_siniflama_2026-09-20_orkestrator.json` (3361 dosya × 7 alan)
- `Huginn Data Insights/data/orchestrator/VAULT-ORPHAN-INCELEME-01_rapor_2026-09-20_orkestrator.md` (bu rapor)
- Aynilari `worktree klasoru/data/orchestrator/` dizinine de yazildi

## Test sonuçlari

| Kontrol | Sonuç | Durum |
|---------|-------|-------|
| Orphan sayisi | 3361 | OK |
| JSON şeması (dosya/kategori/boy/degistirilme/neden_orphan/oneri/risk) | 7 alan ✓ | OK |
| Kategori kapsamı | 7 kategori | OK |
| Risk atamasi | High/Medium/Low | OK |
| Aksiyon önerisi | keep/review/archive (delete yok) | OK |
| İki dizin yazma | HDI + worktree | OK |

## Bulgular

🟡 **Worktree ikizi risk:** 668 dosya, keep önerisi (silme yok), yönetim kararı bekleniyor.

🟡 **Geliştirici araç orphan:** 1104 dosya (.roo/.kilo/.cursor/.vscode altinda), keep önerisi, proje kurulum dosyasi olabilir.

🟢 **Arşivlenebilir:** 7 dosya (geçici/yedek/legacy), arşiv deposu adayi.

🔵 **Aktif belge inceleme:** 1291 dosya, vault haritasina eklenecek veya silinecek mi kararı insan tarafindan verilmeli.

## Eksik / Erteleme

- ❌ **Kırık referans (xref):** Referans var ama hedef yok, ayrı tarama gerekir (sonraki sprint)
- ⚠️ **Silme kararı:** Bu turda silme yapilmadi. Tüm öneriler "archive" veya "review"
- ⏳ **Worktree senkronizasyon:** İki ağacin yönetim stratejisi ortaya konmadi (D-XX'de)

## Aksiyon Plani

| Risk | Kategori | Say | Oneri | Durumu |
|------|----------|-----|-------|--------|
| 🔴 High | worktree_ikizi | 668 | keep | Iki ağaç yönetimi netleştirilmeli |
| 🔴 High | gelistirici_arac | 1104 | keep | Kurul dosyalari, silinmez |
| 🟡 Medium | eski_proje_ikizi | 291 | review | Konsolidasyon veya arşiv kararı |
| 🟡 Medium | aktif_belge | 1291 | review | Vault haritasina eklenecek veya silinecek |
| 🟢 Low | gecici_yedek | 5 | archive | Hemen arşivlenebilir |
| 🟢 Low | arsiv_legacy | 2 | archive | Hemen arşivlenebilir |
| 🟢 Low | icerik_yedek | 0 | archive | Hemen arşivlenebilir |

**Silme bloğu:** Hiçbir kategori bu turda "delete" önerisi almadi. Tüm temizlik "archive" (depo taşı) ile yapilacak.

## Kaynaklar

- Siniflama JSON: `data/orchestrator/VAULT-ORPHAN-INCELEME-01_siniflama_2026-09-20_orkestrator.json` (tam detay)
- Tarama sonuçlari: `data/orchestrator/VAULT-TARAMA-02_analiz_2026-09-20_orkestrator.json`
