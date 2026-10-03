# -*- coding: utf-8 -*-
"""ajan-chat.jsonl'den tek görevin kayıtlarını KESİLMEDEN yazdırır.

Kullanım: python scripts/chat_satir_oku.py <task_id>
Neden: `ajan_chat.py oku` 200 karakterde kesiyor; karar metinleri kesilince
orkestratör yarım bilgiyle onay/ret veriyor (D-260).
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DOSYA = Path(__file__).resolve().parents[1] / "data" / "orchestrator" / "ajan-chat.jsonl"


def main() -> int:
    if len(sys.argv) < 2:
        print("kullanim: chat_satir_oku.py <task_id>")
        return 2
    hedef = sys.argv[1]
    n = 0
    for i, satir in enumerate(DOSYA.read_text(encoding="utf-8").splitlines()):
        if not satir.strip():
            continue
        k = json.loads(satir)
        if k.get("task_id") != hedef:
            continue
        n += 1
        print(f"--- satir {i + 1} | {k.get('timestamp')} | {k.get('kimden')} -> {k.get('ajan')} | {k.get('durum')} | {k.get('onem', '')}")
        print("SORUN:", k.get("sorun", ""))
        print("COZUM:", k.get("cozum", ""))
    print(f"toplam {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
