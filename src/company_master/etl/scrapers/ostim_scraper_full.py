# -*- coding: utf-8 -*-
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Iterator
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.ostim.org.tr"
FIRMA_LIST_URL = "{}/firmalar".format(BASE_URL)
USER_AGENT = "AnkaraB2B-Bot/1.0"
REQUEST_TIMEOUT = 30
RATE_LIMIT_SECONDS = 3.0

BIREYSEL_EMAIL_DOMAINS = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "yandex.com", "mynet.com"}

@dataclass
class OstimFirma:
    unvan: str
    telefonler: List[str] = field(default_factory=list)
    emailler: List[str] = field(default_factory=list)
    web_sitesi: Optional[str] = None
    adres: Optional[str] = None
    sosyal_medya: dict = field(default_factory=dict)
    vergi_no: Optional[str] = None
    osb_parsel: Optional[str] = None
    sektor: Optional[str] = None
    slug: Optional[str] = None
    kaynak: str = "ostim.org.tr"
    cekilme_tarihi: str = field(default_factory=lambda: datetime.now().isoformat())

def kvkk_filtrele(telefon: str | None, email: str | None) -> tuple[str | None, str | None]:
    out_email = email
    if email:
        email_lower = email.lower().strip()
        if not email_lower.startswith(("info@", "iletisim@", "contact@", "kurumsal@", "satis@", "destek@")):
            domain = email_lower.split("@", 1)[1] if "@" in email_lower else ""
            if domain in BIREYSEL_EMAIL_DOMAINS:
                out_email = None
    return telefon, out_email

def fetch_robots() -> set[str]:
    try:
        resp = requests.get("{}/robots.txt".format(BASE_URL), headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        dis = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if line.lower().startswith("disallow:"):
                p = line.split(":", 1)[1].strip()
                if p and p != "/":
                    dis.add(p)
        return dis
    except Exception:
        return set()

def fetch_all_firmalar(output_path: Path, page_delay: float = RATE_LIMIT_SECONDS) -> Iterator[OstimFirma]:
    disallowed = fetch_robots()
    print("[ROBOTS] Disallow: {}".format(disallowed))
    if "/firmalar" in disallowed:
        raise PermissionError("/firmalar disallowed")
    sayfa = 1
    toplam = 0
    with open(output_path, "w", encoding="utf-8") as f:
        while True:
            url = "{}?page={}".format(FIRMA_LIST_URL, sayfa) if sayfa > 1 else FIRMA_LIST_URL
            print("[PAGE] {} -> {}".format(sayfa, url))
            try:
                resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
            except requests.RequestException as exc:
                print("[HATA] Sayfa {}: {}".format(sayfa, exc))
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            kartlar = soup.select("div.col-lg-4.mb-3")
            if not kartlar:
                print("[BITIS] Sayfa {}: firma bulunamadi, durduruluyor.".format(sayfa))
                break
            for kart in kartlar:
                unvan = ""
                title_el = kart.select_one("p.listCompanyTitle")
                if title_el:
                    for i in title_el.select("i"):
                        i.decompose()
                    unvan = title_el.get_text(strip=True)
                if not unvan:
                    a_el = kart.select_one("a[title]")
                    if a_el:
                        unvan = a_el.get("title", "").strip()
                if not unvan:
                    continue
                telefonler_raw = []
                phone_el = kart.select_one("p.listCompanyPhone")
                if phone_el:
                    for i in phone_el.select("i"):
                        i.decompose()
                    phone_text = phone_el.get_text(strip=True)
                    for t in phone_text.split(","):
                        t = t.strip()
                        if t:
                            telefonler_raw.append(t)
                emailler_raw = []
                mail_el = kart.select_one("p.listCompanyMail")
                if mail_el:
                    for i in mail_el.select("i"):
                        i.decompose()
                    mail_text = mail_el.get_text(strip=True)
                    for e in mail_text.split(","):
                        e = e.strip()
                        if e:
                            emailler_raw.append(e)
                temiz_emailler = []
                for em in emailler_raw:
                    _, em_out = kvkk_filtrele(None, em)
                    if em_out:
                        temiz_emailler.append(em_out)
                slug = None
                link_el = kart.select_one('a[href*="/firmalar/"]')
                if link_el:
                    href = link_el.get("href", "")
                    slug = href.rstrip("/").split("/")[-1] if href else None
                sektor = None
                firma = OstimFirma(
                    unvan=unvan,
                    telefonler=telefonler_raw,
                    emailler=temiz_emailler,
                    slug=slug,
                    sektor=sektor,
                )
                f.write(json.dumps(asdict(firma), ensure_ascii=False) + "\n")
                toplam += 1
                yield firma
            print("[PAGE {}] {} firma, toplam: {}".format(sayfa, len(kartlar), toplam))
            sayfa += 1
            time.sleep(page_delay)

if __name__ == "__main__":
    out_dir = Path("C:/Projeler/Huginn Data Insights/data/ostim")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "firmalar_full.jsonl"
    print("[BASLAMA] {} -> {}".format(datetime.now().isoformat(), out_file))
    for _ in fetch_all_firmalar(out_file):
        pass
    print("[BITIS] {} -> toplam: {} KB approx".format(datetime.now().isoformat(), out_file.stat().st_size // 100))
