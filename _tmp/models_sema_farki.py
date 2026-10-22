# -*- coding: utf-8 -*-
"""KOK NEDEN ARAYISI: Codex, 9Router /models yanitini neden decode edemiyor?
Olculen hata: 'failed to decode models response: Data at line 1 column 330393
(body: 330393 bytes)'  -> 330393 = 9Router yanitinin tam boyutu.

Iki aday kok neden:
  (1) govde tek JSON degil (NDJSON / birlesik JSON)  -> python da patlardı
  (2) govde geceli JSON ama Codex'in bekledigi ZORUNLU alanlar eksik/tip farkli
Bu betik govdeyi ham + alan bazinda inceler.
"""
import json
import urllib.request

K9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"

req = urllib.request.Request("http://localhost:20128/v1/models",
                             headers={"Authorization": "Bearer " + K9})
with urllib.request.urlopen(req, timeout=40) as r:
    ham = r.read()

print("boyut:", len(ham), "bayt")
print("satir sayisi:", ham.count(b"\n") + 1)
print("BOM var mi:", ham[:3] == b"\xef\xbb\xbf")
print("ilk 90:", repr(ham[:90].decode("utf-8", "replace")))
print("son 90:", repr(ham[-90:].decode("utf-8", "replace")))

# govdede birden fazla JSON var mi? '}{' deseni
bitisik = ham.count(b"}{")
print("bitisik '}{' sayisi:", bitisik)

j = json.loads(ham.decode("utf-8"))
print("ust alanlar:", sorted(j.keys()))
m0 = j["data"][0]
print("model ogge alanlari:", sorted(m0.keys()))
print("orcnek ogge:", json.dumps(m0, ensure_ascii=False)[:300])

# Codex kataloqlarinda gorunen ZORUNLU alanlar: karsilastir
CODEX_BEKLENEN = ["slug", "display_name", "description", "default_reasoning_level",
                  "supported_reasoning_levels", "shell_type", "visibility",
                  "supported_in_api", "priority", "additional_speed_tiers",
                  "service_tiers", "availability_nux", "upgrade",
                  "base_instructions"]
eksik = [a for a in CODEX_BEKLENEN if a not in m0]
print("Codex semasinda OLUP 9Router'da OLMAYAN alanlar:", eksik)
tip = {a: type(m0.get(a)).__name__ for a in sorted(m0)}
print("9Router ogge tipleri:", json.dumps(tip)[:400])
