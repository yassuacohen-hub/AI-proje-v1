# -*- coding: utf-8 -*-
"""Notion gorev panosu aynasi - TEK YONLU (okur, yazmaz).

NEDEN AYRI DOSYA (D-86): Notion cagrilari `python -c` ile yapilamaz;
PowerShell `{}` ve `{}` karakterlerini yutuyor, komut sessizce bozuluyor.
Bu script tek yerde kalici, her kurulumda ayni mantik.

NEDEN TEK YONLU (D-260): Kaynak daima data/orchestrator/task_board.json.
Notion bir AYNA yuzeydir. Oradan panoya yazilirsa iki kaynak dogar ve
"pano plan, teslim alinmis" tutarsizligi (D-260 kanitsiz durum beyani) buyur.

Kullanim:
    python scripts/notion_pano.py kur      # panoyu olusturur (bir kez)
    python scripts/notion_pano.py kontrol  # sadece baglanti/erişim testi
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

KOK = pathlib.Path(__file__).resolve().parents[1]
ENV = KOK / ".env"
PANO = KOK / "data" / "orchestrator" / "task_board.json"

API = "https://api.notion.com/v1"
SURUM = "2022-06-28"
BEKLEME = 0.4  # Notion ~3 istek/sn; guvenli taraf

# --- Turkce etiketler -------------------------------------------------------
ONCELIK_SIRA = ["P0", "P1", "P2", "P3"]
ONCELIK_AD = {"P0": "KIRMIZI - en onemli", "P1": "TURUNCU - onemli",
              "P2": "SARI - orta", "P3": "GRI - sonra"}
DURUM_AD = {"plan": "YAPILACAK", "aktif": "SU ANDA YAPILIYOR",
            "review": "ONAY BEKLIYOR", "tamamlandi": "BITTI"}
AJAN_AD = {"yasu": "yasu", "utku": "utku", "ihsan": "ihsan", "salih": "salih"}


def api_key() -> str:
    """NOTION_API_KEY degerini .env icinden okur (sir, ekrana basilmaz)."""
    for satir in ENV.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if satir.startswith("NOTION_API_KEY="):
            deger = satir.split("=", 1)[1].strip()
            if deger:
                return deger
    raise SystemExit("HATA: .env icinde NOTION_API_KEY yok")


def istek(yol: str, govde: dict | None = None, yontem: str | None = None) -> dict:
    """Notion cagrisi. Varsayilan POST; blok eklemek icin yontem='PATCH'.

    D-86 notu: blok ekleme PATCH ister. POST '/blocks/{id}/children'
    'invalid_request_url' doner ve sessizce gecersiz sayfa birakir.
    """
    veri = json.dumps(govde).encode() if govde is not None else None
    basliklar = {"Authorization": "Bearer " + api_key(), "Notion-Version": SURUM}
    if veri is not None:
        basliklar["Content-Type"] = "application/json"
    if yontem is None:
        yontem = "POST" if veri is not None else "GET"
    req = urllib.request.Request(API + yol, data=veri, headers=basliklar, method=yontem)
    time.sleep(BEKLEME)
    try:
        with urllib.request.urlopen(req, timeout=30) as yanit:
            return json.loads(yanit.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        hata = exc.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"HATA: Notion {exc.code} - {yol}\n{hata}") from exc




from notion_aciklama import ACIKLAMA  # noqa: E402


def pano_gorevleri() -> list[dict]:
    """Panodaki AKTIF gorevleri dondurur.

    D-260: pano dosyasi tum gecmisi tutar (124 kayit: 87 done, 15 arsiv...).
    Notion panosu yalnizca yapilacak isleri gostermeli; aksi halde bitmis
    isler panoya geri doner. BITEN IS SILINMEZ, arsivde kalir.
    """
    veri = json.loads(PANO.read_text(encoding="utf-8"))
    ts = veri if isinstance(veri, list) else veri.get("tasks", [])
    return [t for t in ts if t.get("durum") in ("plan", "aktif", "review")]


def ben() -> dict:
    """Botun hangi workspace'e bagli oldugunu dondurur."""
    return istek("/users/me")


def ara(sayfa: int = 100) -> list[dict]:
    """Botun erisebildigi tum sayfa/veritabanlarini listeler."""
    return istek("/search", {"page_size": sayfa}).get("results", [])


def baslik(obje: dict) -> str:
    if obje.get("object") == "database":
        return "".join(x.get("plain_text", "") for x in obje.get("title", []))
    for prop in obje.get("properties", {}).values():
        if prop.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in prop.get("title", []))
    return ""


DUZ_BASLIK = {
    "SCRAPE-002-LEMMLESS-ANKARA-OSB": "Ankara sanayi sitelerinden şirket topla",
    "SCRAPE-001-DOCKER-SETUP": "Veritabanını tek komutla kur",
    "SCRAPE-005-KAZIMA-DOCKER-INTEGRATION": "Kazımayı otomatik çalışan servise çevir",
    "SCRAPE-003-9ROUTER-JINA-FALLBACK": "Okunamayan sayfaları yedek yöntemle oku",
    "SCRAPE-004-QWEN-SINIFLANDIRMA": "Okunamayan veriyi sınıflandır",
    "SCRAPE-006-QUALITY-AUDIT": "Verinin eksik olup olmadığını ölç",
    "SCRAPE-007-FINAL-REPORT": "Kazıma döneminin son raporunu yaz",
    "VERI-TENDER-KOLON-01": "İhale sütunlarını yeni sisteme uyarla",
    "VERI-RISK-MOTORU-01": "Firma risk puanını hesapla",
    "VERI-SKOR-MOTORU-01": "Firma uygunluk puanını hesapla",
    "DOC-GLOBAL-INTEL-ARASTIRMA-01": "6. faz kaynaklarını araştır",
    "VERI-OSB-TEMIZLIK-01": "Firma etiketlerini düzelt (cop kayıt yok)",
    "ALTYAPI-RAG-EMBEDDER-01": "Sahte aramayı gerçek anlam aramasıyla değiştir",
    "VERI-ENTITY-GRAPH-01": "Firma-kisi bağlantı semasını yaz",
    "DOC-VENDOR-DD-ARASTIRMA-01": "Tedarikçi adaylarını araştır",
    "ALTYAPI-ODIN-UYARLAMA-01": "Odin güvenlik listesini hazırla",
    "ALTYAPI-AJAN-CAKISMA-01": "Ajan çakışma kilidini yaz",
    "TEST-ODIN-PROMPT-INJECTION": "Odin'i kandırma testini yap",
    "ALTYAPI-MIMIR-BAGLAM-01": "Mimir bağlam (context) ucunu yaz",
}


def aciklama_getir(gorev_id: str) -> dict:
    """Gorev id -> pano icin duz Turkce metinler dondurur.

    Listede yoksa aciklamasiz gosterir; UYDURMA YAPMAZ (D-260).
    """
    a = ACIKLAMA.get(gorev_id)
    bas = DUZ_BASLIK.get(gorev_id, gorev_id)
    if not a:
        return {"baslik": bas, "yapti": "(aciklama henuz yazilmadi)",
                "etki": "(bilinmiyor)", "bagli": "(bilinmiyor)", "kanit": "(yok)"}
    return {"baslik": bas, "yapti": a["yapti"], "etki": a["etki"],
            "bagli": a["bagli"], "kanit": a["kanit"]}


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "kur":
        import notion_kur
        notion_kur.kur()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "senkron":
        import notion_senkron
        notion_senkron.senkron(bilesik_test="--bilesik" in sys.argv)
        return
    print("Baglanti:", ben()["name"])
    print("Erisilebilir obje sayisi:", len(ara()))
    gorevler = pano_gorevleri()
    print(f"Aktif gorev: {len(gorevler)}")
    eksik = [g.get("task_id") for g in gorevler
             if (g.get("task_id") or g.get("id")) not in ACIKLAMA]
    print("Aciklamasi olmayan gorev:", eksik or "yok")


if __name__ == "__main__":
    main()
