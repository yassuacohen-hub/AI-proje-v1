# -*- coding: utf-8 -*-
"""SON-13: Claude Desktop picker 'claude' iceren id filtresi + qwen/gorsel kanalli
olcumu (402/429). Tavan 700; asarsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-13 (2026-10-21 ~00:40 — KLAVYE TUZAGI: CLAUDE DESKTOP KUTUSU YALNIZ ADINDA `claude` GECEN ID'LERI GOSTERIYOR):** PO: "acip kapattim hersey tamam ama QWEN yok, Evren icin gorsel ureten de yok; liste bu kadar" + ekran fotografi (10 satir). **KESIN KURAL D (olculen):** config'de 18 kayit vardi, ekranda 10. Gorene 10/10'un adinda `claude` geciyor (`claude-claudecombo`, `claude_sadece`, `cc/claude-*`, `fullclaude`, `claude-evren-*`, `claude-bedava-*`); kaybolan 8/8'de YOK (`yasu-9router`, `mimir-dis`, `cl/nvidia/nemotron-3-ultra…:free`, `qwen3.8-flash-next`, `deepseek-v4.1-flash`, `glm-5.3`, `cl/nvidia/nemotron-3.5-super-vl:free`, `openrouter/nvidia/nemotron-3-nano-omni…:free`). **Etiket yetmez** — 'Karma Claude+Evren' etiketli `yasu-9router` da gorunmuyordu → filtre **id** uzerinden. **Cozum (kuruldu):** `scripts/claude_kutu_onek.py` → `claude-` onekli combo acar (`kind=NULL`, DB yedegi `data.yedek-20261021_003453.sqlite`, `--sil` ile geri): `claude-karma-evren`→yasu-9router (TAMAM), `claude-mimir`→mimir-dis (TAMAM), `claude-gorsel-okur`→super-vl, `claude-akilyuruten`→nano-omni, `claude-qwen-flash`→qwen3.8-flash-next, `claude-qwen-bedava`→`cf/@cf/qwen/qwq-32b`, `claude-qwen-coder`→`cf/@cf/qwen/qwen2.5-coder-32b-instruct`. ADAYLAR tablosu bu oneklere tasindi → **16 kayit, hepsi claude iceriyor** (yedek `claude3p.20261021_003809.json`). **QWEN GERCEGI (64 qwen kanali tek tek olculdu — `scripts/claude_gorsel_qwen_tara.py`):** TAMAM veren YOK. Dagilim: ~35 kanal `402 insufficient_credits` (cline bakiyesi **-0.13 $**), 4 kanal `429 gunluk 60 istek limiti` (00:00 UTC sifirlanir: `qwen3.8-flash-next`, `cf/@cf/qwen/qwq-32b`, `qwq`, `qwen2.5-coder-32b`), kalanlar 503/401/410. → Qwen **olumedi, kotasi bugun tukendi**; kutuda gorunuyor + etiketi sebebi soyluyor (ZORLA listesi). **GORSEL URETIM GERCEGI (11 gorsel model + `/v1/images/generations` olculdu):** hepsi `402 para` veya `401 Missing API key` (images ucu farkli kimlik istiyor). `evren/` onekli model sayisi **0**. → Bedava gorsel URETEN kanal yok; secenekler: (i) Cline bakiyesi yukle, (ii) sabah kota sifirlaninca qwen'i dene, (iii) tasarım KODU (HTML/CSS/React/SVG) uretimi calisiyor. **Arac hatasi + duzeltme:** `claude_tasarim_aday.py` eski parser kullaniyordu (SSE'yi BOS sanar) → yeni arac iki bicimi de okuyor. **Cift `ZORLA` tanimi** refactor artigi kalmisti (ikincisi ilkini eziyordu) → silindi. Amac onbellegi yeni combo adlarina devredildi (kota korunur). Kavuza 13. tuzak eklendi.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-13 (2026-10-21" in metin:
    print("SON-13 zaten var")
    raise SystemExit(0)
satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-12 (2026-10-21"):
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
