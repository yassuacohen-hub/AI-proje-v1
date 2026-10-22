# -*- coding: utf-8 -*-
"""SON-6 kaydini hafizaya ekle (uygulayici: c5-670121384888, 20.10.2026 21:31).
Kisa tutulur: D-219 tavani 400 satir. Ayni kayit varsa tekrar eklemez (idempotent)."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
ÇAPA = "- **Çevre kirliliği (kısmen temizlendi 20.10 ~21:01):**"

KAYIT = """- **SON-6 (2026-10-20 ~21:30 — GUI TAKILMASI KÖKTEN ÇÖZÜLDÜ (TAKMA AD) + 2. HATA PENCERESİ KAPATILDI):** PO: "terminalde çalışıyor, Codex arayüzünde yazınca 'Düşünüyor'da takılıyor". **Kök neden (ölçüldü):** GUI, listeden her seçimde `config.toml`'a KENDİ katalog adını yazıyor (`gpt-5.6-sol`, `deepseek-v4.1-flash`, `glm-5.3`); aktif sağlayıcı 9Router olduğu için o adların karşılığı yok → ekranda okunan gerçek hata: `503 [codex/gpt-5.6-sol] [400] The 'gpt-5.6-sol' model is not supported when using Codex with a ChatGPT account` → sohbet donuyor. **ÇÖZÜM = takma ad:** 9Router `combos` kayıtları `/v1/models`'da id olarak görünüp `/responses`'ta ÇALIŞIYOR (kanıt: `fullclaude`) → GUI'nin yazdığı 14 ada combo açıldı, her biri CANLI modele bağlandı → `scripts/codex_gui_takma_ad.py` (`--durum`, `--test`; DB yedeği `data.yedek-20261020_212102.sqlite`, sadece INSERT). Kanıt: **14/14 takma ad `completed` (3-9 sn)** → "GUI'den seçim yapma" yasağı KALKTI (`~/.codex/MODELLER.md` güncellendi). **Ölü kanal bulgusu:** `cl/*`, `kimchi/*`, `tokenrouter/*` deepseek/glm kanalları 503, `nvidia/*` 410 Gone (hesapsız); `cx/gpt-5.6-sol` da 503 (hesap desteklemiyor) → takma adlar ücretsiz çalışan Nemotron/luna'ya bağlandı. **2. hata penceresi:** `kombo_senkron_bekcisi.vbs:6` olmayan `C:\\Program Files\\Python312\\python.exe` yolunu çağırıyordu → WScript 80070002 popup; `_tmp/vbs_yama.py` ile gerçek yola yamalandı (bayt düzeyi, `.yedek-20261020`), `wscript` rc=0 + stderr boş. **Bilinçli dokunulmayan zararlılar:** `MCP notebooks/data-agent-kit/visualization failed` (Cursor'ın `\\pipe\\datacloud-mcp-*` borularına bağlı, Cursor kapalıyken ölür), `Skill descriptions shortened` (bağlam bütçesi uyarısı). **PO teslimi:** `C:\\Users\\yasin\\OneDrive\\Desktop\\gereksiz\\` → `codex_model_menu.bat` + `codex_model_sec.py`.
- **Tuzak (yeni, kalıcı): Windows'ta `.vbs`/betik içinde SABİT Python yolu = saatli bomba.** Ölç: `py --list-paths` / `where python`; üretimde `sys.executable` kullan. Aynı sınıf: `bash` isteyen eklenti (SON-5) + sabit `C:\\Program Files\\Python312` (SON-6).
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-6 (2026-10-20" in metin:
    print("SON-6 zaten kayıtlı — dokunulmadı")
else:
    if ÇAPA not in metin:
        raise SystemExit("ÇAPA bulunamadı — dosya yapısı değişmiş, elle kontrol et")
    yeni = metin.replace(ÇAPA, KAYIT + ÇAPA, 1)
    HEDEF.write_text(yeni, encoding="utf-8")
    geri = HEDEF.read_text(encoding="utf-8")
    print("EKLENDI · SON-6 var mi:", "SON-6 (2026-10-20" in geri,
          "· satir sayisi:", geri.count("\n") + 1)
