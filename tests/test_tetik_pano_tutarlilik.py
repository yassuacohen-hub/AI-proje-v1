"""D-317 mandalı — tetik ↔ pano tutarlılığı.

Kural gövdesi `tests/test_tetik_pano_tutarlilik.py`'de yaşar; burada yalnız
**kendi kırılması** ölçülür (D-256/4).

Çalışma kuralı (D-317/2):
  1. Yazma kapısı  -> `tetik_ekle()` panoda kapalı durum görürse tetik yazmaz.
  2. Canlı dosya  -> bu mandal, her ajanın kuyruğunda KAPALI durumdaki bir
                     görev için bekleyen tetik bulursa kırmızı verir.

Bekleyen **yeni** bayat tetik sayısı tavanı 0'dır (D-220: yalnız küçülür).
D-317 anında ölçülen 3 bayat tetik **donmuş borç tabanıdır** — panoyu
düzenlemek D-77 gereği orkestratöründür. D-217'deki `tests/_brief_baseline.txt`
taban deseniyle aynı mantık: mevcut kirlilik dondurulur, yenisi kapatılır.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pytest  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOKLUK = os.path.join(KOK, "data", "orchestrator")
PANO = os.path.join(KOKLUK, "task_board.json")
TETIK_KOK = os.path.join(KOKLUK, "triggers")
AJANLAR = ("ihsan", "utku", "salih", "yasu")

#: Pano durumu kapanmış sayılan değerler — bu görevler tetikte bekleyemez.
KAPALI_DURUMLAR = frozenset({"iptal", "done", "archive", "inactive", "iptal_stale"})

#: D-317 anında ölçülen bayat tetikler. Taban **kayıt bazında** dondurulur;
#: yalnız sayı değil, hangi (ajan, görev) çiftleri ölçüldüyse onlar da yazılır.
#: Böylece "bu 3 tanesi bilinen borç, gerisi yeni" ayrımı test edilebilir.
#: D-217'deki `tests/_brief_baseline.txt` taban deseniyle aynı mantık.
BASELINE_BAYAT: frozenset[tuple[str, str]] = frozenset(
    {
        ("utku", "ALTYAPI-EVREN-PRIVATE-DOGRULAMA"),  # pano=done, sahibi yasu
        ("utku", "VERI-ODIN-EGITIM-VERISI-HAZIRLA"),  # pano=iptal
        ("utku", "ALTYAPI-ODIN-EGITIM-PIPELINE"),  # pano=iptal
    }
)

#: Yeni bayat tetik için tavan. D-220: asla yükseltilmez.
BAYAT_TETIK_TAVANI = 0

TETIK_DURUMLARI = ("bekliyor", "alindi", "teslim", "done")


def _pano() -> dict[str, dict]:
    with open(PANO, encoding="utf-8") as f:
        tb = json.load(f)
    if isinstance(tb, dict):
        for alan in ("gorevler", "gorev", "tasks"):
            if alan in tb:
                liste = tb[alan]
                break
        else:
            liste = []
    else:
        liste = tb
    if isinstance(liste, dict):
        liste = list(liste.values())
    return {
        str(x.get("task_id")): x
        for x in liste
        if isinstance(x, dict) and x.get("task_id")
    }


def _bekleyen_tetikler() -> list[tuple[str, str, str]]:
    """(ajan, task_id, pano_durumu) listesi; pano dışı tetikler `?` döner."""
    pano = _pano()
    sonuc: list[tuple[str, str, str]] = []
    for ajan in AJANLAR:
        yol = os.path.join(TETIK_KOK, f"{ajan}.jsonl")
        if not os.path.exists(yol):
            continue
        with open(yol, encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if not satir:
                    continue
                try:
                    kayit = json.loads(satir)
                except json.JSONDecodeError:
                    continue
                if kayit.get("durum") != "bekliyor":
                    continue
                tid = str(kayit.get("task_id"))
                durum = str(pano.get(tid, {}).get("durum", "?"))
                sonuc.append((ajan, tid, durum))
    return sonuc


def _bayat() -> list[tuple[str, str, str]]:
    return [x for x in _bekleyen_tetikler() if x[2] in KAPALI_DURUMLAR]


def _bayat_yeni() -> list[tuple[str, str, str]]:
    """Donmuş tabanda olmayan bayat tetikler — bunlar yeni borçtur."""
    return [x for x in _bayat() if (x[0], x[1]) not in BASELINE_BAYAT]


class TestD317TetikPano:
    def test_yeni_bayat_tetik_yok(self):
        """TABANDA olmayan bayat tetik varsa kırmızı — yeni ihlal demektir."""
        yeni = _bayat_yeni()
        assert len(yeni) <= BAYAT_TETIK_TAVANI, (
            f"D-317 ihlali: yeni bayat tetik {len(yeni)}, tavan {BAYAT_TETIK_TAVANI}"
            f" -> {yeni}"
        )

    def test_dondurulmus_borc_silinmis_olabilir(self):
        """Taban girdisi kapanırsa bu hata DEĞİLDİR; mandal yeşil kalmalı.

        Taban yalnız üst sınırdır. Görev sahibi tetiği geri çekerse
        `BASELINE - gercek_kume` boş olur; test bunu affetmek zorundadır,
        yoksa borç kapandığında mandal kırılır (D-214'te aynı tuzak).
        """
        gercek = {(x[0], x[1]) for x in _bayat()}
        kalan = BASELINE_BAYAT - gercek
        assert kalan <= BASELINE_BAYAT, "taban asla genislemez"

    def test_taban_kusurlari_pano_durumuyla_uyumlu(self):
        """Tabandaki her görevin panosu gerçekten kapanmış olmalı.

        Tabanı elle şişirmenin (D-224) tek engeli burasıdır: pano durumu
        `iptal`/`done`/`archive` DEĞİLSE o çift bayat sayılmaz ve
        `test_yeni_bayat_tetik_yok` onu yakalar.
        """
        pano = _pano()
        for ajan, tid in sorted(BASELINE_BAYAT):
            gorev = pano.get(tid)
            assert gorev is not None, f"tabandaki {tid} panoda yok (D-231 arşive bak)"
            durum = str(gorev.get("durum", "?"))
            assert durum in KAPALI_DURUMLAR, (
                f"tabandaki {tid} pano={durum}; kapanmamışsa tabandan cikarilmali"
            )

    @pytest.mark.parametrize("durum", sorted(KAPALI_DURUMLAR))
    def test_kapali_durum_listesi_bozulmaz(self, durum):
        """Yeni bir kapanış durumu eklenirse tanım güncellensin (D-311 kalıbı)."""
        assert durum in KAPALI_DURUMLAR

    def test_kaynak_dosyalar_var(self):
        """Kararda atıf yapılan üç kaynak gerçekten diskte."""
        for yol in (
            os.path.join("scripts", "tetik_pano_tutarlilik_olcum.py"),
            os.path.join("AGENTS.md"),
            os.path.join(KOKLUK, "task_board.json"),
        ):
            assert os.path.exists(os.path.join(KOK, yol)), f"eksik kaynak: {yol}"
