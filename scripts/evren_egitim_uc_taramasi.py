"""EVREN: egitim/fine-tune ucu var mi? Canli API taramasi (D-260)."""
import json
import pathlib
import urllib.request
import urllib.error

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
OUT = pathlib.Path(r"C:\Users\yasin\AppData\Local\Temp\evren_api_taramasi.txt")

anahtar = None
for satir in (KOK / ".env").read_text(encoding="utf-8-sig").splitlines():
    s = satir.strip()
    if "evren_llm_" in s:
        anahtar = "evren_llm_" + s.split("evren_llm_", 1)[1].split()[0].strip()
        break

BASE = "https://evren-llmapi.ssyz.org.tr/v1"
PANEL = "https://api.ssyz.org.tr/api/v1"
HDR = {"X-API-Key": anahtar, "Content-Type": "application/json"}

lines = [f"Anahtar: ...{anahtar[-4:]}", ""]


def cek(url, method="GET", hdr=None):
    h = dict(HDR)
    if hdr:
        h.update(hdr)
    req = urllib.request.Request(url, data=None if method == "GET" else b"",
                                 method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, f"{type(e).__name__}"


lines.append("=== 1) KULLANILABILIR UC TARAMASI (API anahtariyla) ===")
UCLER = [
    "/fine_tuning/jobs", "/fine-tuning/jobs", "/fine_tune", "/finetune",
    "/training/jobs", "/jobs", "/train", "/tuning", "/adapters",
    "/models/fine-tunable", "/embeddings", "/rerank", "/ocr",
    "/audio/transcriptions", "/responses", "/chat/completions", "/models",
]
for u in UCLER:
    st, ic = cek(BASE + u)
    lines.append(f"  {st:<5} GET {u}")
    if st not in (404, 405, 401):
        lines.append(f"        -> {ic[:130]}")

lines.append("\n=== 2) KATALOGDAKI TASK/MODEL ALANLARI ===")
st, ic = cek(BASE + "/models")
if st == 200:
    try:
        kat = json.loads(ic).get("data", [])
        lines.append(f"  model sayisi: {len(kat)}")
        anahtarlar = set()
        for m in kat:
            anahtarlar.update(m.keys())
        lines.append(f"  alanlar: {sorted(anahtarlar)}")
        lines.append("  fine-tune/egitim alani var mi: "
                     f"{[a for a in anahtarlar if 'fine' in a.lower() or 'train' in a.lower() or 'tune' in a.lower()] or 'HAYIR'}")
    except Exception as e:
        lines.append(f"  parse hatasi: {e}")

lines.append("\n=== 3) PANEL API (evren.ssyz.org.tr yonetici uclari) ===")
for u in ["/llm/finetuning", "/llm/training", "/llm/jobs", "/llm/models",
          "/llm/pricing", "/llm/quotas", "/llm/key-policies", "/training/jobs",
          "/gpu", "/billing", "/llm/credits"]:
    st, ic = cek(PANEL + u)
    lines.append(f"  {st:<5} GET {u}")
    if st == 200:
        lines.append(f"        -> {ic[:160]}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
