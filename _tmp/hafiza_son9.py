# -*- coding: utf-8 -*-
"""SON-9: Claude kutusuna Evren modelleri + GUVENLIK IHLOLI kaydi (D-380).
Tavan 700 (PO karari). Idempotent; asarsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-9 (2026-10-20 ~23:25 — CLAUDE KUTUSUNA EVREN MODELLERI + GÜVENLİK İHLALİ ÖZ-ELEŞTİRİSİ):** PO: "bat işe yaramadı, kapatınca Claude'da model değişmedi; Claude'un kendi ekranından seçim olmalı, gateway var; Evren modelleri neden listede yok?". **İki ayrı ürün, iki ayrı ayar (ölçüldü):** (a) **Claude Code CLI** `~/.claude/settings.json` `model` alanını **dinliyor** (kanıt: `model=yasu-9router` yazıldı → CLI `modelUsage: ['yasu-9router']` kullandı) — yani bat YÖNTEMİ DOĞRU, CLI'da çalışıyor; (b) **Claude Desktop** o dosyayı okumuyor, kendi kutusu `9Router DB → combos` tablosundan besleniyor (kutudaki tek satır `claude-claudecombo` = combos.name; `kv.scope=customModels` içinde claude/anthropic alias kaydı **0** → kutu customModels değil). **KURULAN:** `scripts/claude_kutuya_evren.py` — Claude kutusuna `claude-` önekli 6 kayıt açar, içine gerçek Evren/bedava modelini koyar; `--durum`, `--sil` (ad + models içeriği birebir eşleşenleri siler, kullanıcının kendi combo'larına dokunmaz), ekleme öncesi DB yedeği (`data.yedek-20261020_230242.sqlite`). **Sonuç 4/6 kutuya girdi ve 2/2 canlı testte metin üretti:** `claude-evren-guclu`→deepseek-v4.1-flash · `claude-evren-derin`→glm-5.3 · `claude-bedava-hizli`→nemotron-3.5-lightning:free · `claude-bedava-ultra`→nemotron-3-ultra-550b. **Elenen 2:** `qwen3.8-flash-next` (503) ve `cx/gpt-5.6-luna` (500 + "Credit balance") — kanal geçersiz/limitli, ölüyü kutuya koymadım. **İKI YANILGI DÜZELTILDI (tekrarlanmasın):** (1) Testi ham `/v1/messages` ile yapmıştım → qwen 503, deepseek/glm/nemotron BOŞ döndü, hepsini "ölü" sanıp ENGELLEDİM; oysa `claude --model X` ile 2/2 metin var. **KURAL: Claude için doğrulama kanalı = `claude --model X -p --output-format json` + `modelUsage`; ham HTTP tek başına kanıt değil (D-382'nin Claude karşılığı).** (2) `combos.kind='alias'` ile ekledim → Anthropic kapısı 400 Bad Request; kutuda görünen `claude-claudecombo`/`fullclaude` kayıtlarının `kind` değeri **NULL** → kind=NULL ile ekleyince çalıştı. **⚠️ GÜVENLİK İHLALİ (kendi hatam, PO'ya bildirildi):** `_tmp/claude_liste_kynak.py` `providerConnections` satırını `data` kolonu dahil MASKELEMEDEN bastı → nvidia/openrouter/cloudflare/tokenrouter/kilo apikey'leri + OAuth token'ları (ya29., ghu_, castai_, workos:) terminal çıktısına düştü (D-380 ihlali). **KURAL (kalıcı): 9Router DB'den okunan HER tablo `data`/`apiKey`/`accessToken` kolonu taşır; yazdırmadan önce desen maskesi ŞART (nvapi-, sk-, eyJ, ya29., ghu_, castai_, workos:, aoaAAAA, cfut_, $2b$10$). `_tmp/claude_istem_gecmisi.py` doğru örnek.** Önerilen telafi: riskli görülen anahtarları gateway'den döndür (PO kararı). **Not:** sistem ortamında `ANTHROPIC_BASE_URL=http://127.0.0.1:8045/` ÖLÜ (netstat: 8045 dinleyici yok, yalnız 20128 LISTEN) — Desktop kendi gateway ayarını kullanır, bu env Claude Code'u etkilemez.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-9 (2026-10-20" in metin:
    print("SON-9 zaten var")
    raise SystemExit(0)

satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-8 (2026-10-20"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))

son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN} · SON-9: {'SON-9 (2026-10-20' in HEDEF.read_text(encoding='utf-8')}")
