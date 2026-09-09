"""OSTIM OSB uye listesi scraper.

Detay sayfasi parse (2026-09-02):
- Sag kolon / aside icindeki bilgi kutulari (label + deger)
- Adres, Web, Vergi No, Parsel alanlari icin fallback zinciri
- vergi_no bulunamazsa unvan icinden 10-11 haneli regex
- osb_parsel bulunamazsa adres icinde PARSEL/ADA anahtar kelimesi aranir

Resume (2026-09-03):
- State file: data/ostim/.scrape_state.json
- Sektor/sayfa seviyesinde kayit. Yeniden baslatma tamamlanan sektorleri atlar.
"""

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
from bs4 import BeautifulSoup, Tag

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "ostim_detay_scrape.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("ostim_scraper")

VKN_PATTERN = re.compile(r"\b(\d{10,11})\b")
PARSEL_PATTERN = re.compile(r"\b(PARSEL|ADA)\b", re.IGNORECASE)
WEB_BLOCKLIST = (
    "ostim.org.tr", "ostimonline.com", "ostimradyo.com", "osp.com.tr", "isim.org.tr",
    "facebook.com", "twitter.com", "x.com",
    "linkedin.com", "instagram.com", "youtube.com",
)
DETAY_LABEL_MAP = {
    "adres": ("adres", "adresi", "address"),
    "vergi_no": ("vergi no", "vergi numarasi", "tax no", "tax number", "vkn"),
    "osb_parsel": ("ada / parsel", "ada/parsel", "ada", "parsel", "parsel no"),
    "telefon": ("telefon", "phone", "tel"),
    "email": ("e-posta", "eposta", "email", "mail"),
    "web_sitesi": ("web sitesi", "web", "website"),
}

BASE_URL = "https://www.ostim.org.tr"
FIRMA_LIST_URL = f"{BASE_URL}/firmalar"
SEKTOR_LIST_URL = f"{BASE_URL}/sektorler"
ROBOTS_URL = f"{BASE_URL}/robots.txt"

USER_AGENT = "AnkaraB2B-Bot/1.0 (research@example.com)"
RATE_LIMIT_SECONDS = 3.0
REQUEST_TIMEOUT = 15

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
BIREYSEL_EMAIL_DOMAINS = {
    "gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "yandex.com", "mynet.com",
}

STATE_DIR = Path("data/ostim")
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATH = STATE_DIR / ".scrape_state.json"


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"completed_sectors": {}, "total_records": 0}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"completed_sectors": {}, "total_records": 0}


def _save_state(state: dict[str, Any]) -> None:
    tmp_path = STATE_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, STATE_PATH)


def _get_sector_last_page(state: dict[str, Any], sector_slug: str) -> int:
    return state.get("completed_sectors", {}).get(sector_slug, 0)


def _mark_page_done(state: dict[str, Any], sector_slug: str, page: int) -> None:
    if "completed_sectors" not in state:
        state["completed_sectors"] = {}
    state["completed_sectors"][sector_slug] = page


def _mark_sector_done(state: dict[str, Any], sector_slug: str, last_page: int) -> None:
    _mark_page_done(state, sector_slug, last_page)


def _increment_total(state: dict[str, Any], count: int) -> None:
    state["total_records"] = state.get("total_records", 0) + count


@dataclass
class OstimFirma:
    unvan: str
    telefonler: list[str] = field(default_factory=list)
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
    kaynak: str = "ostim.org.tr"
    cekilme_tarihi: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def fetch_robots() -> set[str]:
    try:
        resp = requests.get(
            ROBOTS_URL, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        disallowed: set[str] = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path and path != "/":
                    disallowed.add(path)
        return disallowed
    except requests.RequestException as exc:
        log.warning("robots.txt cekilemedi: %s; scraping riski kullaniciya aittir.", exc)
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
    resp = requests.get(
        SEKTOR_LIST_URL, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    sektorler: list[dict[str, str]] = []
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


def fetch_firmalar(liste_url: str, sayfa: int = 1) -> list["OstimFirma"]:
    url = f"{liste_url}?page={sayfa}" if sayfa > 1 else liste_url
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    firmalar: list["OstimFirma"] = []

    for card in soup.select("a[href^='/firmalar/']"):
        href = card.get("href", "")
        slug = href.rstrip("/").split("/")[-1] if href else None
        if not slug or slug == "firmalar":
            continue

        unvan = ""
        title_el = card.select_one("p.listCompanyTitle")
        if title_el:
            for i_tag in title_el.select("i"):
                i_tag.decompose()
            unvan = title_el.get_text(strip=True)
        if not unvan:
            continue

        telefonler_raw: list[str] = []
        phone_el = card.select_one("p.listCompanyPhone")
        if phone_el:
            for i_tag in phone_el.select("i"):
                i_tag.decompose()
            phone_text = phone_el.get_text(strip=True)
            for t in phone_text.split(","):
                t = t.strip()
                if t:
                    telefonler_raw.append(t)

        emailler_raw: list[str] = []
        mail_el = card.select_one("p.listCompanyMail")
        if mail_el:
            for i_tag in mail_el.select("i"):
                i_tag.decompose()
            mail_text = mail_el.get_text(strip=True)
            for e in mail_text.split(","):
                e = e.strip()
                if e:
                    emailler_raw.append(e)

        temiz_emailler: list[str] = []
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


def _label_match(text: str, labels: tuple[str, ...]) -> bool:
    t = text.lower().strip(" :")
    return any(t == lab or t.startswith(lab + ":") or t.startswith(lab + " ") for lab in labels)


def _extract_value_after(node: Tag, max_skip: int = 5) -> str | None:
    cur = node
    for _ in range(max_skip):
        nxt = cur.find_next_sibling()
        if nxt is None:
            return None
        text = nxt.get_text(" ", strip=True)
        if text:
            return text
        cur = nxt
    return None


def _find_detail_block(soup: BeautifulSoup, field_key: str) -> str | None:
    labels = DETAY_LABEL_MAP[field_key]
    for el in soup.find_all(string=True):
        if not isinstance(el, str):
            continue
        if _label_match(el.strip(), labels):
            parent = el.parent
            if not isinstance(parent, Tag):
                continue
            value = _extract_value_after(parent)
            if value and len(value) >= 2:
                cleaned = re.sub(r"\s+", " ", value).strip(" :")
                return cleaned
    for el in soup.find_all(string=True):
        if not isinstance(el, str):
            continue
        if _label_match(el.strip(), labels):
            root = el.parent
            if not isinstance(root, Tag):
                continue
            for tag in root.find_all(["a", "span", "div", "p"], recursive=False):
                text = tag.get_text(" ", strip=True)
                if text and len(text) >= 2:
                    cleaned = re.sub(r"\s+", " ", text).strip(" :")
                    return cleaned
    return None


def _extract_web_sitesi(soup: BeautifulSoup) -> str | None:
    seen: set[str] = set()
    for a in soup.select("a[href^='http']"):
        href = a.get("href", "")
        if not href.startswith("http"):
            continue
        if href in seen:
            continue
        seen.add(href)
        if any(b in href for b in WEB_BLOCKLIST):
            continue
        low = href.lower()
        if "ostim" in low:
            continue
        return href
    return None


def _extract_sosyal_medya(soup: BeautifulSoup) -> dict[str, str]:
    sosyal: dict[str, str] = {}
    for a in soup.select(
        "a[href*='linkedin.com'], a[href*='twitter.com'], a[href*='x.com'],"
        " a[href*='facebook.com'], a[href*='instagram.com']"
    ):
        href = a.get("href", "")
        if "linkedin.com" in href:
            sosyal["linkedin"] = href
        elif "twitter.com" in href or "x.com" in href:
            sosyal["twitter"] = href
        elif "facebook.com" in href:
            sosyal["facebook"] = href
        elif "instagram.com" in href:
            sosyal["instagram"] = href
    return sosyal


def _vergi_no_fallback(unvan: str) -> tuple[str | None, str | None]:
    if not unvan:
        return None, None
    m = VKN_PATTERN.search(unvan)
    if m:
        return m.group(1), "unvan_regex"
    return None, None


def _parsel_fallback(adres: str | None) -> tuple[str | None, str | None]:
    if not adres:
        return None, None
    if PARSEL_PATTERN.search(adres):
        return adres.strip(), "adres_icinde"
    return None, None


def fetch_firma_detay(slug: str) -> dict:
    url = f"{BASE_URL}/firmalar/{slug}"
    try:
        resp = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error("Detay sayfasi %s: %s", slug, exc)
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    data: dict = {
        "web_sitesi": None,
        "adres": None,
        "sosyal_medya": {},
        "vergi_no": None,
        "vergi_no_kaynagi": None,
        "osb_parsel": None,
        "osb_parsel_kaynagi": None,
        "yetkili": None,
    }

    data["web_sitesi"] = _extract_web_sitesi(soup)
    data["sosyal_medya"] = _extract_sosyal_medya(soup)
    data["adres"] = _find_detail_block(soup, "adres")
    vergi_val = _find_detail_block(soup, "vergi_no")
    if vergi_val:
        data["vergi_no"] = vergi_val
        data["vergi_no_kaynagi"] = "detay_sayfa"

    parsel_val = _find_detail_block(soup, "osb_parsel")
    if parsel_val:
        data["osb_parsel"] = parsel_val
        data["osb_parsel_kaynagi"] = "detay_sayfa"
    else:
        parsel_val, kaynak = _parsel_fallback(data.get("adres"))
        if parsel_val:
            data["osb_parsel"] = parsel_val
            data["osb_parsel_kaynagi"] = kaynak

    return data


def scrape_firma_full(liste_url: str, sayfa: int = 1, detay_al: bool = False) -> Iterator[OstimFirma]:
    firmalar = fetch_firmalar(liste_url, sayfa)
    for idx, firma in enumerate(firmalar):
        if detay_al and firma.slug:
            time.sleep(RATE_LIMIT_SECONDS)
            detay = fetch_firma_detay(firma.slug)
            firma.web_sitesi = detay.get("web_sitesi")
            firma.adres = detay.get("adres")
            firma.sosyal_medya = detay.get("sosyal_medya", {}) or {}
            firma.vergi_no = detay.get("vergi_no")
            firma.vergi_no_kaynagi = detay.get("vergi_no_kaynagi")
            firma.osb_parsel = detay.get("osb_parsel")
            firma.osb_parsel_kaynagi = detay.get("osb_parsel_kaynagi")
            if not firma.vergi_no:
                vkn, kaynak = _vergi_no_fallback(firma.unvan)
                if vkn:
                    firma.vergi_no = vkn
                    firma.vergi_no_kaynagi = kaynak
        if (idx + 1) % 10 == 0:
            log.info("  + Sayfa %d: firma %d/%d islendi", sayfa, idx + 1, len(firmalar))
        yield firma


def scrape_tum_osb(output_path: Path, detay_al: bool = False) -> Iterator[OstimFirma]:
    log.info("BASLA %s - OSTIM scraping (detayli=%s)", datetime.now().isoformat(), detay_al)
    log.info("KONTROL robots.txt: %s", ROBOTS_URL)

    disallowed = fetch_robots()
    log.info("BILGI Disallow listesinde %d path var: %s",
             len(disallowed), sorted(disallowed)[:5])

    if not is_path_allowed("/firmalar", disallowed):
        log.error("DUR /firmalar disallow edilmis. Durduruluyor.")
        return

    sektorler = fetch_sektor_listesi()
    log.info("BILGI %d sektor bulundu", len(sektorler))

    state = _load_state()
    resume_info = {
        sektor["slug"]: {
            "ad": sektor["ad"],
            "url": sektor["url"],
        }
        for sektor in sektorler
    }
    toplam = state.get("total_records", 0)
    file_mode = "a" if output_path.exists() else "w"
    log.info("Cikti dosyasi modu: %s", file_mode)
    log.info("Resume state: %d sektor tamamlandi", len(state.get("completed_sectors", {})))
    with open(output_path, file_mode, encoding="utf-8") as f:
        for sektor in sektorler:
            slug = sektor["slug"]
            last_page = _get_sector_last_page(state, slug)
            if last_page > 0:
                log.info("SEKTOR %s (%s) - devam ediliyor, son sayfa: %d", sektor["ad"], sektor["url"], last_page)
            else:
                log.info("SEKTOR %s (%s)", sektor["ad"], sektor["url"])
            sayfa = last_page + 1
            while True:
                try:
                    firmalar_list = list(scrape_firma_full(sektor["url"], sayfa, detay_al=detay_al))
                except requests.RequestException as exc:
                    log.error("HATA %s sayfa %d: %s", sektor["ad"], sayfa, exc)
                    break
                if not firmalar_list:
                    _mark_sector_done(state, slug, sayfa - 1)
                    _save_state(state)
                    log.info("  SEKTOR BITTI %s (bos sayfa %d)", sektor["ad"], sayfa)
                    break
                for firma in firmalar_list:
                    firma.sektor = sektor["ad"]
                    f.write(firma.to_jsonl() + "\n")
                    toplam += 1
                    yield firma
                _increment_total(state, len(firmalar_list))
                _mark_page_done(state, slug, sayfa)
                _save_state(state)
                log.info("  + %s sayfa %d: %d firma (toplam: %d)", sektor["ad"], sayfa, len(firmalar_list), toplam)
                sayfa += 1
                time.sleep(RATE_LIMIT_SECONDS)
    state["total_records"] = toplam
    _save_state(state)
    log.info("BITIS %s - %d firma yazildi: %s",
             datetime.now().isoformat(), toplam, output_path)


if __name__ == "__main__":
    import sys
    detayli = "--detayli" in sys.argv
    if detayli:
        sys.argv.remove("--detayli")
    output = (
        Path(sys.argv[1]) if len(sys.argv) > 1
        else Path("data/ostim/firmalar_detayli.jsonl" if detayli else "data/ostim_firmalar.jsonl")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    for _ in scrape_tum_osb(output, detay_al=detayli):
        pass