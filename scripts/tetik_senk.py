#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tetik-Pano Senkronizasyonu: Pano durumu ile tetik dosyaları uyum sağla.

Kök sorun: ADMIN-UX-LOGOUT-01 panoda `review` ama tetiği hâlâ `bekliyor`,
nöbetçi sonsuz uyarı üretiyor. Bu script panodaki final durumları tetik dosyalarıyla
eşitler ve sayaçları sıfırlar.

Kullanım (ALTYAPI-TETIK-ZAMAN-01):
    python scripts/tetik_senk.py             # tek seferlik senkron
    python scripts/tetik_senk.py --gunluk    # senkron + gunluk log satiri
    python scripts/tetik_senk.py kur         # gunluk zamanlayici bagla (schtasks)
    python scripts/tetik_senk.py durum       # zamanlayici + son log satirlari
    python scripts/tetik_senk.py kaldir      # zamanlayiciyi sil (geri al)

Gunluk log (--gunluk): data/orchestrator/tetik_senk_log.jsonl
    {"an": ISO, "senk": N, "sapma": M}

Çıkış kodları (sessiz basari yasagi):
    0 -> senkron temiz (sapma yok)
    1 -> okuma/yazma hatasi var
    2 -> duzeltilemeyen sapma var (bkz. ALTYAPI-TETIK-ZAMAN-01)
    3 -> hic tetik dosyasi bulunamadi (yol/kurulum hatasi)
    4 -> --gunluk istendi ama log satiri yazilamadi (0 satir etkilendi)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# Windows konsolu cp1254; rapor satirlarindaki emoji UnicodeEncodeError veriyordu.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import düzeltme
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.company_master.orchestrator import task_board as tb, trigger as trig


#: Pano bu durumlardaysa gorev kapanmistir; tetik kuyrugunda acik kalmamali.
FINAL_PANO_DURUMLARI = ("done", "blocked", "archive", "reddedildi", "iptal")

#: Tetik kuyrugundaki "acik" (ucusta) durumlar. Panoda final olan bir gorevin
#: tetigi bu durumlardan birindeyse sapma vardir; `kapandi` yapilarak duzeltilir.
ACIK_TETIK_DURUMLARI = ("bekliyor", "alindi", "teslim", "zincir_bekleme", "blocked")

#: Gunluk senkron log dosyasi (JSONL).
LOG_DOSYA_ADI = "tetik_senk_log.jsonl"


def tetik_senk() -> dict[str, Any]:
    """Pano durumlarını tetik kuyruğu dosyalarıyla senkronize et."""
    rapor = {
        "tarih": datetime.now(timezone.utc).isoformat(),
        "basarili": 0,
        "hata": 0,
        "sapma": 0,  # tespit edilip DUZELTILEMEYEN sapma (sessiz basari yasagi)
        "bulunan_dosya": 0,  # sessiz basari yasagi: 0 ise hic tarama yapilmamis
        "detay": []
    }

    try:
        pano = json.loads(tb.TASK_BOARD.read_text(encoding='utf-8'))
    except Exception as e:
        rapor["hata"] += 1
        rapor["sapma"] += 1  # okunamayan panoya karsi senkron yapilamaz -> duzeltilemez
        rapor["detay"].append(f"❌ Pano okunamadı: {e}")
        return rapor

    # Görev durumlarını ve sahibini ID'ye göre inşa et
    pano_durum_map = {t["task_id"]: {
        "durum": t.get("durum", "plan"),
        "sahip": t.get("sahip", "-"),
        "baslik": t.get("baslik", "")
    } for t in pano}

    # Tetik kuyruğu dosyaları (tüm ajanlar)
    # D-33/D-60: kanonik ajan listesi tek kaynak = trigger.AJANLAR
    ajanlar = list(trig.AJANLAR)
    # VAULT-CLEANUP-BATCH: onceden `Path("data/orchestrator")` idi; hem goreli
    # (cwd'ye bagimli) hem de `triggers/` alt klasorunu atliyordu -> script hicbir
    # tetik bulamadan sessizce basarili donuyordu.
    data_dir = tb.STATE_DIR / "triggers"

    for ajan in ajanlar:
        tetik_dosya = data_dir / f"{ajan}.jsonl"

        if not tetik_dosya.exists():
            rapor["detay"].append(f"ℹ️  {ajan}: tetik dosyası yok (posta boş)")
            continue
        rapor["bulunan_dosya"] += 1

        # Tetik satırlarını oku
        tetikler = []
        try:
            with tetik_dosya.open(encoding='utf-8') as f:
                for satir in f:
                    if satir.strip():
                        tetikler.append(json.loads(satir))
        except Exception as e:
            rapor["hata"] += 1
            rapor["sapma"] += 1  # okunamayan kuyruk duzeltilemez
            rapor["detay"].append(f"❌ {ajan}.jsonl okunamadı: {e}")
            continue

        # Senkronizasyon: pano durumuna göre tetikleri düzelt
        tetikler_guncel = []
        duzeltilen = []

        for tetik in tetikler:
            task_id = tetik.get("task_id")
            pano_bilgi = pano_durum_map.get(task_id)

            if not pano_bilgi:
                # Pano'da bu görev yok -> bekliyor kalır (bayat tetik).
                # Tetik hâlâ "acik" ise bu duzeltilemeyen bir sapmadir: hangi
                # panoya ait oldugu bilinmeden kapatilamaz (exit != 0).
                if tetik.get("durum") in ACIK_TETIK_DURUMLARI:
                    rapor["sapma"] += 1
                    rapor["detay"].append(
                        f"⚠️  {ajan}: {task_id} tetigi acik ('{tetik.get('durum')}') "
                        "ama panoda gorev yok — duzeltilemedi"
                    )
                tetikler_guncel.append(tetik)
                continue

            pano_durum = pano_bilgi["durum"]

            # Pano durumuna göre tetik durumunu güncelle
            # "iptal" de final durumdur; onceden listede yoktu, iptal edilen
            # gorevlerin tetigi sonsuz uyari uretiyordu (VAULT-CLEANUP-BATCH).
            # ALTYAPI-TETIK-ZAMAN-01: yalniz "bekliyor" degil, ucusta olan tum
            # acik durumlar (alindi/teslim/zincir_bekleme/blocked) kapatilir;
            # aksi halde panoda biten gorev kuyrukta acik kalip sapma uretiyordu.
            if pano_durum in FINAL_PANO_DURUMLARI:
                # Final durumlar: tetiği kapat
                tetik_eski_durum = tetik.get("durum")
                if tetik_eski_durum in ACIK_TETIK_DURUMLARI:
                    tetik["durum"] = "kapandi"
                    tetik["kapanma_nedeni"] = f"pano durumu {pano_durum}"
                    duzeltilen.append(f"{task_id}: {tetik_eski_durum} → kapandi")
                tetikler_guncel.append(tetik)
            else:
                # Aktif durumlar: tetik bekleyen kalır veya sahip güncellenirse işle
                eski_ajan = tetik.get("ajan", "")
                # Normalize: "cline" → "yasu"
                yeni_ajan = trig.ajan_normalize(eski_ajan)
                if eski_ajan != yeni_ajan:
                    tetik["ajan"] = yeni_ajan
                    duzeltilen.append(f"{task_id}: ajan '{eski_ajan}' → '{yeni_ajan}'")
                tetikler_guncel.append(tetik)

        # Tetik dosyasına geri yaz
        try:
            with tetik_dosya.open('w', encoding='utf-8') as f:
                for tetik in tetikler_guncel:
                    f.write(json.dumps(tetik, ensure_ascii=False) + '\n')
            rapor["basarili"] += len(duzeltilen)
            if duzeltilen:
                rapor["detay"].append(f"✅ {ajan}: {len(duzeltilen)} düzeltme")
                rapor["detay"].extend([f"   - {d}" for d in duzeltilen])
        except Exception as e:
            rapor["hata"] += 1
            rapor["sapma"] += 1  # yazilamayan duzeltme = uygulanmamis sapma
            rapor["detay"].append(f"❌ {ajan}.jsonl yazılamadı: {e}")
            continue

    return rapor


def _log_satiri(rapor: dict[str, Any]) -> dict[str, Any]:
    """Gunluk log satirini uret: {"an": ISO, "senk": N, "sapma": M}."""
    return {
        "an": datetime.now(timezone.utc).isoformat(),
        "senk": int(rapor.get("basarili", 0)),
        "sapma": int(rapor.get("sapma", 0)),
    }


def gunluk_log_yaz(rapor: dict[str, Any], yol: Path | None = None) -> bool:
    """Senkron sonucunu JSONL gunluk loga EKLE (append). Basarili ise True.

    Her gunluk kosu bir satir birakir; senk=0 olsa bile iz kalir. Yazilamazsa
    False doner ve rapora hata islenir (sessiz basari yasagi -> exit 4).
    """
    hedef = Path(yol) if yol else (tb.STATE_DIR / LOG_DOSYA_ADI)
    try:
        hedef.parent.mkdir(parents=True, exist_ok=True)
        with hedef.open("a", encoding="utf-8") as f:
            f.write(json.dumps(_log_satiri(rapor), ensure_ascii=False) + "\n")
    except Exception as e:
        rapor["hata"] += 1
        rapor["detay"].append(f"❌ gunluk log yazilamadi ({hedef}): {e}")
        return False
    rapor["detay"].append(f"📝 gunluk log satiri yazildi: {hedef}")
    return True


def cikis_kodu(rapor: dict[str, Any], log_yazildi: bool = True) -> int:
    """Rapordan cikis kodunu turet (sessiz basari yasagi)."""
    if rapor.get("bulunan_dosya", 0) == 0:
        return 3  # hic tetik dosyasi yok -> yol/kurulum hatasi
    if rapor.get("sapma", 0) > 0:
        return 2  # duzeltilemeyen sapma var -> sessizce 0 donulemez
    if not log_yazildi:
        return 4  # --gunluk istendi ama 0 satir yazildi
    if rapor.get("hata", 0) > 0:
        return 1
    return 0


def cmd_senkron(args: argparse.Namespace) -> int:
    """Tek senkron kosusu (+ istege bagli gunluk log satiri)."""
    # D-66: bypass-override flag (manual tetikleme, saat uyuşmazlığı bypass)
    if args.bypass_override:
        neden = args.bypass_reason or "D-66 — Manual bypass"
        print("\n" + "="*60)
        print("D-66 BYPASS TETIKLEME (MANUAL OVERRIDE)")
        print("="*60)
        print(f"Neden: {neden}")
        print(f"Zaman: {datetime.now(timezone.utc).isoformat()}")
        print("="*60 + "\n")
        import logging
        logger = logging.getLogger("tetik_senk")
        if not logger.handlers:
            logging.basicConfig(level=logging.INFO)
        logger.info(f"D-66 bypass tetikleme: reason={neden}, timestamp={datetime.now(timezone.utc).isoformat()}")
        rapor = tetik_senk()
        rapor["detay"].insert(0, f"🔄 D-66 BYPASS: {neden}")
    else:
        rapor = tetik_senk()

    log_yazildi = True
    if args.gunluk:
        log_yazildi = gunluk_log_yaz(rapor)

    print("\n" + "="*60)
    print("TETIK-PANO SENKRONİZASYONU")
    print("="*60)
    for satir in rapor["detay"]:
        print(satir)
    print(f"\nSonuç: ✅ {rapor['basarili']} | sapma: {rapor['sapma']} "
          f"| ❌ {rapor['hata']} | taranan dosya: {rapor['bulunan_dosya']}")
    print("="*60 + "\n")

    kod = cikis_kodu(rapor, log_yazildi)
    # Sessiz basari yasagi: exit 0 disindaki her kod icin NEDEN yazilir.
    if kod == 3:
        print("HATA: Hicbir tetik dosyasi bulunamadi; yol yanlis olabilir "
              f"({tb.STATE_DIR / 'triggers'}).", file=sys.stderr)
    elif kod == 2:
        print(f"HATA: {rapor['sapma']} duzeltilemeyen sapma var "
              "(sessiz basari yasagi).", file=sys.stderr)
    elif kod == 4:
        print("HATA: gunluk log satiri yazilamadi (0 satir etkilendi).",
              file=sys.stderr)
    return kod


# ---- zamanlayici baglamasi (schtasks; gorev_nobetci.py ile ayni desen) ----

#: Windows Gorev Zamanlayici gorev adi.
ZAMANLAYICI_GOREV = "HuginnData-TetikSenk"

_BAT_YOL = Path(__file__).resolve().parent / "tetik_senk.bat"
_VBS_YOL = Path(__file__).resolve().parent / "tetik_senk.vbs"


def _bat_olustur() -> Path:
    """Gunluk kosuyu cagiran bat dosyasini uret (cikti ayri log dosyasina)."""
    root = str(Path(tb.ROOT))
    icerik = (
        "@echo off\r\n"
        f'cd /d "{root}"\r\n'
        "python scripts\\tetik_senk.py --gunluk "
        ">> data\\orchestrator\\tetik_senk_cikti.log 2>&1\r\n"
    )
    _BAT_YOL.write_text(icerik, encoding="utf-8")
    return _BAT_YOL


def _vbs_olustur() -> Path:
    """Bat dosyasini GIZLI pencerede calistiran VBS sarmalayici (FIX-NOB-02 deseni)."""
    icerik = (
        "' ALTYAPI-TETIK-ZAMAN-01: tetik_senk.bat dosyasini gizli pencerede calistirir\r\n"
        'Set sh = CreateObject("WScript.Shell")\r\n'
        f'sh.Run "cmd /c ""{_BAT_YOL}""", 0, False\r\n'
    )
    _VBS_YOL.write_text(icerik, encoding="utf-8")
    return _VBS_YOL


def cmd_kur(args: argparse.Namespace) -> int:
    """Gunluk senkronu Windows Gorev Zamanlayici'ya bagla."""
    bat = _bat_olustur()
    vbs = _vbs_olustur()
    tr = f'wscript.exe "{vbs}"'
    komut = ["schtasks", "/Create", "/TN", ZAMANLAYICI_GOREV, "/TR", tr,
             "/SC", "DAILY", "/ST", args.saat, "/F"]
    try:
        r = subprocess.run(komut, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", check=False)
    except Exception as exc:
        print(f"HATA: schtasks calistirilamadi: {exc}", file=sys.stderr)
        return 1
    if r.returncode != 0:
        print(f"HATA: zamanlayici kurulamadi (kod {r.returncode}): "
              f"{(r.stdout or r.stderr or '').strip()}", file=sys.stderr)
        print("Elle kurulum: " + " ".join(f'"{p}"' if " " in p else p for p in komut),
              file=sys.stderr)
        return 1
    print(f"Zamanlayici kuruldu: {ZAMANLAYICI_GOREV} (gunluk {args.saat})")
    print(f"  bat: {bat}")
    print(f"  vbs: {vbs}")
    print("  kaldir: python scripts/tetik_senk.py kaldir")
    return 0


def cmd_kaldir(args: argparse.Namespace) -> int:
    """Zamanlayiciyi sil (tek komutla geri al)."""
    try:
        r = subprocess.run(["schtasks", "/Delete", "/TN", ZAMANLAYICI_GOREV, "/F"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", check=False)
    except Exception as exc:
        print(f"HATA: schtasks calistirilamadi: {exc}", file=sys.stderr)
        return 1
    if r.returncode != 0:
        print(f"Zamanlayici kaydi silinemedi: {(r.stdout or r.stderr or '').strip()}")
        return 0  # kayit yoksa da istenen son durum saglanmis olur
    print(f"Zamanlayici kaldirildi: {ZAMANLAYICI_GOREV}")
    return 0


def cmd_durum(args: argparse.Namespace) -> int:
    """Zamanlayici kaydi + son gunluk log satirlarini goster."""
    try:
        r = subprocess.run(["schtasks", "/Query", "/TN", ZAMANLAYICI_GOREV,
                            "/fo", "LIST", "/v"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", check=False)
        print((r.stdout or "").strip() if r.returncode == 0
              else "Zamanlayici kaydi yok (`kur` ile bagla).")
    except Exception as exc:
        print(f"Zamanlayici sorgulama hatasi: {exc}")

    log = tb.STATE_DIR / LOG_DOSYA_ADI
    print(f"\nGunluk log: {log}")
    if not log.exists():
        print("  (henuz satir yok)")
        return 0
    satirlar = [s for s in log.read_text(encoding="utf-8").splitlines() if s.strip()]
    print(f"  satir sayisi: {len(satirlar)}")
    for s in satirlar[-5:]:
        print(f"  {s}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Geriye uyum: `tetik_senk.py` ve `tetik_senk.py --gunluk` = senkron kosusu.
    if not argv or argv[0] not in ("senkron", "kur", "kaldir", "durum"):
        argv = ["senkron"] + argv

    parser = argparse.ArgumentParser(
        description="Pano durumu ile tetik kuyrugunu senkronize et "
                    "(+ gunluk zamanlayici baglamasi)."
    )
    alt = parser.add_subparsers(dest="komut", required=True)

    p = alt.add_parser("senkron", help="Tek senkron kosusu (varsayilan)")
    p.add_argument(
        "--gunluk", action="store_true",
        help=f"Sonucu {LOG_DOSYA_ADI} dosyasina gunluk satir olarak ekle",
    )
    p.add_argument(
        "--bypass-override", action="store_true",
        help="D-66: Saat uyuşmazlığını bypass et (manual tetikleme)",
    )
    p.add_argument(
        "--bypass-reason", type=str, default=None,
        help="D-66 bypass sebebi (loglama için)",
    )
    p.set_defaults(func=cmd_senkron)

    p = alt.add_parser("kur", help="Gunluk senkronu Gorev Zamanlayici'ya bagla")
    p.add_argument("--saat", default="08:30", help="Gunluk calisma saati (SS:DD)")
    p.set_defaults(func=cmd_kur)

    alt.add_parser("kaldir", help="Zamanlayiciyi sil").set_defaults(func=cmd_kaldir)
    alt.add_parser("durum", help="Zamanlayici + son log satirlari").set_defaults(
        func=cmd_durum)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
