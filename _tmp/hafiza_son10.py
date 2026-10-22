# -*- coding: utf-8 -*-
"""SON-10: Claude Desktop model kutusu (inferenceModels) bulundu ve dolduruldu.
Tavan 700. Idempotent; asarsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-10 (2026-10-20 ~23:40 — CLAUDE DESKTOP'UN MODEL KUTUSU BULUNDU VE DOLDURULDU: ARAYÜZDEN SEÇİM MÜMKÜN):** PO: "bat işe yaramadı, kapatınca model değişmiyor; Claude'un kendi ekranından seçim olmalı, gateway var; Evren modelleri neden yok?" ve resmi doküman linkini verdi. **Doğru adres (ölçüldü):** `AppData\\Local\\Claude-3p\\configLibrary\\<appliedId>.json` — `_meta.json → appliedId` ile bulunur. **Resmî şema (claude.com/docs/third-party/claude-desktop/configuration, `#models`):** `inferenceModels` = `[{name, labelOverride, anthropicFamilyTier, supports1m, prefer1m, isFamilyDefault}]`; `name` **gateway'in `/v1/models` döndürdüğü birebir id** olmalı; `labelOverride` seçicide görünen yazı; **ilk kayıt varsayılan**; **liste doluysa otomatik keşif atlanır** → PO'nun tek satır görmesinin sebebi listede 1 kayıt olmasıydı (`claude-claudecombo` + `anthropicFamilyTier: sonnet`). **TESLİM:** `scripts/claude_kutu_doldur.py` — `--durum` / (varsayılan: adayları kapıdan test et + yaz) / `--geri` (yedekten tam geri yükleme); yazım öncesi yedek `~/.claude/yedek/claude3p.*.json` + eski liste ayrı dosyada + JSON geri-okuma doğrulaması, başarısızsa otomatik geri yükleme. **Sonuç 9 model kutuya yazıldı** ve hepsi `/v1/messages` kapısından 2/2 metin üretti: combo(~2sn) · claude_sadece(~1) · haiku(~0.7) · sonnet(~2) · opus(~1.7) · mimir-dis(~1.5) · fullclaude(~2.4) · **EVREN Ultra 550B (~2.3, ücretsiz)** · claude-bedava-ultra(~1.3). **Elenen 5 (ölçüldü, ölü model kutuya konmaz):** `yasu-9router` BOŞ, `bzl/auto:free` 503, `claude-evren-guclu`/`claude-evren-derin`/`claude-bedava-hizli` BOŞ. **ETİKETTE HIZ UYDURMASI YASAĞI (kendi hatam):** ilk sürümde hızları elle yazdım ("ultra ~4sn"), ölçüm 28sn verdi → etiketi `kapidan_olculen_sn` ile üretilen değere çevirdim. **Tuzağa ekle:** (1) Claude **Desktop** `~/.claude/settings.json` `model` alanını OKUMAZ; **Claude Code CLI** okur (kanıt SON-9) — "bat işe yaramadı" şikâyeti ürün ayrımı, bozukluk değil. (2) Claude Desktop MSIX içinde (`C:\\Program Files\\WindowsApps\\Claude_2.42304.0.0_x64__pzs8sxrjxfjjc\\app\\Claude.exe`) → `app.asar` şeması taranamadı, şema RESMİ DOKÜMANDAN alındı; tahminle alan adı uydurmak yerine doküman oku. (3) `%LOCALAPPDATA%\\Claude` içinde yalnız `logs` var; config `Claude-3p` altında. **Ayrıca** `combos` tablosuna `claude-` önekli 6 alias açıldı (`scripts/claude_kutuya_evren.py`, `--sil` ile geri alınır, DB yedeği `data.yedek-20261020_230242.sqlite`) — ancak Desktop kutusu `inferenceModels`'i okuduğu için asıl çözüm SON-10 aracıdır.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-10 (2026-10-20" in metin:
    print("SON-10 zaten var")
    raise SystemExit(0)

satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-9 (2026-10-20"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))

son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN} · SON-10: {'SON-10 (2026-10-20' in HEDEF.read_text(encoding='utf-8')}")
