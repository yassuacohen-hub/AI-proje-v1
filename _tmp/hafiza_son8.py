# -*- coding: utf-8 -*-
"""SON-8 kaydini ekler; D-219 tavani (400 satir) asmamalik icin ONCE eskiyeni arsivler.
Yontem (BILGISIZ silme YOK): SON, SON-2, SON-3, SON-4 maddeleri TAM METNIYLE
ihsan_project_context_arsiv.md'ye tasinir; ana dosyaya tek satir isaret birakilir.
Idempotent: arsivlenmis-se bulursa tekrar tasimaz; SON-8 varsa dokunmaz."""
import datetime as dt
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
ARSIV = Path(r"c:\Huginn Data Projesi\Huginn Data Insights"
             r"\ihsan_project_context_arsiv.md")
TASINACAK = ("- **SON (2026-10-20 ~19:55", "- **SON-2 (2026-10-20 ~20:10",
             "- **SON-3 (2006", "- **SON-3 (2026-10-20 ~20:28",
             "- **SON-4 (2026-10-20 ~20:47")
ISARET = ("- **SON / SON-2 / SON-3 / SON-4 (19:55-20:47) → TAM METIN ARSIVDE:** "
          "`ihsan_project_context_arsiv.md`. Ozet: 9 profil + `evren` saglayicisi "
          "kuruldu; `codex_model_sec.py` + `codex_model_menu.bat` dogdu; GUI listesi "
          "format uyuşmazlığından boş kalır (düzeltilmez); `cc/*` 503 = OAuth token "
          "revoked; 4 bozuk zamanlanmis gorev devre disi; **D-382: Codex profili "
          "dogrulamasi `codex -p X exec` ile ucdan uca, ham HTTP ayristirmasi tek "
          "kanit degil.**")

KAYIT = """- **SON-8 (2026-10-20 ~22:33 — CLAUDE MODEL SEÇİCİ KURULDU + ROZET SIRRI):** PO: "Claude Code'da seçim yapabiliyoruz, model bilgisini/hızını göreyim; repo SSOT, masaüstü hızlı erişim". **Ölçülen kapı farkı:** Claude → `127.0.0.1:20128/v1` + **`/v1/messages`** (Anthropic biçimi), kimlik = **`x-api-key` + `ANTHROPIC_AUTH_TOKEN`**; `ANTHROPIC_API_KEY` ile → `401 Invalid API key`, `Bearer` ile → `401 Missing API key` (ham gövde okunarak kanıtlandı). **Claude'da GERÇEK seçim var** (Codex'te yoktu): `claude --model X -p` → 3/3 cevap; `claude -p --output-format json` → **`modelUsage` anahtarı kullanılan GERÇEK modeli yazar** (seçim kanıtı; combo seçilince orada göründü). **SSOT:** `~/.claude/settings.json` → `model: "sonnet"` + `env ANTHROPIC_DEFAULT_*_MODEL`; `sonnet` takma adını ham `/v1/messages`'a göndermek **404** veriyor → `hedef_cevir()` env ile çözüyor. **Portföyden elenen:** `openrouter/nvidia/nemotron-3.5-lightning:free` Anthropic kapısında **BOŞ** döndü (Responses kapısında çalışıyor) → Claude listesine konmadı. **Ölçülen hızlar (2 tekrar, sn):** haiku 1.0 · claude_sadece 1.4 · claude-claudecombo 1.6 · opus 1.7 · sonnet 2.0 · yasu-9router 2.0 · bzl/auto 2.7 · fullclaude 6.0. **TESLİM:** `scripts/claude_model_sec.py` (tablo/`hizli|combo|opus|sonnet|haiku|hepsi|karma|oto`/`--durum`/`--test`/`--ucu-ucu`/`--geri`; her seçimde canlı test + yedek + JSON geri-okuma) ve `claude_model_menu.bat`; masaüstü `gereksiz\\` = 4 dosya (codex+claude menü/seçici, `codex_degistir.bat`). **ROZET SIRRI (ölçüldü, patch→test→revert):** Codex sol alt rozeti **sağlayıcının `name` alanını** basıyor (model adını değil) → `rozet_guncelle()` yalnız AKTİF provider bloğundaki `name` satırını `"GÜÇ · model"` yapar (`[^\[]*` blok sınırı + `tomllib` yeniden-parse); kanıt: isim değiştiğinde Codex çalışmaya devam etti (rc=0), sonra eski adı geri döndü; seçim sonrası rozet `EN-HIZLI · qwen3.8-flash-next`. **Tuzağa yeni ekle:** (a) kullanıcı ortamında `ANTHROPIC_BASE_URL=http://127.0.0.1:8045/` **ÖLÜ port** (connection refused) — settings.env kazanır, `set` çıktısına güvenme; (b) 9Router Claude yanıtları NDJSON/çok-nesne olabiliyor → `json.loads` "Extra data" patlatır, süre ölçülür ama metin regex ile çıkarılır.
"""

metin = HEDEF.read_text(encoding="utf-8")

if "SON-8 (2026-10-20" in metin:
    print("SON-8 zaten var — dokunulmadı")
    raise SystemExit(0)

# 1) tasima
satirlar = metin.splitlines()
tasinan, kalan = [], []
for s in satirlar:
    if any(s.startswith(p) for p in TASINACAK) and "ARSIVDE" not in s:
        tasinan.append(s)
    else:
        kalan.append(s)
print("tasinacak madde:", len(tasinan))

if tasinan:
    if not ARSIV.exists():
        ARSIV.write_text("# İhsan hafıza ARŞİVİ (D-219 tavanı için taşındı)\n\n"
                         "> Kaynak: `ihsan_project_context.md` · taşındı: "
                         + dt.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n",
                         encoding="utf-8")
    arsiv_metin = ARSIV.read_text(encoding="utf-8")
    yeni_blok = "\n\n".join(tasinan)
    for parca in tasinan:
        if parca[:60] not in arsiv_metin:
            arsiv_metin = arsiv_metin.rstrip() + "\n\n" + parca + "\n"
    ARSIV.write_text(arsiv_metin, encoding="utf-8")
    if ISARET not in "\n".join(kalan):
        # isareti ilk tasinan maddenin oldugu yere koy (sirayi korur)
        for i, s in enumerate(satirlar):
            if any(s.startswith(p) for p in TASINACAK) and "ARSIVDE" not in s:
                kalan.insert(min(i, len(kalan)), ISARET)
                break
    metin_yeni = "\n".join(kalan) + "\n"
    print("arsiv satir sayisi:", ARSIV.read_text(encoding='utf-8').count(chr(10)) + 1)
else:
    metin_yeni = metin
    print("arsivlenecek yeni madde yok")

# 2) SON-8 ekle (SON-7'den hemen sonra)
if "ARSIVDE" in metin_yeni:
    satirlar = metin_yeni.splitlines()
else:
    satirlar = metin_yeni.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-7 (2026-10-20"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))

son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > 400:
    raise SystemExit(f"TAVAN ASILACAK ({sayi} > 400) — yazilmadi, elle kisalt")
HEDEF.write_text(son, encoding="utf-8")
print("YAZILDI · satir:", sayi, "· SON-8 var mi:", "SON-8 (2026-10-20" in son,
      "· isaret satiri var mi:", "ARSIVDE" in son)
