# UI-ADMIN-SSE-IHLAL-03 — Brief (ihsan)

**Başlık:** [UI] SSE mimari ihlalini düzelt → admin_realtime.py polling (3s)
**Öncelik:** P0 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_realtime.py`

## Neden

Mimari demir kural: **SSE yalnız müşteri panelinde**. Admin panelde ihlal var (SSOT §4.1 / §8.3 C1).

## Adımlar

1. `_sse_oku()` **satır 143** ihlal noktası.
2. Seçenek A: `_db_kpi_oku()` (`:154`) + `admin_auto_refresh.render_auto_refresh()` (`:76`) ile polling'e çevir.
3. Seçenek B: `docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md` kural 4'e gerekçeli istisna maddesi yaz.
4. KK-1 KARARI (urun sahibi, 2026-09-24): **Secenek A - polling.** Bloke kalkti. ADR'ye istisna YAZILMAYACAK; admin KPI'lari saatlik degisir, ~5sn gecikme kabul edilebilir.
5. Musteri panelindeki SSE'ye (P7-19b, FastAPI, ADR satir 73) **dokunma** - o dogru yerde. Admin'deki fazlalik kopya kaldiriliyor, tasinmiyor.
6. Olu kalan SSE yardimcilarini/importlarini sil; yarisi duran kod birakma.

## Kabul kriteri

- [ ] KK-1 kararı SSOT §11'de `🔴 Açık` → karar metniyle kapandı.
- [ ] Seçilen yol uygulandı, ADR ile kod tutarlı.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
