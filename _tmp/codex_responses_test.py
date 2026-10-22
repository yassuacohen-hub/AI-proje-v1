# -*- coding: utf-8 -*-
"""CODEX WIRE TEST: tüm adaylar /responses ucundan (Codex gerçekte bunu kullanır)."""
import json
import time
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
EVRN = "evren_llm_BZ2d6Zxirtse1n5ehKgLDp_3h4LVnSXCJBc3BYWD70M"

ADAYLAR = [
    # (etiket, base, key, model)
    ("9r_nemotron_ultra", "http://localhost:20128/v1", KEY9,
     "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free"),
    ("9r_nemotron_light", "http://localhost:20128/v1", KEY9,
     "kc/nvidia/nemotron-3.5-lightning:free"),
    ("9r_nemotron_nano_r", "http://localhost:20128/v1", KEY9,
     "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ("9r_or_free", "http://localhost:20128/v1", KEY9, "kc/openrouter/free"),
    ("9r_laguna_s", "http://localhost:20128/v1", KEY9,
     "openrouter/poolside/laguna-s-2.1:free"),
    ("9r_north_code", "http://localhost:20128/v1", KEY9,
     "kc/cohere/north-mini-code:free"),
    ("9r_dots_note", "http://localhost:20128/v1", KEY9,
     "kc/dots-studio/dots-3-note-preview:free"),
    ("9r_minimax", "http://localhost:20128/v1", KEY9,
     "cl/minimax/minimax-m3.1-flash:free"),
    ("9r_bzl_auto", "http://localhost:20128/v1", KEY9, "bzl/auto:free"),
    ("ev_deepseek", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "deepseek-v4.1-flash"),
    ("ev_glm", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "glm-5.3"),
    ("ev_qwen_flash", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "qwen3.8-flash-next"),
    ("ev_gemma", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "gemma-4-31b"),
    ("ev_mimo", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "mimo-v2.6-pro"),
    ("ev_qwen_vl", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "qwen3-vl-30b"),
    ("ev_auto", "https://evren-llmapi.ssyz.org.tr/v1", EVRN, "auto"),
]


def responses_test(base, key, model):
    body = {"model": model, "input": "Reply with exactly: PONG", "stream": False}
    req = urllib.request.Request(
        base + "/responses", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        sure = round(time.time() - t, 1)
        durum = j.get("status", "?")
        parcalar = []
        for it in j.get("output", []) or []:
            if it.get("type") == "message":
                for c in it.get("content", []) or []:
                    parcalar.append(c.get("text") or c.get("value") or "")
        metin = " ".join(parcalar).strip()
        if durum == "completed" and metin:
            return "OK", metin[:30], sure
        return durum or "BOS", metin[:30] or json.dumps(j)[:80], sure
    except Exception as e:  # noqa: BLE001
        govde = ""
        if hasattr(e, "read"):
            try:
                govde = e.read().decode("utf-8", "replace")[:70]
            except Exception:  # noqa: BLE001
                pass
        return "HATA", (str(e)[:60] + " " + govde[:50]), round(time.time() - t, 1)


def main():
    sonuc = {}
    for etiket, base, key, model in ADAYLAR:
        sinif, detay, sure = responses_test(base, key, model)
        sonuc[etiket] = {"model": model, "sinif": sinif, "sure_sn": sure,
                         "detay": detay}
        print((sinif.ljust(10) + etiket.ljust(20) + f"{sure:6.1f}s ").encode(
            "ascii", "replace").decode() + detay[:40].encode("ascii", "replace").decode())
    with open("_tmp/codex_responses_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    ok = sum(1 for v in sonuc.values() if v["sinif"] == "OK")
    print(f"== OK {ok}/{len(ADAYLAR)} ==")


if __name__ == "__main__":
    main()
