# -*- coding: utf-8 -*-
"""OSB scraper ortak base class."""
from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import requests
from bs4 import BeautifulSoup


@dataclass
class BaseOsfbFirma:
    unvan: str
    telefonlar: list[str] = field(default_factory=list)
    emailler: list[str] = field(default_factory=list)
    web_sitesi: str | None = None
    adres: str | None = None
    sosyal_medya: dict[str, str] = field(default_factory=dict)
    yetkili: dict | None = None
    vergi_no: str | None = None
    vergi_no_kaynagi: str | None = None
    osb_parsel: str | None = None
    osb_parsel_kaynagi: str | None = None
    sektor: str | None = None
    slug: str | None = None
    kaynak: str = ""
    cekilme_tarihi: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class BaseOsfbScraper:
    BASE_URL: str = ""
    FIRMA_LISTE_URL: str = ""
    ROBOTS_URL: str = ""
    USER_AGENT: str = ""
    RATE_LIMIT_SECONDS: float = 2.0
    REQUEST_TIMEOUT: int = 20
    WEB_BLOCKLIST: tuple[str, ...] = ()
    VKN_PATTERN: re.Pattern = re.compile(r"\b(\d{10,11})\b")
    STATE_DIR: Path = Path("data")
    STATE_PATH: Path = STATE_DIR / ".scrape_state.json"
    OUTPUT_PATH: Path = STATE_DIR / "firmalar.jsonl"
    FIRMA_CLASS = BaseOsfbFirma
    log: logging.Logger = logging.getLogger("base_osfb_scraper")

    def _load_state(self) -> dict[str, Any]:
        if not self.STATE_PATH.exists():
            return {"completed_pages": [], "total_records": 0}
        try:
            return json.loads(self.STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"completed_pages": [], "total_records": 0}

    def _save_state(self, state: dict[str, Any]) -> None:
        tmp = self.STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.STATE_PATH)

    def normalize_website(self, v: str | None) -> str | None:
        if not v:
            return None
        s = v.strip()
        if not s:
            return None
        if not s.startswith("http"):
            s = "https://" + s
        low = s.lower()
        if any(b in low for b in self.WEB_BLOCKLIST):
            return None
        return s

    def extract_vkn(self, unvan: str | None) -> str | None:
        if not unvan:
            return None
        m = self.VKN_PATTERN.search(unvan)
        return m.group(1) if m else None

    def fetch_firma_liste(self, page: int = 1) -> list[BaseOsfbFirma]:
        raise NotImplementedError

    def fetch_firma_detay(self, slug: str) -> dict[str, Any]:
        return {}

    # --- Güvenli sayfalama şablonu (D-235 / VERI-KAZIYICI-DONGU-01) -------------
    # Kök neden: WordPress tabanlı OSB siteleri geçersiz ?page/N/ için sayfa 1'i
    # döndürür. "liste boşalınca dur" koşulu asla gerçekleşmez -> sonsuz döngü.
    # İvedik'te ölçüldü: 15 firma x 224 tekrar = 3375 hayalet kayıt (%99.6 kopya).
    MAX_SAYFA: int = 500          # sert tavan: hiçbir OSB 500 sayfa değil
    TEKRAR_TOLERANSI: int = 2     # ardışık kaç yinelenen sayfadan sonra dur

    def sayfa_dongusu(self) -> Iterator[tuple[int, list[BaseOsfbFirma]]]:
        """Sayfaları getirir; tekrar/boş/tavan görünce durur. Tekil ünvan yayar."""
        gorulen_sayfa: set[str] = set()
        gorulen_unvan: set[str] = set()
        tekrar = 0
        for sayfa in range(1, self.MAX_SAYFA + 1):
            firmalar = self.fetch_firma_liste(sayfa)
            if not firmalar:
                self.log.info("Sayfa %d boş — bitti", sayfa)
                return
            imza = "|".join(f.unvan for f in firmalar)
            if imza in gorulen_sayfa:
                tekrar += 1
                self.log.warning("Sayfa %d önceki bir sayfanın kopyası (%d/%d)",
                                 sayfa, tekrar, self.TEKRAR_TOLERANSI)
                if tekrar >= self.TEKRAR_TOLERANSI:
                    self.log.error("Sayfalama döngüsü — sayfa %d'de durduruldu", sayfa)
                    return
                continue
            gorulen_sayfa.add(imza)
            tekrar = 0
            yeni = [f for f in firmalar if f.unvan not in gorulen_unvan]
            gorulen_unvan.update(f.unvan for f in yeni)
            if not yeni:
                self.log.warning("Sayfa %d: tüm ünvanlar zaten görüldü — bitti", sayfa)
                return
            yield sayfa, yeni
            time.sleep(self.RATE_LIMIT_SECONDS)
        self.log.error("MAX_SAYFA (%d) aşıldı — durduruldu", self.MAX_SAYFA)

    def scrape(self, detay_al: bool = False) -> Iterator[BaseOsfbFirma]:
        raise NotImplementedError
