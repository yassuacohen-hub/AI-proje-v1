"""EVREN chat ucu olcumu (SCRAPE-004 zincirine eklenmeden once dogrulanir)."""
import json
import pathlib
import requests

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
env = (KOK / ".env").read_text(encoding="utf-8-sig")
key = ""
for ln in env.splitlines():
    if "evren_llm_" in ln:
        key = "evren_llm_" + ln.split("evren_llm_", 1)[1].split()[0].strip()
        break

BASE = "https://evren-llmapi.ssyz.org.tr"
H = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

SISTEM = ('Sen NACE siniflandirmaci sin. Verilen metinden SADECE JSON dondur: '
          '{"nace_kodu": "XX.XX", "sektor_adi": "...", "unvan": "...", '
          '"etiket_bos": false}. Bilmiyorsan etiket_bos=true dondur.')
ORNEK = ("06 SIHHAT GRUP IS GUVENLIGI OSGB DANISMANLIK TIC.LTD.STI. "
         "Ankara Ostim Organize Sanayi Bolgesi. Is guvenligi egitimi, "
         "risk analizi ve isyeri sagligi hizmetleri verir.")

for model in ("mimo-v2.6-pro", "auto", "glm-5.3"):
    try:
        r = requests.post(BASE + "/v1/chat/completions", headers=H, timeout=90,
                          json={"model": model, "temperature": 0,
                                "stream": False,
                                "messages": [{"role": "system",
                                              "content": SISTEM},
                                             {"role": "user",
                                              "content": ORNEK}]})
        print(f"--- {model}: HTTP {r.status_code}")
        if r.status_code != 200:
            print("   ", r.text[:160])
            continue
        d = r.json()
        icerik = d["choices"][0]["message"]["content"]
        print("    cevap:", icerik[:220].replace("\n", " "))
        try:
            v = json.loads(icerik)
            print("    JSON OK -> nace:", v.get("nace_kodu"),
                  "| unvan:", v.get("unvan"))
        except ValueError:
            print("    JSON DEGIL (dogrudan ciktida gelmeli)")
        u = d.get("usage", {})
        ev = u.get("evren", {}) if isinstance(u, dict) else {}
        print("    kredi:", ev.get("credits_held_cr"),
              "| kalan:", ev.get("credits_remaining_cr"))
    except Exception as e:
        print(f"--- {model}: HATA {type(e).__name__}: {str(e)[:140]}")