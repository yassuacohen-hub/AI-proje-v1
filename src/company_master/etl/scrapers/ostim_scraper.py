"""OSTİM OSB üye listesi scraper.

Web Kazıma Uzmanı masa başı analizine göre:
- Hedef: https://www.ostim.org.tr/firmalar
- Sektör sayfaları: https://www.ostim.org.tr/sektorler/{sektor-slug}
- robots.txt: /firmalar disallow edilmemiş (taranabilir)
- 17 sektör, 6.500+ işletme, 65.000 çalışan
- Sayfa başına ~30 firma, ~200+ sayfa toplam

Yasal/etik:
- Rate limit: 1 istek / 3 saniye
- User-Agent: AnkaraB2B-Bot/1.0 (research@example.com)
- Yalnızca kurumsal iletişim (info@, sabit telefon)
- Tüm telefonlar alınır (GSM dahil) — Karar 6 (2026-09-01)
- robots.txt kontrolü her oturum başında

Karar referansı: V10/10_ankara_osb_sentez Karar 4 + Karar 6
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.ostim.org.tr"
FIRMA_LIST_URL = f"{BASE_URL}/firmalar"
SEKTOR_LIST_URL = f"{BASE_URL}/sektorler"
ROBOTS_URL = f"{BASE_URL}/robots.txt"

USER_AGENT = "AnkaraB2B-Bot/1.0 (research@example.com)"
RATE_LIMIT_SECONDS = 3.0
REQUEST_TIMEOUT = 30

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
BIREYSEL_EMAIL_DOMAINS = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "yandex.com", "mynet.com"}


@dataclass
class OstimFirma:
    """Tek bir OSTİM firmasının normalized kaydı (iletişim-yoğunluklu)."""
    unvan: str
    telefonler: list[str] = field(default_factory=list)
    emailler: list[str] = field(default_factory=list)
    web_sitesi: str | None = None
    adres: str | None = None
    sosyal_medya: dict[str, str] = field(default_factory=dict)
    yetkili: dict | None = None
    vergi_no: str | None = None
    osb_parsel: str | None = None
    sektor: str | None = None
    slug: str | None = None
    kaynak: str = "ostim.org.tr"
    cekilme_tarihi: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def fetch_robots() -> set[str]:
    try:
        resp = requests.get(ROBOTS_URL, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        disallowed = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path and path != "/":
                    disallowed.add(path)
        return disallowed
    except requests.RequestException as exc:
        print(f"[UYARI] robots.txt çekilemedi: {exc}; scraping riski kullanıcıya aittir.")
        return set()


def is_path_allowed(path: str, disallowed: set[str]) -> bool:
    for d in disallowed:
        if path.startswith(d):
            return False
    return True


def kvkk_filtrele(telefon, email):
    out_email = email
    if email:
        email_lower = email.lower().strip()
        if not EMAIL_PATTERN.match(email_lower):
            out_email = None
        else:
            domain = email_lower.split("@", 1)[1] if "@" in email_lower else ""
            if domain in BIREYSEL_EMAIL_DOMAINS:
                out_email = None
    return telefon, out_email


def fetch_sektor_listesi() -> list[dict[str, str]]:
    resp = requests.get(SEKTOR_LIST_URL, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    sektorler = []
    for link in soup.select("a[href*='/sektorler/']"):
        ad = link.get_text(strip=True)
        href = link.get("href", "")
        slug = href.rstrip("/").split("/")[-1]
        if ad and slug and slug != "sektorler":
            sektorler.append({
                "ad": ad,
                "slug": slug,
                "url": f"{BASE_URL}{href}" if href.startswith("/") else href,
            })
    return sektorler


def fetch_firmalar(sektor_url: str, sayfa: int = 1) -> list[OstimFirma]:
    """Bir sektörün belirli bir sayfasındaki firmaları parse eder.

    OSTİM gerçek HTML yapısı (pilot test 2026-09-01):
    - Kart: <div class="col-lg-4 mb-3">
    - Ünvan: <p class="listCompanyTitle"> veya <a title="">
    - Telefon: <p class="listCompanyPhone"> (i tag icon)
    - Email: <p class="listCompanyMail"> (i tag icon)
    - Link: <a href="/firmalar/{slug}">
    """
    url = f"{sektor_url}?page={sayfa}" if sayfa > 1 else sektor_url
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    firmalar = []
    for card in soup.select("div.col-lg-4.mb-3"):
        link_el = card.select_one("a[href^='/firmalar/']")
        if not link_el:
            continue
        href = link_el.get("href", "")
        slug = href.rstrip("/").split("/")[-1] if href else None
        if not slug or slug == "firmalar":
            continue
        unvan = ""
        title_attr = link_el.get("title", "").strip()
        title_el = card.select_one("p.listCompanyTitle")
        if title_attr:
            unvan = title_attr
        elif title_el:
            for i_tag in title_el.select("i"):
                i_tag.decompose()
            unvan = title_el.get_text(strip=True)
        if not unvan:
            continue
        telefonler_raw = []
        phone_el = card.select_one("p.listCompanyPhone")
        if phone_el:
            for i_tag in phone_el.select("i"):
                i_tag.decompose()
            phone_text = phone_el.get_text(strip=True)
            for t in phone_text.split(","):
                t = t.strip()
                if t:
                    telefonler_raw.append(t)
        emailler_raw = []
        mail_el = card.select_one("p.listCompanyMail")
        if mail_el:
            for i_tag in mail_el.select("i"):
                i_tag.decompose()
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
        firmalar.append(OstimFirma(
            unvan=unvan,
            telefonler=telefonler_raw,
            emailler=temiz_emailler,
            slug=slug,
            web_sitesi=None,
            adres=None,
            sosyal_medya={},
        ))
    return firmalar


def fetch_firma_detay(slug: str) -> dict:
    """Bir firmanın detay sayfasından ek bilgi çeker."""
    url = f"{BASE_URL}/firmalar/{slug}"
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[HATA] Detay sayfası {slug}: {exc}")
        return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    data = {
        "web_sitesi": None,
        "adres": None,
        "sosyal_medya": {},
        "vergi_no": None,
        "osb_parsel": None,
        "yetkili": None,
    }
    for a in soup.select("a[href^='http']"):
        href = a.get("href", "")
        if "ostim.org.tr" in href:
            continue
        if href.startswith("http"):
            data["web_sitesi"] = href
            break
    for a in soup.select("a[href*='linkedin.com'], a[href*='twitter.com'], a[href*='x.com'], a[href*='facebook.com'], a[href*='instagram.com']"):
        href = a.get("href", "")
        if "linkedin.com" in href:
            data["sosyal_medya"]["linkedin"] = href
        elif "twitter.com" in href or "x.com" in href:
            data["sosyal_medya"]["twitter"] = href
        elif "facebook.com" in href:
            data["sosyal_medya"]["facebook"] = href
        elif "instagram.com" in href:
            data["sosyal_medya"]["instagram"] = href
    for label in ["Adres", "Adresi", "Address"]:
        adres_el = soup.find(string=re.compile(label, re.IGNORECASE))
        if adres_el:
            parent = adres_el.parent
            if parent:
                next_sib = parent.find_next_sibling()
                if next_sib:
                    data["adres"] = next_sib.get_text(strip=True)
                    break
                data["adres"] = parent.get_text(strip=True).replace(label, "").strip()
                break
    for label in ["Vergi No", "Vergi Numarası", "Tax"]:
        vergi_el = soup.find(string=re.compile(label, re.IGNORECASE))
        if vergi_el:
            parent = vergi_el.parent
            if parent:
                next_sib = parent.find_next_sibling()
                if next_sib:
                    data["vergi_no"] = next_sib.get_text(strip=True)
                    break
    for label in ["Ada", "Parsel", "Parsel No"]:
        parsel_el = soup.find(string=re.compile(label, re.IGNORECASE))
        if parsel_el:
            parent = parsel_el.parent
            if parent:
                next_sib = parent.find_next_sibling()
                if next_sib:
                    data["osb_parsel"] = next_sib.get_text(strip=True)
                    break
    return data


def scrape_firma_full(sektor_url: str, sayfa: int = 1, detay_al: bool = False) -> Iterator[OstimFirma]:
    """Liste + (opsiyonel) detay sayfası scrape."""
    firmalar = fetch_firmalar(sektor_url, sayfa)
    for firma in firmalar:
        if detay_al and firma.slug:
            time.sleep(RATE_LIMIT_SECONDS)
            detay = fetch_firma_detay(firma.slug)
            firma.web_sitesi = detay.get("web_sitesi")
            firma.adres = detay.get("adres")
            firma.sosyal_medya = detay.get("sosyal_medya", {})
            firma.vergi_no = detay.get("vergi_no")
            firma.osb_parsel = detay.get("osb_parsel")
        yield firma


def scrape_tum_osb(output_path: Path, detay_al: bool = False) -> Iterator[OstimFirma]:
    """Tüm OSTİM firmalarını scrape eder ve JSONL'e yazar.

    detay_al=True: Her firma için detay sayfası da çekilir (YAVAŞ, 2 kat istek).
    detay_al=False: Sadece liste sayfası.
    """
    print(f"[BAŞLA] {datetime.now().isoformat()} — OSTİM scraping")
    print(f"[KONTROL] robots.txt: {ROBOTS_URL}")
    disallowed = fetch_robots()
    print(f"[BİLGİ] Disallow listesinde {len(disallowed)} path var: {sorted(disallowed)[:5]}")
    if not is_path_allowed("/firmalar", disallowed):
        print("[DUR] /firmalar disallow edilmiş. Durduruluyor.")
        return
    sektorler = fetch_sektor_listesi()
    print(f"[BİLGİ] {len(sektorler)} sektör bulundu")
    toplam = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for sektor in sektorler:
            print(f"[SEKTÖR] {sektor['ad']} ({sektor['url']})")
            sayfa = 1
            while True:
                try:
                    firmalar_list = list(scrape_firma_full(sektor["url"], sayfa, detay_al=detay_al))
                except requests.RequestException as exc:
                    print(f"[HATA] {sektor['ad']} sayfa {sayfa}: {exc}")
                    break
                if not firmalar_list:
                    break
                for firma in firmalar_list:
                    firma.sektor = sektor["ad"]
                    f.write(firma.to_jsonl() + "\n")
                    toplam += 1
                    yield firma
                print(f"  [+] {sektor['ad']} sayfa {sayfa}: {len(firmalar_list)} firma")
                sayfa += 1
                time.sleep(RATE_LIMIT_SECONDS)
    print(f"[BİTİŞ] {datetime.now().isoformat()} — {toplam} firma yazıldı: {output_path}")


if __name__ == "__main__":
    import sys
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/ostim_firmalar.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    for _ in scrape_tum_osb(output):
        pass