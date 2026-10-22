# -*- coding: utf-8 -*-
"""Çok satırlı JSON gövdeye dayanıklı ücretsiz model testi + Evren /responses gövde kontrolü."""
import json
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
EVRN = "evren_llm_BZ2d6Zxirtse1n5ehKgLDp_3h4LVnSXCJBc3BYWD70M"


def govde_ayristir(metin):
    """İlk tam JSON nesnesini döndür (9Router çok satırlı gövde atabiliyor)."""
    try:
        return json.loads(metin)
    except json.JSONDecodeError:
        for satir in metin.splitlines():
            satir = satir.strip()
            if satir.startswith("{"):
                try:
                    return json.loads(satir)
                except json.JSONDecodeError:
                    continue
        # iç içe satırları birleştirerek dene
        for i, satir in enumerate(metin.splitlines()):
            if satir.strip().startswith("{"):
                try:
                    return json.loads("".join(metin.splitlines()[i:]))
                except json.JSONDecodeError:
                    continue
    return None


def chat(url, key, model):
    body = {"model": model, "max_tokens": 200,
            "messages": [{"role": "user", "content": "Sadece OK yaz."}]}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            j = govde_ayristir(r.read().decode("utf-8", "replace"))
        if not j:
            return "BOZUK-GOVDE"
        msg = ((j.get("choices") or [{}])[0] or {}).get("message") or {}
        metin = (msg.get("content") or msg.get("reasoning_content")
                 or msg.get("reasoning") or "").strip()
        return ("TAMAM " + repr(metin[:25])) if metin else "BOS"
    except Exception as e:  # noqa: BLE001
        govde = ""
        if hasattr(e, "read"):
            try:
                govde = e.read().decode("utf-8", "replace")[:80]
            except Exception:  # noqa: BLE001
                pass
        return f"HATA {str(e)[:50]} {govde[:60]}"


def responses(url, key, model):
    body = {"model": model, "input": "Say only OK", "stream": False}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            ham = r.read().decode("utf-8", "replace")
        j = govde_ayristir(ham)
        if not j:
            return "BOZUK-GOVDE " + repr(ham[:80])
        durum = j.get("status", "?")
        metin = json.dumps(j.get("output", ""))[:120]
        return f"TAMAM status={durum} govde={metin[:90]}"
    except Exception as e:  # noqa: BLE001
        return f"HATA {str(e)[:60]}"


def main():
    sonuc = {}
    for m in ["bzl/auto:free", "cl/minimax/minimax-m3.1-flash:free",
              "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
              "kc/nvidia/nemotron-3.5-lightning:free",
              "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
              "kc/cohere/north-mini-code:free",
              "openrouter/poolside/laguna-s-2.1:free",
              "openrouter/poolside/laguna-xs-2.1:free",
              "kc/dots-studio/dots-3-note-preview:free",
              "kc/openrouter/free",
              "openrouter/z-ai/glm-5.2:free",
              "openrouter/google/gemma-4-31b-it:free"]:
        sonuc["9r:" + m] = chat("http://localhost:20128/v1/chat/completions", KEY9, m)
    sonuc["evren:/responses"] = responses(
        "https://evren-llmapi.ssyz.org.tr/v1/responses", EVRN, "glm-5.3")
    sonuc["9r:/responses"] = responses(
        "http://localhost:20128/v1/responses", KEY9,
        "openrouter/nvidia/nemotron-3.5-lightning:free")
    with open("_tmp/free_test2_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    for m, s in sonuc.items():
        print(("OK " if s.startswith("TAMAM") else "XX ") + m[:58].ljust(58)
              + s[:55].encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
