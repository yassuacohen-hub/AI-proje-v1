# Brief — GIT-HIJYEN-01 (kilo)

**Oncelik:** P2 · **Ajan:** kilo · **Kontrolor:** roo

## Amac
`python scripts/kodlama_denetim.py --kapsam kod` su an **exit 1** veriyor:
- `crlf_karisik` → 60 dosya (ayni dosyada CRLF + LF karisik)
- `dosya_sonu` → 106 dosya (son satirda newline yok)

Bu eski borc; her teslimde denetimi kirletiyor ve gercek bulgulari gizliyor.

## Yapilacak
1. `python scripts/kodlama_denetim.py --kapsam kod` calistir, bulgu listesini kaydet (oncesi sayilar).
2. `python scripts/kodlama_denetim.py --duzelt` ile otomatik duzeltmeyi uygula.
3. Tekrar `--kapsam kod` calistir → **exit 0** olmali. Kalan bulgu varsa elle duzelt (BOM/NUL/mojibake asla birakma).
4. `.gitattributes` kontrol: `* text=auto eol=lf` benzeri satir var mi? Yoksa **ekleme onerisi** raporda yaz, dosyayi degistirme (roo karar verir).
5. Tam test suiti: `python -m pytest -q` → yesil olmali. Kirilan test varsa duzelt veya raporda acikca belirt.

## Sinirlar
- Sadece satir sonu / dosya sonu / kodlama duzeltmesi. **Mantik degisikligi YOK.**
- Commit ATMA (roo sabah commitler).
- `.env`, `data/`, `backups/`, `_trash/` dokunma.

## Teslim (5 madde zorunlu)
1. `data/orchestrator/GIT-HIJYEN-01_rapor_2026-09-17_kilo.md` — oncesi/sonrasi bulgu sayilari + degisen dosya sayisi + test sonucu
2. Bilinen failure varsa raporda acik yazili
3. `task_board.json` entry guncel
4. `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id GIT-HIJYEN-01 ...`
5. Testler tekrarlanabilir
