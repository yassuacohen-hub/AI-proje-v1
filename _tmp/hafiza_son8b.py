# -*- coding: utf-8 -*-
"""PO KARARI (2026-10-20 ~22:37): 'hafiza dosyasinin sinirlarini genisletebilirsin,
arsiive almadan hafiza genislet'.
-> Arsiv TASINMASI YAPILMAZ. D-219 tavani 400 -> 700 satira cikarilir (PO onayli,
   dipnot olarak dosyanin kendi beyan satirina islenir) ve SON-8 eklenir.
Idempotent; tavan asilirsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
ESKI_TAVAN = "Tavan 400 satır (D-219 Ek, 2026-10-02)"
YENI_TAVAN = ("Tavan 700 satır (D-219 Ek, 2026-10-02 → **PO kararı 2026-10-20 22:37: "
              "400 → 700**, arşive taşımadan genişlet)")
TAVAN = 700

KAYIT = """- **SON-8 (2026-10-20 ~22:35 — CLAUDE MODEL SEÇİCİ KURULDU + ROZET SIRRI ÇÖZÜLDÜ):** PO: "Claude Code'da seçim yapabiliyoruz; modelin adını/özelliğini/hızını göreyim; asıl dosyalar repoda kalsın, masaüstü klasörü hızlı erişim olsun". **Ölçülen kapı farkı:** Claude → `127.0.0.1:20128/v1` + **`/v1/messages`** (Anthropic biçimi); kimlik = **`x-api-key` + `ANTHROPIC_AUTH_TOKEN`**. `ANTHROPIC_API_KEY` ile denersek `401 Invalid API key`, `Bearer` ile `401 Missing API key` (ham gövde okunarak kanıtlandı — hata mesajları farklı, tahminle çözülmezdi). **Claude'da GERÇEK seçim var** (Codex'te yoktu): `claude --model X -p` → 3/3 cevap ve `claude -p --output-format json` içindeki **`modelUsage` anahtarı kullanılan GERÇEK modeli yazar** → "seçim uygulandı mı?" sorusunun kesin cevabı. **SSOT:** `~/.claude/settings.json` (`model: "sonnet"` + `env ANTHROPIC_DEFAULT_*_MODEL`); `sonnet` takma adını ham `/v1/messages`'a göndermek **404** veriyor → araç `hedef_cevir()` ile env'deki gerçek id'ye çeviriyor. **Portföyden elenen model:** `openrouter/nvidia/nemotron-3.5-lightning:free` Anthropic kapısında **BOŞ** döndü (Aynı id Responses kapısında çalışıyor) → Claude listesine konmadı (ölçüm olmadan listeleme yok). **Ölçülen hızlar (2 tekrar, sn):** haiku 1.0 · claude_sadece 1.4 · claude-claudecombo 1.6 · opus 1.7 · sonnet 2.0 · yasu-9router 2.0 · bzl/auto 2.7 · fullclaude 6.0. **TESLİM (repo SSOT + masaüstü kopya):** `scripts/claude_model_sec.py` — tablo + `hizli|combo|opus|sonnet|haiku|hepsi|karma|oto` + `--durum|--test|--ucu-ucu|--geri`; her seçimde CANLI test + yedek + JSON geri-okuma; `scripts/claude_model_menu.bat` (çift tık). Masaüstü `gereksiz\\`: `claude_model_menu.bat`, `claude_model_sec.py`, `codex_model_menu.bat`, `codex_model_sec.py`, `codex_degistir.bat`. Kanıt: `--test` → `completed 1.9s cc/claude-sonnet-5 → CLAUDE-OK`; `--ucu-ucu` → `OK 13.2s ['claude_sadece']`. **ROZET SIRRI (patch→test→revert ile ölçüldü):** Codex sol alt rozeti **sağlayıcının `name` alanını** basıyor, model adını DEĞİL (onca tur "Özel/Evren" yazmasının sebebi). `rozet_guncelle()` yalnız AKTİF provider bloğundaki `name` satırını `"GÜÇ · model"` yapar (blok sınırı `[^\[]*`, sonra `tomllib` ile yeniden parse). Kanıt: isim değişince Codex rc=0 çalışmaya devam etti → güvenli; PO seçiminde rozet `EN-HIZLI · qwen3.8-flash-next` olacak. **Yeni tuzaklar:** (a) kullanıcı ORTAMında `ANTHROPIC_BASE_URL=http://127.0.0.1:8045/` **ÖLÜ port** (connection refused) — gerçek adres `settings.json env`'deki 20128; `set` çıktısına güvenme, SSOT dosyayı oku; (b) 9Router'ın Claude yanıtları çok-nesneli/NDJSON olabiliyor → `json.loads` "Extra data: line 1 column 597" patlatır; süre ölçülür, metin regex ile çıkarılır; (c) `apply_diff` uzun/çok bloklı Türkçe metinde sık patlıyor → tek bloğa böl veya programlık düzenle.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-8 (2026-10-20" in metin:
    print("SON-8 zaten var — dokunulmadı")
    raise SystemExit(0)

if ESKI_TAVAN in metin:
    metin = metin.replace(ESKI_TAVAN, YENI_TAVAN, 1)
    print("TAVAN guncellendi:", YENI_TAVAN.split("(")[0].strip())

satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-7 (2026-10-20"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))

son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > TAVAN {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
geri = HEDEF.read_text(encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN} · SON-8: {'SON-8 (2026-10-20' in geri} ·"
      f" tavan beyani guncel: {'PO kararı 2026-10-20 22:37' in geri}")
