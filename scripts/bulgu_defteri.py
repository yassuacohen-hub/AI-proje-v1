"""D-318 — Bulgu Defteri kanonik doküman; teslim kapısına bağlanır.

Karar (KAHİN, 2026-10-02): "Bulgu defteri kanonik doküman olsun, her tur
sonunda doldursun. Herkes özel bulgu defteri mi istiyor? Tek bir bulgu
defteri format belirleyelim, tek yeterli olur mu?"

Ölçülen cevaplar:

* **Tek yeterli.** Ajan başına ayrı bulgu defteri **0 tane** — ayrı defter
  ihtiyacı doğrulanmamış bir varsayımdır. D-224: varsayım ölçülmeden
  karara dönüşmez.
* **Kural yazılıydı, zorlanmıyordu.** AGENTS.md'de "Bulgu İşleme Zorunluluğu"
  bölümü ve `bulgu_defteri.md` yolu **vardı**; dosya diskte **yoktu**.
  123 teslim raporundan yalnız 25'inde `## Bulgular` bölümü var (%20).
  `cmd_teslim` bulgu defterini hiç aramıyor.
* **Bu tur bir teslim daha ekledi ve aynı hatayı yaptı:** teslim özeti
  bulguları sıkıştırmak yerine defter tutuldu, defter yoktu.

Kural: defter zaten kuraldı, **eksik olan zorlayıcıydı** (D-239 deseni —
kural gövdesi tek dosyada yaşar, teslim komutu onu çağırır).

Bu modül tek yazıcıdır (D-211): ajan elle satır eklemez, bu aracı çağırır.
`TESLIM_KAPISI` teslimden önce kontrol eder; kanıt üretilemiyorsa teslim
`blocked` olur (D-244 mantığı).
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: Veri satırının ilk alanı ISO tarih olmalı; başlık paragrafı ayırt edilir.
TARIH_DESEN = re.compile(r"^\d{4}-\d{2}-\d{2}\b")

#: Tek kanonik yol (D-220 Kural 1 — tür tablosunda "görev panosu" altında).
DEFLER = Path("data/orchestrator/bulgu_defteri.md")

BASLIK = """# Bulgu Defteri (D-67 · D-318)

**Tek kanonik dosya.** Ajan başına ayrı bulgu defteri yoktur ve açılmaz —
ölçüm: hiçbir ajan kendi defterini tutmuyor, ayrı defter ihtiyacı doğrulanmamış
varsayımdır (D-224). Dört ayrı defter olsaydı aynı bulgu dört yere yazılır,
karşılaştırması kaybolur ve ikiz yapı doğardı (D-211).

**Tek yazıcı:** `scripts/bulgu_defteri.py`. Elle satır eklenmez.

**Zorlayıcı:** `gorev_kutusu.py teslim` teslimden önce bu dosyada görev
`task_id`'sini arar; bulunamazsa teslim reddedilir (D-239: kural gövdesi tek
yerde, üretim komutu onu çağırır).

**Satır formatı (6 alan, borular):**

```
tarih | task_id | rol | renk | özet | karar
```

| Alan | Kural |
|---|---|
| `tarih` | `YYYY-AA-GG` |
| `task_id` | panodaki kanonik kimlik |
| `rol` | ajan kanonik adı (`ihsan` · `utku` · `salih` · `yasu`) |
| `renk` | 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri |
| `özet` | tek cümle; sayı varsa ölçülmüş sayı |
| `karar` | `görev:<ID>` · `D-NNN` · `kapandı:<kanıt>` · `red: <gerekçe>` |

**Karar sütunu boş bırakılmaz.** D-67: orkestratör her satırı üç seçenekten
biriyle işler — görev açar, karara bağlar, gerekçeyle reddeder. Boş satır
işlenmemiş bulgudur ve denetimde kırmızı yanar.
"""

#: Renk kodları — emoji yerine ASCII karşılık kullanılır (D-86 terminal cp1254).
RENKLER = {
    "acil": "🔴",
    "dikkat": "🟡",
    "tamam": "🟢",
    "oneri": "🔵",
}

#: Kanonik rol adları (D-33/D-60).
ROLLER = ("ihsan", "utku", "salih", "yasu")


# --- Yazıcı -----------------------------------------------------------------


def satir_birlestir(
    tarih: str, task_id: str, rol: str, renk: str, ozet: str, karar: str
) -> str:
    """Altı alanı tek satıra birleştirir; alan eksikse `ValueError`."""
    for ad, deger in (
        ("tarih", tarih), ("task_id", task_id), ("rol", rol),
        ("renk", renk), ("ozet", ozet), ("karar", karar),
    ):
        if not str(deger).strip():
            raise ValueError(f"bulgu satiri eksik alan: {ad}")

    r = renk.strip()
    # İsim ("dikkat") veya doğrudan emoji kabul edilir.
    if r in RENKLER:
        r = RENKLER[r]
    if r not in RENKLER.values():
        raise ValueError(f"gecersiz renk: {renk!r} (gecerli: {sorted(RENKLER)})")

    if rol.strip() not in ROLLER:
        raise ValueError(f"kanonik olmayan rol: {rol!r} (gecerli: {ROLLER})")

    ozet = " ".join(str(ozet).split())  # çok satırlı özet satır kırar
    karar = " ".join(str(karar).split())
    return f"{tarih} | {task_id} | {rol} | {r} | {ozet} | {karar}"


def _kilit_ac(dosya: Path, bekle_sn: float = 5.0):
    """Defter için süreçler arası kilit döndürür (context manager).

    Tek kanonik defter **dört ajan tarafından eşzamanlı** yazılır. Kilit
    olmadan oku-değiştir-yaz kalıbı kayıp güncellemeye açıktır: iki ajan aynı
    dosyayı okur, ikisi de kendi satırını ekler, **son yazan ilkini siler**
    (D-267'in "iki yol bir kaydı" deseninin dosya sürümü).

    Uygulama stdlib-only: `O_CREAT|O_EXCL` ile kilit dosyası, sonsuz döngü
    değil — `bekle_sn` sonunda `TimeoutError`. Kilit sahibi ölürse dosya kalır;
    bu yüzden kilit yaşı 60 sn üstüyse "sahipsiz" sayılıp alınır.
    """
    import contextlib
    import errno
    import os
    import time

    @contextlib.contextmanager
    def _cm():
        kilit = dosya.with_suffix(dosya.suffix + ".kilit")
        kilit.parent.mkdir(parents=True, exist_ok=True)
        son = time.monotonic() + bekle_sn
        sahipli = False
        while True:
            try:
                fd = os.open(kilit, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode("ascii"))
                os.close(fd)
                sahipli = True
                break
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                # Sahipsiz kilit: yaşı fazla büyükse al.
                try:
                    yas = time.time() - kilit.stat().st_mtime
                except OSError:
                    yas = 0.0
                if yas > 60:
                    try:
                        kilit.unlink()
                    except OSError:
                        pass
                    continue
                if time.monotonic() > son:
                    raise TimeoutError(
                        f"bulgu defteri kilitli: {kilit} ({yas:.0f} sn) — "
                        f"başka ajan yazıyor, {bekle_sn} sn beklenildi"
                    )
                time.sleep(0.05)
        try:
            yield
        finally:
            if sahipli:
                try:
                    kilit.unlink()
                except OSError:
                    pass

    return _cm()


def ekle(
    task_id: str,
    rol: str,
    ozet: str,
    karar: str,
    renk: str = "oneri",
    tarih: str | None = None,
    dosya: Path | None = None,
) -> str:
    """Bulgu satırı ekler. Aynı satır varsa **yok sayılır** (idempotent).

    Döner: yazılan satır ya da zaten var olan satır.
    """
    satir = satir_birlestir(
        tarih or date.today().isoformat(), task_id, rol, renk, ozet, karar
    )
    dosya = _coz(dosya)

    # Kilit **kontrol + yazma** ikisini de sarar; ayrı ayrı yapılırsa
    # ikisi arasındaki boşluk yine kayıp güncelleme penceresidir.
    with _kilit_ac(dosya):
        mevcut = dosya.read_text(encoding="utf-8") if dosya.exists() else BASLIK

        if satir in mevcut:
            return satir

        govde = mevcut.rstrip("\n")
        # Başlık/format bloğu korunur; satırlar en alta eklenir.
        dosya.parent.mkdir(parents=True, exist_ok=True)
        dosya.write_text(govde + "\n" + satir + "\n", encoding="utf-8")
    return satir


def _veri_satirlari(dosya: Path):
    """Yalnız **veri** satırları — `YYYY-AA-GG` ile başlayanlar.

    Defterin başlığı açıklama paragrafı, markdown tablosu ve kod bloğu içerir;
    bunlar boruya benzer ve sayımı bozuyordu (7 veri satırı varken 30 sayılıyordu).

    İki ayırıcı birlikte çalışır:
      1. ``` ile sınırlanan **kod bloğu** içindeki satırlar veri değildir —
         başlıktaki örnek satırın kendisi 6 alanlı ve geçerli görünürdü.
      2. Kalan satırlarda ilk alan ISO tarih olmalı; açıklama paragrafı ve
         markdown tablosu bu testten geçmez.
    """
    if not dosya.exists():
        return []
    sonuc = []
    kod_blokunda = False
    for satir in dosya.read_text(encoding="utf-8").splitlines():
        t = satir.strip()
        if t.startswith("```"):
            kod_blokunda = not kod_blokunda
            continue
        if kod_blokunda or not t:
            continue
        if TARIH_DESEN.match(t):
            sonuc.append(t)
    return sonuc


def eklenecek_mi(satir: str) -> bool:
    """Veri satırı biçimi geçerli mi: `tarih | task_id | rol | renk | özet | karar`."""
    alanlar = [a.strip() for a in satir.split("|")]
    if len(alanlar) != 6:
        return False
    if not TARIH_DESEN.match(alanlar[0]):
        return False
    if alanlar[2] not in ROLLER:
        return False
    if alanlar[3] not in RENKLER.values():
        return False
    return bool(alanlar[4]) and bool(alanlar[5])


def _coz(dosya: Path | None) -> Path:
    """`None` → kanonik defter.

    Varsayılan değer **fonksiyon tanımında bağlanırsa**, `DEFLER` çalışma
    anında değiştirilemez (test kapsamı, göçük yolu). Bu yüzden `None`
    kabul edilir ve çözümleme çağrı anında yapılır.
    """
    return DEFLER if dosya is None else dosya


def task_var_mi(task_id: str, dosya: Path | None = None) -> bool:
    """Verilen görev defterde geçiyor mu (teslim kapısı bunu çağırır)."""
    for satir in _veri_satirlari(_coz(dosya)):
        alanlar = [a.strip() for a in satir.split("|")]
        if len(alanlar) >= 2 and alanlar[1] == task_id:
            return True
    return False


def islenmemis(dosya: Path | None = None) -> list[str]:
    """`karar` alanı boş satırlar — orkestratör ihlali (denetim)."""
    sonuc = []
    for satir in _veri_satirlari(_coz(dosya)):
        alanlar = satir.split("|")
        if len(alanlar) >= 6:
            if not alanlar[-1].strip() or alanlar[-1].strip() == "-":
                sonuc.append(satir[:80])
        else:
            sonuc.append(f"ALAN SAYISI EKSİK ({len(alanlar)}): {satir[:60]}")
    return sonuc


def istatistik(dosya: Path | None = None) -> dict:
    """Defter özeti: görev sayısı, renk dağılımı, işlenmemiş satır."""
    renk: dict[str, int] = {}
    gorev: set[str] = set()
    veri = _veri_satirlari(_coz(dosya))
    for satir in veri:
        alanlar = [a.strip() for a in satir.split("|")]
        if len(alanlar) >= 2 and alanlar[1]:
            gorev.add(alanlar[1])
        if len(alanlar) >= 4 and alanlar[3]:
            renk[alanlar[3]] = renk.get(alanlar[3], 0) + 1
    return {
        "satir": len(veri),
        "gorev": len(gorev),
        "renk": renk,
        "islenmemis": len(islenmemis(dosya)),
    }


# --- CLI --------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Bulgu defteri (D-318 tek kanonik)")
    alt = ap.add_subparsers(dest="komut", required=True)

    p_ekle = alt.add_parser("ekle")
    p_ekle.add_argument("--task-id", required=True)
    p_ekle.add_argument("--rol", required=True, choices=ROLLER)
    p_ekle.add_argument("--ozet", required=True)
    p_ekle.add_argument("--karar", required=True)
    p_ekle.add_argument("--renk", default="oneri", choices=sorted(RENKLER))

    alt.add_parser("istatistik")
    alt.add_parser("islenmemis")

    args = ap.parse_args(argv)

    if args.komut == "ekle":
        satir = ekle(args.task_id, args.rol, args.ozet, args.karar, args.renk)
        print(f"KAYDEDILDI: {satir}")
        return 0

    if args.komut == "islenmemis":
        satirlar = islenmemis()
        if satirlar:
            print(f"D-67 IHLALI: {len(satirlar)} satir islenmemis")
            for s in satirlar:
                print(f"  - {s}")
            return 1
        print("Tum satirlar islenmis (karar alani dolu).")
        return 0

    st = istatistik()
    print(f"satir: {st['satir']} | farkli gorev: {st['gorev']} | "
          f"islenmemis: {st['islenmemis']}")
    for r, adet in sorted(st["renk"].items(), key=lambda x: -x[1]):
        print(f"  {r} {adet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
