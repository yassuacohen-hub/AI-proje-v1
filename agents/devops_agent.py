# Production Agent - LLM ile entegre yetenek sistemi
#
# ALTYAPI-SKILL-YAPISI-01 Faz B: bu dosya `import anthropic` ile basliyordu;
# paket kurulu degil -> ModuleNotFoundError. Proje kurali yeni bagimlilik
# eklemeyi yasaklar. Cozum: mevcut NineRouter istemcisi (9Router) kullanilir;
# `anthropic` SDK hic eklenmedi.
#
# Degisiklik logu:
#   - import anthropic  -> company_master.gateway.ninerouter_client
#   - model koda gomuluydu -> ortam degiskeninden okunur (NINEROUTER_MODEL)
#   - skills.common.*    -> skills.tools.* / skills.services.*

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))
if str(_KOK) not in sys.path:
    sys.path.insert(0, str(_KOK))

from company_master.gateway.ninerouter_client import (  # noqa: E402
    NineRouter,
    NineRouterError,
)

from skills.base import registry  # noqa: E402
import skills.services.ninerouter  # noqa: E402,F401  (registry yuklemesi icin sart)
import skills.tools.file_ops  # noqa: E402,F401
import skills.tools.llm_helper  # noqa: E402,F401
import skills.tools.devops  # noqa: E402,F401
import skills.tools.streamlit  # noqa: E402,F401

#: Model adi koda gomulmez; ortam degiskeni yoksa bu kullanilir.
VARSAYILAN_MODEL = "openai/gpt-5"


class ProductionAgent:
    """Registry'deki yetenekleri LLM'e tool olarak sunan ajan."""

    def __init__(self, model: str | None = None) -> None:
        self.client = NineRouter()
        self.model = (
            model
            or os.environ.get("NINEROUTER_MODEL", "").strip()
            or VARSAYILAN_MODEL
        )

    def tools(self) -> list[dict]:
        """LLM'e gonderilecek tool semalari."""
        return registry.get_all_schemas()

    def run(self, user_prompt: str) -> str:
        """Bir tur calistirir; tool cagrisi varsa sonucu dondurur."""
        available_tools = self.tools()
        print(f"Ajan yetenekleri yukleniyor... ({len(available_tools)} tool)")

        try:
            yanit = self.client.chat(user_prompt, model=self.model)
        except NineRouterError as exc:
            return f"9Router hatasi: {exc}"

        return self._tool_cagri_isle(yanit)

    def _tool_cagri_isle(self, yanit: str) -> str:
        """9Router yanitinda tool cagrisi varsa calistirir."""
        if not yanit:
            return "Bos yanit."
        try:
            yuk = json.loads(yanit)
        except (TypeError, ValueError):
            return yanit

        if not isinstance(yuk, dict):
            return yanit

        for secim in yuk.get("choices") or []:
            if not isinstance(secim, dict):
                continue
            cagrilar = (secim.get("message") or {}).get("tool_calls") or []
            for cagri in cagrilar:
                fn = (cagri or {}).get("function") or {}
                isim = fn.get("name")
                try:
                    girdi = json.loads(fn.get("arguments") or "{}")
                except (TypeError, ValueError):
                    girdi = {}
                print(f"LLM tool cagirdi: {isim} | {girdi}")
                try:
                    sonuc = registry.execute_skill(isim, **girdi)
                except (ValueError, TypeError) as exc:
                    return f"Tool hatasi ({isim}): {exc}"
                return f"Tool sonucu ({isim}): {sonuc}"
        return yanit


# --- CALISTIRMA ORNEGI ---
if __name__ == "__main__":
    ajan = ProductionAgent()
    print(ajan.run(
        "Streamlit uygulamam production sunucusunda surekli kopuyor, "
        "nginx ayarlarini kontrol etmeliyim. domain: mystreamlitapp.com"
    ))
