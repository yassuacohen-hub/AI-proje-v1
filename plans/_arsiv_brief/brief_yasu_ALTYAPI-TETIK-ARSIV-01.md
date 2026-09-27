# ALTYAPI-TETIK-ARSIV-01 — Kanonik olmayan tetik dosyalarini tasi

## Gorev Ozeti
`data/orchestrator/triggers/` icinde D-60 oncesi 14 kanonik olmayan `.jsonl`
duruyor. Her tarama, her denetim, her senkron bunlari geziyor; yanlis ajana
tetik dusme riski ve kalici gurultu kaynagi.

## Mevcut Durum (kanit: `dir /b data\orchestrator\triggers`)
Kanonik (D-33/D-60, `trigger.AJANLAR`): `ihsan.jsonl`, `utku.jsonl`,
`salih.jsonl`, `yasu.jsonl` — **kalacak**.

Kanonik olmayan — tasinacak:
`arastirmaci.jsonl`, `claude_code.jsonl`, `copilot.jsonl`, `cursor_grok.jsonl`,
`external_agent.jsonl`, `gelistirici.jsonl`, `kalite.jsonl`, `mimar.jsonl`,
`mimari.jsonl`, `MVP-KUL-02.jsonl`, `research_ponytale_caveman.jsonl`,
`web_kazima.jsonl`

Ayrica: `ihsan.ALARM.json` — kanonik ajan ama `.jsonl` degil; **once incele**,
icerigi hala anlamliysa birak, degilse arsivle. Karari raporda gerekcelendir.

## Is Maddeleri
1. Hedef dizin: `data/orchestrator/triggers/_arsiv_2026-09-23/` (olustur).
2. **Tasimadan once her dosyada acik kayit taramasi yap:** `durum` alani
   `bekliyor`/`alindi` olan kayit varsa o dosyayi **tasima**, raporda listele.
   Yarim kalmis is sessizce gomulmeyecek.
3. Temiz olanlari tasi (sil degil, tasi — geri donus yolu acik kalsin).
4. `trigger.AJANLAR` listesini kaynak al; dosya adi listesini koda gomme.
5. Tasima sonrasi `python scripts/pano_denetim.py` calistir, yeni uyari cikmadigini dogrula.
6. Rapor: `data/orchestrator/ALTYAPI-TETIK-ARSIV-01_rapor_2026-09-23_yasu.md`
   — tasinan / tasinmayan + gerekce tablosu.

## Ek Bulgu (ayni raporda ele al, kod degisikligi bu gorevde yok)
Yasu'nun onceki bulgusu: `data_worktree/orchestrator/` altinda pano kopyasi var.
Iki pano = iki dogruluk kaynagi riski. Hangi dosyalarin kopya oldugunu listele,
silme/tasima **yapma** — karar orkestratorde (D-172 otorite kurali).

## Kurallar
- D-60 kanonik ajan listesi, D-77 pano isleri orkestratore ait, D-86 cmd.exe.
- Silme yok, tasima var. Geri alinamaz islem bu gorevde yasak.

## Teslim
```
python scripts/gorev_kutusu.py teslim --task-id ALTYAPI-TETIK-ARSIV-01 --ajan yasu --ozet "<ozet>" --cikti data/orchestrator/ALTYAPI-TETIK-ARSIV-01_rapor_2026-09-23_yasu.md
```

## Sure Tahmini
2s

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
