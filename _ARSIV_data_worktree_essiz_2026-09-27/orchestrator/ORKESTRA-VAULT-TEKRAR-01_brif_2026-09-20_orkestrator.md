# ORKESTRA-VAULT-TEKRAR-01 — Brif

**Görev ID:** ORKESTRA-VAULT-TEKRAR-01  
**Sahip:** Orkestratör İhsan  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Çıktı:** `data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-20_orkestrator.md`

---

## Problem

KAHİN raporu (2026-09-20):
> "vault isim tekrarları hala devam ediyor tekrar bakılacak uzun zincir görevinde sen buna tekrar bakarsın"

Obsidian vault (`AI proje v1/`) ve worktree root'ta **isim tekrarları** mevcut:
- `AGENTS.md` (root) vs `AGENTS.md` (AI proje v1/)
- `ANA_KURALLAR.md` (root) vs `ANA_KURALLAR.md` (AI proje v1/)
- `AGENT_SYNC.md` (root) vs `AGENT_SYNC.md` (AI proje v1/)

**Sonuç:** Import/referans karmaşası, git diff gürültü, aray tanımı belirsiz.

---

## İş Maddeleri

1. **Tespit:** Vault'daki 3 dosyayı listele (tümü gerçekten `AI proje v1/` içinde)
2. **Analiz:** Root dosyalarla karşılaştır (içerik aynı mı, stale mi, bağımsız mı?)
3. **Karar:** Vault dosyaları kaldırılacak mı (single-source-of-truth root) yoksa symlink yapılacak mı?
4. **Rapor:** Karar tablosu + hazırlık notları

---

## Kabul Kriterleri

- ✅ 3 dosya bulundu ve içeriği kıyaslandı
- ✅ Kök neden (niye çoğaldı) tanımlandı
- ✅ Karar: root SSOT veya vault SSOT
- ✅ Rapor D-67 formatında (Ne yapıldı / Bulgular / Karar)
