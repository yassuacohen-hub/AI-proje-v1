# AGENTS-MERGE-UU — Rapor

- **Ajan:** ihsan
- **Tarih:** 2026-09-23
- **Öncelik:** P0
- **Brif:** [`AGENTS-MERGE-UU_brif_2026-09-23_ihsan.md`](AGENTS-MERGE-UU_brif_2026-09-23_ihsan.md)

## Özet

Kök `AGENTS.md` ile vault `Huginn Data Insights/AGENTS.md` arasındaki kural kopyası giderildi. Kök dosya artık yalnızca n8n-as-code bloğu + vault SSOT işaretçisi taşıyor. KAHİN'in yeni kuralı **D-188 (önce pano, sonra tetik)** ve kapanış kuralı **D-189 (kök AGENTS.md kural taşımaz)** vault AGENTS.md'ye işlendi.

## Bulgu: "UU branch çatışması" gerçek git çatışması değildi

| Kontrol | Sonuç |
|---|---|
| `git ls-files -u` (vault) | boş — unmerged dosya yok |
| `MERGE_HEAD` | yok |
| `<<<<<<<` / `=======` / `>>>>>>>` işaretleri | her iki AGENTS.md'de 0 |
| Kök `c:/Huginn Data Projesi` | git deposu değil |

Gerçek sorun: **iki dosyada paralel kural kopyası**. Kök AGENTS.md 76-108. satırlar arasında D-55/D-60/ORCH-08 özetlerini tutuyordu; vault AGENTS.md ise tam ve güncel kaydı (D-48…D-186) tutuyor. Kopya sürüm kayması üretiyor, kök özet eskiyordu (ör. `salih` ajanı kök listede yok).

## Yapılan Değişiklikler

### 1. `AGENTS.md` (kök) — 108 → 93 satır

- `<!-- n8n-as-code-start -->` … `<!-- n8n-as-code-end -->` bloğu (2-72) **hiç dokunulmadı** — `npx --yes n8nac update-ai` tarafından yeniden üretilir.
- 76-108 arası kopya kural özeti kaldırıldı; yerine "Çalışma Alanı Kuralları — Tek Kaynak" işaretçisi + 3 maddelik okuma/yazma sırası geldi.
- `[[Huginn Data Insights/AGENTS]]` wikilink'i İlgili Nodlar'a eklendi (D-184 graph köprüsü).

### 2. `Huginn Data Insights/AGENTS.md` — 581 → 592 satır

- **D-188 — Önce Pano, Sonra Tetik (KAHİN kararı 2026-09-23):** görev önce `task_board.json`'a yazılır (brif diskte, `talimat` alanı brif yolunu gösterir), sonra `triggers/{ajan}.jsonl` tetiği atılır. Ters sıra yasak. Doğrulama `gorev_at.py pano`. D-66 ve D-68 ile birlikte uygulanır.
- **D-189 — Kök AGENTS.md Kural Taşımaz:** kök dosya yalnızca n8n bloğu + vault işaretçisi içerir.

## Doğrulama

```
AGENTS.md                     BOM False  catisma 0  satir 93
Huginn Data Insights/AGENTS.md BOM False catisma 0  satir 592
```

- UTF-8, BOM yok — uygun.
- Çatışma işareti yok.
- Commit atılmadı (brif gereği).

## D-188'i Tetikleyen Olay

Bu görevin kendisi kuralın gerekçesi oldu: `AGENTS-MERGE-UU` ve `VAULT-CLEANUP-BATCH` tetikleri `ihsan.jsonl`'e yazılmış ama panoda karşılığı açılmamıştı. `al` komutu `HATA: Görev panoda bulunamadı: AGENTS-MERGE-UU` verdi, iş başlamadan durdu. İki brif yazılıp `data/_tmp/pano_eksik_gorev_ekle.py` ile pano kayıtları açıldıktan sonra görevler alınabildi.

## Öneriler (KAHİN onayına)

1. **D-188'i koda bağla:** `gorev_kutusu.py` tetik yazma yolunda panoda kayıt yoksa tetik yazmayı reddetsin — kural belgeyle değil kodla dayatılsın.
2. **Tetik/pano tutarlılık kontrolü:** günlük bakım içinde `triggers/*.jsonl` içindeki `bekliyor` kayıtlarının panoda karşılığı taransın; yetim tetik alarm üretsin.
3. **Görev ID öneki D-57 ile hizalanmalı:** `AGENTS-MERGE-UU` / `VAULT-CLEANUP-BATCH` kimlikleri D-57 ALAN öneklerine (UI/API/VERI/TEST/DOC/ALTYAPI/ORKESTRA) uymuyor. `gorev_at.py` doğrular ama `gorev_ekle` bypass ediyor — bu boşluk kapatılmalı.

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
