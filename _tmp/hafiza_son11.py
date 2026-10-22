# -*- coding: utf-8 -*-
"""SON-11: (1) SSE akis parser korlugu (D-382 tekrari), (2) kind='alias' combo'lar
/v1/models'da YAYINLANMIYOR kesfi, (3) qwen gunluk limiti, (4) gorsel kanallari.
Tavan 700; asarsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-11 (2026-10-21 ~00:00 — CLAUDE KUTUSU 17 MODELE ÇIKTI + İKİ YENİ KESİN KURAL):** PO: "Evren modellerinin tamamı yok, özellikle qwen flash; hız yazma, yerine hangi 9Router combo'su geliyor yaz; tasarım/görsel/sunum modellerini de ekle; 9 model kalsın". **KESİN KURAL A (ölçüldü, D-382'nin 2. tekrarı):** 9Router Claude kapısında cevaplar **SSE akışı** olarak gelebiliyor (`event: content_block_delta` + `data:{...,"delta":{"text":...}}`); düz `"text":"..."` arayan parser bu modelleri **"BOŞ"** sanıyordu → qwen/deepseek/glm/nemotron aslında ÇALIŞIYOR, ben haksızca elemiştim. Araçta artık `metin_ve_hedef()` hem düz JSON hem akış gövdesini okur. **KESİN KURAL B (ölçüldü, çok değerli):** 9Router `combos.kind` değeri **`'alias'` olanlar `/v1/models`da HİÇ YAYINLANMIYOR (0/14), `NULL` olanların TAMAMI yayınlanıyor (9/9 → düzeltme sonrası 12/12)**. Codex GUI'sine alias eklerken kind=NULL şart. `scripts/claude_alias_gorunur.py` (`--duzelt`: qwen/deepseek/glm kind→NULL, DB yedeği `data.yedek-20261020_235859.sqlite`; Codex alias'larına `gpt-*` diye DOKUNULMADI çünkü Codex tarafı alias'ları takma ad olarak kullanıyor). **qwen ÖLMEMİŞTİ:** hata gövdesi `[bazaarlink/auto:free] [429] You have reached the daily limit of 60 free-model requests (resets 00:00 UTC)` → **geçici limit**, kalıcı arıza ile karıştırılmamalı; araç artık `LİMİTTE` / `PARALI KANAL (402)` / `HTTP xxx` diye AYRI yazıyor. **Ayrıca dikkat:** `qwen3.8-flash-next` combo'sunun hedefi `bzl/auto:free` (yani Evren qwen değil, oto-seçici) — etiket bunu saklamıyor, PO'ya sözlü söylendi. **GÖRSEL/TASARIM gerçeği (ölçüldü):** görsel ÜRETEN kanalların hepsi kapalı — `cl/google/*-image`, `cl/openai/gpt-5-image*` → 503; `cl/qwen/*` → 402 `insufficient_credits (bakiye -0.13$)`; `openrouter/minimax-m3:free`, `gemma-4-31b-it:free` → 503/limit. Kutuya ölü model KONMAZ; bunun yerine **görsel OKUYAN** `cl/nvidia/nemotron-3.5-super-vl:free` eklendi (ekran görüntüsü分析ı → tasarım revizyonu için yeterli) ve tüm kutu **tasarım KODU** (HTML/CSS/React/SVG/slayt) üretimi için çalışıyor. **Etiket formatı PO isteğiyle değişti:** hız yerine `ÖZELLİK · ardindaki-gercek-model` (ör. `EVREN DeepSeek · ÜCRETSİZ · nemotron-3.5-lightning:free`) → combo'nun gerçekten kimi çağırdığı ekranda görünür. **Sonuç: 17 model kutuda**, hepsi kapıdan geçti (biri limit uyarısıyla). Yeni araçlar: `claude_kutu_aday_test.py` (aday havuzu + kapı testi), `claude_tasarim_aday.py` (vision/tasarım taraması), `claude_ham_govde.py` (ham gövde okuma), `claude_alias_gorunur.py`. **DERS (kalıcı): bir modelin 'ölü' olduğuna karar vermeden önce HAM gövdeyi oku; hata kodu (429/402/503) ve govde bicimi (JSON/SSE) farklı eylemler gerektirir. **
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-11 (2026-10-21" in metin:
    print("SON-11 zaten var")
    raise SystemExit(0)
satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-10 (2026-10-20"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))
son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN}")
