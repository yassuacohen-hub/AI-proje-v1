# -*- coding: utf-8 -*-
"""ORCH-08 — Orkestratör görev atama komutu.

Kullanım (repo kökünden):
    python scripts/gorev_at.py at --task-id ORCH-09 --baslik "..." --ajan kilo \
        --oncelik P1 --dosya "src/a.py,docs/b.md" --talimat "..."
    python scripts/gorev_at.py pano

`at` görevi panoya ekler (dosyaları kilitler) ve ajana tetik düşürür.
Ajan `scripts/gorev_kutusu.py bak --ajan kilo` ile postasını görür.

Karar: [[D-182]] — Orkestratör Asistanı İki Seviye (cmd_abrakadabra komutu, key rotasyonu)
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

# Windows konsolu cp1254; "→" ve Türkçe karakterler patlamasın.
for _akis in (sys.stdout, sys.stderr):
    if hasattr(_akis, "reconfigure"):
        try:
            _akis.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass  # Streamlit ortamında başarısız olabilir; ignore

from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]


def _brief_bul(ajan: str, task_id: str) -> Path | None:
    """D-66: brif dosyasini diskte arar; bulamazsa None.

    Iki kanonik konum: plans/brief_<ajan>_<TASK>.md ve
    data/orchestrator/<TASK>_brif_<tarih>_<rol>.md. Yollar KOK'e gore mutlak —
    CWD'ye guvenilmez, komut repo disindan da cagrilabiliyor.
    """
    tekil = KOK / "plans" / f"brief_{ajan}_{task_id}.md"
    if tekil.exists():
        return tekil
    eskiler = sorted((KOK / "data" / "orchestrator").glob(f"{task_id}_brif_*.md"))
    return eskiler[-1] if eskiler else None


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
_VARSAYILAN_ORKESTRATOR = "ihsan"  # D-71 canonical


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
    # D-86: cmd.exe'de "set ORKESTRA_AJAN=roo && ..." degere sondaki boslugu
    # katar ('roo ') ve kapi aktif orkestratoru kendi kimliginden reddeder.
    cagiran = (cagiran or "").strip()
    if not cagiran:
        return None
    aktif = (_orkestrator_oku().get("ajan") or _VARSAYILAN_ORKESTRATOR).strip()
    if cagiran != aktif:
        return f"gorev atamayi yalniz aktif orkestrator yapar; aktif: '{aktif}', cagiran: '{cagiran}'"
    return None


def _anahtar_dondur(yeni_anahtar: str) -> None:
    """D-182: devralma basarili olunca yeni anahtar uretilir; .env varsa atomik guncellenir, yoksa key dosyasina yazilir.

    ponytail: coklu-instance kilitleme yok (dosya yazma yarisina karsi); tek operator varsayimi.
    Coklu operator/deployment cikarsa fcntl/msvcrt kilidi eklenir.
    """
    env_dosya = KOK / ".env"
    if env_dosya.exists():
        satirlar = env_dosya.read_text(encoding="utf-8").splitlines()
        bulundu = False
        for i, satir in enumerate(satirlar):
            if satir.startswith("ABRAKADABRA_KEY="):
                satirlar[i] = f"ABRAKADABRA_KEY={yeni_anahtar}"
                bulundu = True
                break
        if not bulundu:
            satirlar.append(f"ABRAKADABRA_KEY={yeni_anahtar}")
        tmp = env_dosya.with_suffix(".env.tmp")
        tmp.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
        os.replace(tmp, env_dosya)
    else:
        _ANAHTAR_DOSYA.parent.mkdir(parents=True, exist_ok=True)
        _ANAHTAR_DOSYA.write_text(yeni_anahtar, encoding="utf-8")


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
    yeni_anahtar = secrets.token_urlsafe(32)
    _anahtar_dondur(yeni_anahtar)
    trigger.tetik_ekle(
        "ORKESTRA-DEVRALMA",
        args.ajan,
        f"Orkestratorluk devralindi ({kayit['devralma_zamani']}). Yeni gorevleri artik sen dagitiyorsun.",
    )
    print(f"DEVRALDI : {kayit['ajan']}")
    print(f"ZAMAN    : {kayit['devralma_zamani']}")
    print(f"PARMAKIZI: {kayit['anahtar_parmak_izi'][:12]}…")
    print("ANAHTAR  : rotasyon tamamlandi (yeni anahtar env/key dosyasina yazildi, ekrana basilmadi)")
    print(f"TETIK    : python scripts/gorev_kutusu.py bak --ajan {args.ajan}")
    return 0


def _baslik_coz(args: argparse.Namespace) -> str | None:
    """--baslik-b64 verilmişse çözer, yoksa --baslik'i döner. Hata metni döner ya da None.

    cmd.exe cp1254 olduğu için "→" ve Türkçe karakterler doğrudan argüman
    olarak geçirildiğinde bozulur; base64 bu katmanı atlatır.
    """
    b64 = getattr(args, "baslik_b64", None)
    if not b64:
        return None
    try:
        args.baslik = base64.b64decode(b64).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        return f"--baslik-b64 cozulemedi (utf-8 base64 bekleniyor): {exc}"
    return None


def cmd_at(args: argparse.Namespace) -> int:
    hata = _baslik_coz(args)
    if hata:
        print(f"HATA: {hata}", file=sys.stderr)
        return 1
    kapi = _orkestrator_kapisi(getattr(args, "cagiran", None) or os.getenv("ORKESTRA_AJAN"))
    if kapi:
        print(f"HATA (D-58): {kapi}", file=sys.stderr)
        return 4
    ihlal = _d57_dogrula(args.task_id, args.baslik, args.ajan)
    if ihlal:
        print(f"HATA (D-57): {ihlal}", file=sys.stderr)
        return 3
    # Once ATAMA gecerli mi (D-63); gecersiz atama icin brif aramak anlamsiz.
    mod = getattr(args, "mod", "code") or "code"
    if mod == "architect" and args.ajan not in ARCHITECT_AJANLARI:
        print(
            "HATA (D-63): Architect gorevini yalnız "
            f"{' / '.join(ARCHITECT_AJANLARI)} alabilir; verilen: {args.ajan}",
            file=sys.stderr,
        )
        return 5
    # D-66/D-80: Brif VE talimat ikisi de zorunlu. Eskiden kosul "and" idi;
    # talimat verilince brif atlanabiliyordu -> bos 'brief' alanli gorevler.
    # Pano tasinabilir kalsin: brif KOK'e goreli, POSIX ayracli yazilir.
    brief_yolu = _brief_bul(args.ajan, args.task_id)
    if brief_yolu is None:
        print(
            "HATA (D-66): Brif dosyasi diskte yok. Once yaz: "
            f"plans/brief_{args.ajan}_{args.task_id}.md "
            f"(veya data/orchestrator/{args.task_id}_brif_<tarih>_<rol>.md)",
            file=sys.stderr,
        )
        return 6
    brief_goreli = brief_yolu.relative_to(KOK).as_posix()
    if not (args.talimat or "").strip():
        print(
            "HATA (D-80): --talimat bos. En az bir cumle + brif referansi sart: "
            f"--talimat \"{args.task_id}: <ne yapilacak>. Brif: {brief_goreli}\"",
            file=sys.stderr,
        )
        return 6
    talimat = (args.talimat or "").strip()
    if mod == "architect":
        talimat = (talimat + "\n" + ARCHITECT_HATIRLATMA).strip()
    try:
        gorev = tb.gorev_ekle(
            task_id=args.task_id,
            baslik=args.baslik,
            sahip=args.ajan,
            oncelik=args.oncelik,
            dosyalar=_ayristir_liste(args.dosya),
            mod=mod,
            brief=brief_goreli,
            talimat=talimat,
        )
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"HATA (kilit): {exc}", file=sys.stderr)
        print("Dosya baska bir ajanin kilidinde; farkli kapsamla atayin.", file=sys.stderr)
        return 2
    # D-80 sart 3: tetik talimati pano talimatiyla AYNI metin.
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


def cmd_guncelle(args: argparse.Namespace) -> int:
    """D-87: brief/talimat/oncelik/durum duzeltmesi icin tek komut.

    Elle script yazmayi bitirir. Sessiz basari yasak: hicbir alan verilmediyse
    ya da gorev yoksa sifirdan farkli doner.
    """
    kapi = _orkestrator_kapisi(getattr(args, "cagiran", None) or os.getenv("ORKESTRA_AJAN"))
    if kapi:
        print(f"HATA (D-58): {kapi}", file=sys.stderr)
        return 4

    alanlar: dict[str, str] = {}
    # Eski cagiranlarin namespace'inde --sahip yok; dogrudan okumak AttributeError.
    sahip = getattr(args, "sahip", None)
    # NAMING-AUDIT-02: D-57 ihlalli eski basliklar elle duzeltilemiyordu; tek
    # yol pano JSON'una dokunmakti (D-77 ihlali). Basligi buradan gecirince
    # ayni _d57_dogrula kapisindan gecer -- ihlalin yerine ihlal koyulamaz.
    if getattr(args, "baslik", None) or getattr(args, "baslik_b64", None):
        hata = _baslik_coz(args)
        if hata:
            print(f"HATA: {hata}", file=sys.stderr)
            return 1
        mevcut = tb.gorev_getir(args.task_id)
        if mevcut is None:
            print(f"HATA: gorev panoda yok: {args.task_id}", file=sys.stderr)
            return 1
        ihlal = _d57_dogrula(args.task_id, args.baslik, sahip or mevcut.get("sahip", ""))
        if ihlal:
            print(f"HATA (D-57): {ihlal}", file=sys.stderr)
            return 3
        alanlar["baslik"] = args.baslik
    if sahip:
        if sahip not in AJANLAR:
            print(
                f"HATA (D-60): sahip '{sahip}' kanonik degil; izinli: {', '.join(AJANLAR)}",
                file=sys.stderr,
            )
            return 3
        alanlar["sahip"] = sahip
    if args.brief:
        # D-66: brief alani yalnizca diskte var olan dosyayi gosterebilir.
        yol = KOK / args.brief
        if not yol.exists():
            print(f"HATA (D-66): brif dosyasi yok: {args.brief}", file=sys.stderr)
            return 6
        alanlar["brief"] = Path(args.brief).as_posix()
    if args.talimat:
        alanlar["talimat"] = args.talimat.strip()
    if args.oncelik:
        alanlar["oncelik"] = args.oncelik
    if not alanlar and not args.durum:
        print(
            "HATA: guncellenecek alan yok (--baslik/--sahip/--brief/--talimat/--oncelik/--durum)",
            file=sys.stderr,
        )
        return 1

    try:
        gorev = tb.gorev_guncelle(args.task_id, durum=args.durum, **alanlar)
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1
    if gorev is None:  # sessiz basari yasagi: 0 kayit != basari
        print(f"HATA: gorev panoda yok: {args.task_id}", file=sys.stderr)
        return 1

    degisen = ", ".join([*alanlar, *(["durum"] if args.durum else [])])
    print(f"GUNCELLENDI: {args.task_id} ({degisen})")
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
    # D-60: ajan listesi KANONIK kaynaktan gelir. Panodan turetilirse eski
    # 'cline'/'yasin' sahip degerleri alias tablosundan yasu'ya cozulur ve
    # ayni tetik dosyasi iki kez okunur -> gorev cift listelenir.
    ajanlar = list(trigger.AJANLAR)
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
    _baslik_grup = p_at.add_mutually_exclusive_group(required=True)
    _baslik_grup.add_argument("--baslik", help="D-57 kalibinda baslik")
    _baslik_grup.add_argument(
        "--baslik-b64",
        help="Baslik utf-8 base64; cmd.exe Unicode bozulmasini atlatir",
    )
    p_at.add_argument("--ajan", required=True, help="sahip + posta kutusu (ör. kilo)")
    # P3 zaten onayla_ve_sirala.py:43 siralamasinda var; burada eksikti.
    p_at.add_argument("--oncelik", default="P1", choices=["P0", "P1", "P2", "P3"])
    p_at.add_argument("--dosya", default=None, help="Virgülle ayrılı, otomatik kilitlenir")
    p_at.add_argument("--talimat", default="", help="Ajana kısa talimat")
    p_at.add_argument(
        "--mod", default="code", choices=["code", "architect"],
        help="D-63: architect sadece ihsan/utku'ya atanabilir",
    )
    p_at.add_argument("--cagiran", default=None, help="Komutu veren ajan (D-58 kapısı)")
    p_at.set_defaults(func=cmd_at)

    p_upd = alt.add_parser("guncelle", help="Mevcut görevin alanlarını düzelt (D-87)")
    p_upd.add_argument("--task-id", required=True)
    _upd_baslik = p_upd.add_mutually_exclusive_group()
    _upd_baslik.add_argument("--baslik", default=None, help="Yeni baslik (D-57 dogrulanir)")
    _upd_baslik.add_argument("--baslik-b64", default=None, help="Yeni baslik utf-8 base64")
    p_upd.add_argument("--sahip", default=None, help="Sahibi duzelt (kanonik ajan)")
    p_upd.add_argument("--brief", default=None, help="KÖK'e göreli brif yolu; varlığı doğrulanır")
    p_upd.add_argument("--talimat", default=None)
    p_upd.add_argument("--oncelik", default=None, choices=["P0", "P1", "P2", "P3"])
    p_upd.add_argument("--durum", default=None, choices=list(tb.GOREV_DURUMLARI))
    p_upd.add_argument("--cagiran", default=None, help="Komutu veren ajan (D-58 kapısı)")
    p_upd.set_defaults(func=cmd_guncelle)

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
