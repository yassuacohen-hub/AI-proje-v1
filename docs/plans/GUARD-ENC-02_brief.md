# GUARD-ENC-02 — kodlama_denetim genişletme (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-01_ortak_kurallar.md`. Zincir halkası 3/6.

## Kapsam
- `scripts/kodlama_denetim.py`, `tests/test_kodlama_denetim.py`, `data/kodlama_allowlist.json`.
- `.pre-commit-config.yaml` yalnız yeni bayrak gerekiyorsa.

## İş
1. Yeni ihlal kodları (mevcut BOM/NUL/mojibake/compile korunur):
   - `crlf_karisik`: aynı dosyada hem `\r\n` hem `\n`.
   - `sondaki_bosluk`: satır sonu whitespace (`.py`, `.md`, `.toml`, `.yaml`).
   - `tab_girinti`: `.py` dosyasında tab ile girinti.
   - `dosya_sonu`: son satırda newline yok.
2. `--fix` bu 4 kodu da düzeltir (CRLF → LF, trailing ws sil, tab → 4 boşluk yalnız girintide, EOF newline ekle). Düzeltme **idempotent** (ikinci koşu 0 değişiklik).
3. `--sadece-degisen` (git staged+worktree) modu mevcutsa yeni kodlar için de çalışır.
4. Allowlist: `data/kodlama_allowlist.json` yeni kod anahtarları (`crlf`, `bosluk`, `tab`, `eof`) — mevcut biçimle uyumlu.
5. Testler: her kod için pozitif/negatif + fix idempotency + allowlist muafiyeti (tmp_path, gerçek repoya yazma YOK).
6. Repo taraması: yeni kodlarla `python scripts/kodlama_denetim.py` çalıştır; ihlal sayılarını rapora yaz. **Toplu `--fix` UYGULAMA** (FMT-01 ve sabah roo kararı); yalnız kendi değiştirdiğin dosyalar temiz olsun. Gerekirse geçici allowlist ile temiz çıkar, rapora listeyi yaz.

## Teslim kriteri
- Mevcut denetim davranışı geriye uyumlu (eski testler yeşil).
- Tam süit yeşil; `python scripts/kodlama_denetim.py` temiz.
- Rapor: `data/orchestrator/GUARD-ENC-02_rapor_<tarih>_kilo.md` (kod başına ihlal sayısı tablosu).
