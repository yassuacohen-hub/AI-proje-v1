# -*- coding: utf-8 -*-
"""Evren ucretsiz model canli testi (D-382 olcum oncesi kanit)."""
import json
import urllib.request

BASE = "https://evren-llmapi.ssyz.org.tr/v1"
KEY = "evren_llm_BZ2d6Zxirtse1n5ehKgLDp_3h4LVnSXCJBc3BYWD70M"
MODELS = ["deepseek-v4.1-flash", "glm-5.3", "qwen3.8-flash-next",
          "gemma-4-31b", "mimo-v2.6-pro", "qwen3-vl-30b", "auto"]


def istek(yol, veri=None):
    req = urllib.request.Request(
        BASE + yol,
        data=json.dumps(veri).encode() if veri else None,
        headers={"Authorization": "Bearer " + KEY,
                 "Content-Type": "application/json"},
        method="POST" if veri else "GET")
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def main():
    sonuc = {"models_liste": "HATA", "chat": {}}
    try:
        lst = istek("/models")
        idler = sorted(m.get("id", "") for m in lst.get("data", []))
        sonuc["models_liste"] = idler
    except Exception as e:  # noqa: BLE001
        sonuc["models_liste"] = f"HATA: {e}"
    for m in MODELS:
        try:
            r = istek("/chat/completions", {
                "model": m, "max_tokens": 200,
                "messages": [{"role": "user", "content": "Sadece OK yaz."}]})
            ch = (r.get("choices") or [{}])
            msg = ch[0].get("message") or {}
            metin = (msg.get("content") or msg.get("reasoning_content")
                     or msg.get("reasoning") or "").strip()
            if metin:
                sonuc["chat"][m] = f"TAMAM: {metin[:40]!r}"
            else:
                sonuc["chat"][m] = f"BOS: {json.dumps(r, ensure_ascii=False)[:150]}"
        except Exception as e:  # noqa: BLE001
            sonuc["chat"][m] = f"HATA: {e}"
    out = "_tmp/evren_test_sonuc.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("YAZILDI:", out)
    for m, s in sonuc["chat"].items():
        print(("OK " if s.startswith("TAMAM") else "XX ") + m + " -> " + s[:70].encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
