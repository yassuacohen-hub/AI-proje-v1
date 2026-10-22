# -*- coding: utf-8 -*-
"""CODUX GUI MODEL LİSTESİ TEŞHİSİ.
Codex logunda ölçülen hata: 'failed to decode models response:
Data at line 1 column 330393 (body: 330393 bytes)' -> GUI listesi bu
ucun sonucunu kullanir; decode bozulursa listede sadece bayat tek model kalir.
Anahtarlar ELLE yazilmaz, kaynaktan okunur (hafiza kurali 20.10)."""
import json
import pathlib
import urllib.request

K9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
_d = json.loads(pathlib.Path(r"C:\Users\yasin\zoo-9router-import.json")
                .read_text(encoding="utf-8"))
KEV = next(p["openAiApiKey"] for p in _d["providerProfiles"]["apiConfigs"].values()
           if "evren" in p.get("openAiBaseUrl", ""))
print("evren anahtar uzunlugu:", len(KEV), "ascii:", KEV.isascii())


def olc(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=40) as r:
        ham = r.read()
    try:
        j = json.loads(ham.decode("utf-8"))
        idler = [m.get("id") for m in j.get("data", [])]
        print(f"  DECODE OK · {len(idler)} model · {len(ham)} bayt")
        print("  ilk 12:", ", ".join(str(i) for i in idler[:12])[:220])
        # GUI listesini bozan tuhafliklar: tekrar id, bos id, id disinda alan
        tekrarl = len(idler) - len(set(idler))
        bos = sum(1 for i in idler if not i)
        print(f"  tekrar id: {tekrarl} · bos id: {bos}")
    except json.JSONDecodeError as e:
        print(f"  DECODE BOZUK: {e} · {len(ham)} bayt")
        print("  KUYRUK:", repr(ham[-160:].decode("utf-8", "replace")))
        bas = ham[:160].decode("utf-8", "replace")
        print("  BAS:", repr(bas))
    return ham


print("\n[1] 9router /v1/models")
olc("http://localhost:20128/v1/models", K9)

print("\n[2] evren /v1/models")
olc("https://evren-llmapi.ssyz.org.tr/v1/models", KEV)

print("\n[3] Codex onbellege dosyasi")
p = pathlib.Path.home() / ".codex" / "models_cache.json"
if p.exists():
    ham = p.read_bytes()
    j = json.loads(ham.decode("utf-8"))
    print("  boyut:", len(ham), "· fetched_at:", j.get("fetched_at"),
          "· client_version:", j.get("client_version"))
    modlar = j.get("models", [])
    gorunur = [m.get("slug") for m in modlar if m.get("visibility") != "hide"]
    print("  toplam model:", len(modlar), "· GUI'de gorunur:", len(gorunur))
    print("  gorunur sluglar:", ", ".join(str(s) for s in gorunur)[:400])
else:
    print("  ONBELLEK YOK")
