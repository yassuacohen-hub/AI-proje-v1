# -*- coding: utf-8 -*-
"""ORCH-08 — Orkestratör görev atama komutu.

Kullanım (repo kökünden):
    python scripts/gorev_at.py at --task-id ORCH-09 --baslik "..." --ajan kilo \
        --oncelik P1 --dosya "src/a.py,docs/b.md" --talimat "..."
    python scripts/gorev_at.py pano

`at` görevi panoya ekler (dosyaları kilitler) ve ajana tetik düşürür.
Ajan `scripts/gorev_kutusu.py bak --ajan kilo` ile postasını görür.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

# Windows konsolu cp1254; "→" ve Türkçe karakterler patlamasın.
for _akis in (sys.stdout, sys.stderr):
    if hasattr(_akis, "reconfigure"):
        _akis.reconfigure(encoding="utf-8", errors="replace")

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]


# D-57: [ALAN] FIIL + NESNE -> CIKTI (SURE)
ALANLAR = ("UI", "API", "VERI", "TEST", "DOC", "ALTYAPI", "ORKESTRA")
FIILLER = ("yaz", "düzelt", "taşı", "sil", "denetle", "ölç", "belgele", "araştır")
# D-60: kanonik adlar Turkce; tek dogruluk kaynagi trigger.AJANLAR.
AJANLAR = trigger.AJANLAR
# D-63: Architect gorevini yalnız orkestratör (ihsan) ve üretim (utku) alır.
ARCHITECT_AJANLARI = ("ihsan", "utku")
ARCHITECT_HATIRLATMA = "⚠️ Bu görev Architect modunda açılmalıdır."
_BASLIK = re.compile(
    r"^\[(?P<alan>[A-ZĞÜŞİÖÇ]+)\]\s+(?P<fiil>\S+).*?→.+\((?P<sure>\d+[sd])\)$"
)


def _d57_dogrula(task_id: str, baslik: str, ajan: str) -> str | None:
    """D-57 + D-33 ihlalini metin olarak döner; temizse None."""
    if ajan not in AJANLAR:
        return f"ajan '{ajan}' kanonik degil; izinli: {', '.join(AJANLAR)}"
    m = _BASLIK.match(baslik.strip())
    if not m:
        return (
            "baslik D-57 kalibina uymuyor: [ALAN] FIIL + NESNE -> CIKTI (SURE)\n"
            "  ornek: [UI] Ayarlar sayfasini yaz -> admin_kullanici_ayarlari.py (2s)"
        )
    alan = m.group("alan")
    if alan not in ALANLAR:
        return f"ALAN '{alan}' kanonik degil; izinli: {', '.join(ALANLAR)}"
    # cmd.exe Türkçe karakteri bozabildiği için ASCII karşılıkları da kabul edilir.
    _tr = str.maketrans("ğüşıöçĞÜŞİÖÇ", "gusiocGUSIOC")
    _duz = baslik.translate(_tr).lower()
    if not any(f.translate(_tr).lower() in _duz for f in FIILLER):
        return f"kanonik FIIL yok; izinli: {', '.join(FIILLER)}"
    if not task_id.startswith(alan + "-"):
        return f"task_id on eki ALAN ile ayni olmali: '{alan}-...'"
    return None


# D-58: orkestratör devralma (abrakadabra)
_ANAHTAR_DOSYA = KOK / "data" / "orchestrator" / "abrakadabra.key"
_ORK_DOSYA = KOK / "data" / "orchestrator" / "orchestrator.json"
_VARSAYILAN_ORKESTRATOR = "roo"


def _beklenen_anahtar() -> str | None:
    """ABRAKADABRA_KEY ortam değişkeni, yoksa anahtar dosyası. Hiçbiri yoksa None."""
    env = os.getenv("ABRAKADABRA_KEY", "").strip()
    if env:
        return env
    if _ANAHTAR_DOSYA.exists():
        return _ANAHTAR_DOSYA.read_text(encoding="utf-8").strip() or None
    return None


def _parmak_izi(anahtar: str) -> str:
    """Anahtarın kendisi asla saklanmaz; yalnız sha256 özeti."""
    return hashlib.sha256(anahtar.encode("utf-8")).hexdigest()


def _orkestrator_oku() -> dict:
    if not _ORK_DOSYA.exists():
        return {"ajan": _VARSAYILAN_ORKESTRATOR, "devralma_zamani": None, "anahtar_parmak_izi": None}
    try:
        return json.loads(_ORK_DOSYA.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {"ajan": _VARSAYILAN_ORKESTRATOR, "devralma_zamani": None, "anahtar_parmak_izi": None}


def _orkestrator_yaz(ajan: str, anahtar: str) -> dict:
    kayit = {
        "ajan": ajan,
        "devralma_zamani": datetime.now().isoformat(timespec="seconds"),
        "anahtar_parmak_izi": _parmak_izi(anahtar),
    }
    _ORK_DOSYA.parent.mkdir(parents=True, exist_ok=True)
    _ORK_DOSYA.write_text(json.dumps(kayit, ensure_ascii=False, indent=2), encoding="utf-8")
    return kayit


def _orkestrator_kapisi(cagiran: str | None) -> str | None:
    """Çağıran aktif orkestratör değilse ihlal metni döner; temizse None.

    ponytail: çağıran belirtilmezse kapı geçirgen (geriye uyumluluk).
    Kimliği zorunlu kılmak için `ORKESTRA_AJAN` env'i her ajan kabuğunda sabitlenmeli.
    """
    if not cagiran:
        return None
    aktif = _orkestrator_oku().get("ajan") or _VARSAYILAN_ORKESTRATOR
    if cagiran != aktif:
        return f"gorev atamayi yalniz aktif orkestrator yapar; aktif: '{aktif}', cagiran: '{cagiran}'"
    return None


def cmd_abrakadabra(args: argparse.Namespace) -> int:
    """Doğru anahtarla orkestratörlüğü devralır. Anahtar değeri asla basılmaz."""
    beklenen = _beklenen_anahtar()
    if not beklenen:
        print(
            "HATA: anahtar tanimli degil; ABRAKADABRA_KEY ortam degiskenini ya da "
            f"{_ANAHTAR_DOSYA.relative_to(KOK)} dosyasini olusturun.",
            file=sys.stderr,
        )
        return 1
    if not hmac.compare_digest(args.anahtar, beklenen):
        print("HATA: anahtar dogrulanamadi; devralma yapilmadi.", file=sys.stderr)
        return 1
    if args.ajan not in AJANLAR:
        print(f"HATA: ajan '{args.ajan}' kanonik degil; izinli: {', '.join(AJANLAR)}", file=sys.stderr)
        return 1
    kayit = _orkestrator_yaz(args.ajan, beklenen)
    trigger.tetik_ekle(
        "ORKESTRA-DEVRALMA",
        args.ajan,
        f"Orkestratorluk devralindi ({kayit['devralma_zamani']}). Yeni gorevleri artik sen dagitiyorsun.",
    )
    print(f"DEVRALDI : {kayit['ajan']}")
    print(f"ZAMAN    : {kayit['devralma_zamani']}")
    print(f"PARMAKIZI: {kayit['anahtar_parmak_izi'][:12]}…")
    print(f"TETIK    : python scripts/gorev_kutusu.py bak --ajan {args.ajan}")
    return 0


def cmd_at(args: argparse.Namespace) -> int:
    kapi = _orkestrator_kapisi(getattr(args, "cagiran", None) or os.getenv("ORKESTRA_AJAN"))
    if kapi:
        print(f"HATA (D-58): {kapi}", file=sys.stderr)
        return 4
    ihlal = _d57_dogrula(args.task_id, args.baslik, args.ajan)
    if ihlal:
        print(f"HATA (D-57): {ihlal}", file=sys.stderr)
        return 3
    mod = getattr(args, "mod", "code") or "code"
    if mod == "architect" and args.ajan not in ARCHITECT_AJANLARI:
        print(
            "HATA (D-63): Architect gorevini yalnız "
            f"{' / '.join(ARCHITECT_AJANLARI)} alabilir; verilen: {args.ajan}",
            file=sys.stderr,
        )
        return 5
    try:
        gorev = tb.gorev_ekle(
            task_id=args.task_id,
            baslik=args.baslik,
            sahip=args.ajan,
            oncelik=args.oncelik,
            dosyalar=_ayristir_liste(args.dosya),
            mod=mod,
        )
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"HATA (kilit): {exc}", file=sys.stderr)
        print("Dosya baska bir ajanin kilidinde; farkli kapsamla atayin.", file=sys.stderr)
        return 2
    talimat = args.talimat or ""
    if mod == "architect":
        talimat = (talimat + "\n" + ARCHITECT_HATIRLATMA).strip()
    trigger.tetik_ekle(args.task_id, args.ajan, talimat)
    print(f"ATANDI  : {gorev['task_id']} -> {args.ajan} ({gorev['oncelik']}, mod={mod})")
    print(f"BASLIK  : {gorev['baslik']}")
    if gorev["dosyalar"]:
        print(f"KILITLI : {', '.join(gorev['dosyalar'])}")
    if mod == "architect":
        print(f"MOD     : {ARCHITECT_HATIRLATMA}")
    print(f"TETIK   : {args.ajan} postasina dusecek; ajan bakarsa gorur.")
    print(f"          python scripts/gorev_kutusu.py bak --ajan {args.ajan}")
    print(f"HAZIR   : Ajana gidip sadece 'başla' veya 'go' yazmanız yeterlidir (Kural dosyası postayı otomatik okur).")

    return 0


def _kisa_tarih(iso: str | None) -> str:
    """ISO tarihi 'MM-DD HH:MM' formatina kisalir; parse edilemezse ilk 16 karakter."""
    if not iso:
        return "-"
    try:
        return datetime.fromisoformat(str(iso)).strftime("%m-%d %H:%M")
    except ValueError:
        return str(iso)[:16]


def _gorev_basligi(task_id: str | None) -> str:
    """Panodan gorev basligini getirir; gorev bulunamazsa '-'."""
    if not task_id:
        return "-"
    try:
        gorev = tb.gorev_getir(str(task_id))
    except Exception:  # noqa: BLE001 - pano ciktisi hata yuzunden cokmemeli
        return "-"
    if not gorev:
        return "-"
    return str(gorev.get("baslik") or "-")


def _kisalt(metin: str | None, limit: int) -> str:
    """Metni limit uzunlugunda keser; mumkunse kelime sinirinda keser, '…' ekler."""
    metin = (metin or "").strip()
    if len(metin) <= limit:
        return metin
    kirpik = metin[: limit - 1]
    bosluk = kirpik.rfind(" ")
    if bosluk > limit // 2:  # kelime siniri varsa orada kes
        kirpik = kirpik[:bosluk]
    return kirpik.rstrip() + "…"


def cmd_pano(args: argparse.Namespace) -> int:
    ajanlar = sorted({str(t.get("sahip") or "?") for t in tb.gorev_listesi()})
    print("== AJAN POSTALARI (bekleyen tetik) ==")
    herhangi_biri = False
    for ajan in ajanlar:
        bekleyen = trigger.bekleyen_tetikler(ajan)
        if bekleyen:
            herhangi_biri = True
            for k in bekleyen:
                task_id = str(k.get("task_id") or "?")
                baslik = _kisalt(_gorev_basligi(task_id), 28)
                print(
                    f"  [{ajan:<14}] {task_id:<10} "
                    f"({_kisa_tarih(k.get('tarih'))})  {baslik}"
                )
    if not herhangi_biri:
        print("  (bos)")
    print("\n== ONAY KUYRUGU (kontrol bekleyen teslimler) ==")
    kuyruk = trigger.onay_bekleyenler()
    if not kuyruk:
        print("  (bos)")
    else:
        for k in kuyruk:
            task_id = str(k.get("task_id") or "?")
            ajan = str(k.get("ajan") or "?")
            baslik = _kisalt(_gorev_basligi(task_id), 28)
            print(
                f"  {task_id:<10} <- {ajan:<14} "
                f"({_kisa_tarih(k.get('teslim_tarihi'))})  {baslik}"
            )
            print(f"    {_kisalt(k.get('ozet'), 50)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Orkestratör görev atama (ORCH-08)")
    alt = parser.add_subparsers(dest="komut", required=True)

    p_at = alt.add_parser("at", help="Panoya görev ekle + ajana tetik düşür")
    p_at.add_argument("--task-id", required=True)
    p_at.add_argument("--baslik", required=True)
    p_at.add_argument("--ajan", required=True, help="sahip + posta kutusu (ör. kilo)")
    p_at.add_argument("--oncelik", default="P1", choices=["P0", "P1", "P2"])
    p_at.add_argument("--dosya", default=None, help="Virgülle ayrılı, otomatik kilitlenir")
    p_at.add_argument("--talimat", default="", help="Ajana kısa talimat")
    p_at.add_argument(
        "--mod", default="code", choices=["code", "architect"],
        help="D-63: architect sadece ihsan/utku'ya atanabilir",
    )
    p_at.add_argument("--cagiran", default=None, help="Komutu veren ajan (D-58 kapısı)")
    p_at.set_defaults(func=cmd_at)

    p_pano = alt.add_parser("pano", help="Tetik + onay kuyruğu özetini göster")
    p_pano.set_defaults(func=cmd_pano)

    p_abra = alt.add_parser("abrakadabra", help="Orkestratörlüğü devral (D-58)")
    p_abra.add_argument("--ajan", required=True, help="Yeni orkestratör (kilo/cline/roo)")
    p_abra.add_argument("--anahtar", required=True, help="ABRAKADABRA_KEY degeri")
    p_abra.set_defaults(func=cmd_abrakadabra)

    args = parser.parse_args()
    # D-33 ajan adı kuralı: "Ajan kilo" / "Kilo" / "kilo_code" → "kilo".
    if getattr(args, "ajan", None):
        try:
            args.ajan = trigger.ajan_normalize(args.ajan)
        except trigger.TriggerError as exc:
            print(f"HATA: {exc}")
            return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
