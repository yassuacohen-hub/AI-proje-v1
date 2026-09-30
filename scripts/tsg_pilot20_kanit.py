"""TSG-PILOT-20 — olcum sonuclarindan KANIT dosyalari uretir.

Brif kabul kriteri: kanit dosyalari `data/kanit/` altinda, anahtar bicimi
`kanit_anahtari()` uretimi (D-306 kanonik: ilan_sira_no-gazete_sayi-gazete_sayfa).

BU GOREV KOD YAZMAZ. Kanit KATMANI (skills/services/ticaret_sicili_kanit.py)
degistirilmez; burada yalnizca olcumde toplanan ham satir yazilir.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

KLASOR = KOK / "data" / "pilots" / "TSG-PILOT-20"
SONUC = KLASOR / "olcum_sonuc.json"
KANIT = KOK / "data" / "kanit"

KAYNAK = "https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php"

#: Sutun sirasi kaynaktan olculdu (D-306): Müdürlük|Sicil|Unvan|Yayın|Sayı|Sayfa|Tür|Gazete
BASLIK = ["mudurluk", "ticaret_sicil_no", "ticaret_unvani", "yayin_tarihi",
          "gazete_sayi", "gazete_sayfa", "tescil_edilen_husus", "gazete_adi"]


def hucre(r: list[str], i: int) -> str | None:
    """Eksik hucre None olur — bos string UYDURMA degildir (D-216)."""
    return r[i].strip() if i < len(r) and r[i].strip() else None


def main() -> None:
    veri = json.loads(SONUC.read_text(encoding="utf-8"))
    alinan = veri["zaman"]
    KANIT.mkdir(parents=True, exist_ok=True)
    yazilan, atlanan = 0, 0

    for k in veri["kayitlar"]:
        ilk = k.get("ilk_ilan")
        for j, anahtar in enumerate(k["kanit_anahtarlari"]):
            satir = ilk if j == 0 else None
            # Anahtar yalnizca sayi/sayfa uzerinden kurulur; ilk satirdan detay
            # tasinir, sonraki satirlar icin metin bilinmiyor olarak yazilir.
            if satir is not None:
                parca = satir[4].strip(), satir[5].strip()
                if f"{parca[0]}-{parca[0]}-{parca[1]}" != anahtar:
                    satir = None
            govde = {
                "ilan_sira_no": anahtar.split("-")[0],
                "icerik_no": None,
                "mersis_no": None,
                "ticaret_sicil_no": k["sicil_no"],
                "ticaret_unvani": satir[2] if satir else None,
                "adres": None,
                "mudurluk": satir[0] if satir else None,
                "yayin_tarihi": satir[3] if satir else None,
                "gazete_sayi": satir[4] if satir else None,
                "gazete_sayfa": satir[5] if satir else None,
                "tescil_tarihi": None,
                "tescil_edilen_husus": satir[6] if satir else None,
                "delil_belgeler": None,
                "il_turu": satir[6] if satir else None,
                "grup_anahtari": None,
                "iliskili_kayitlar": [],
                "guid": None,
                "katman": 0,
                "kaynak": KAYNAK,
                "alinma_zamani": alinan,
                "ham_metin": "",
                "dogrulama": {
                    "sonuc": "olculdu",
                    "bulgular": [
                        {"kod": "PILOT_OLCUM", "seviye": "bilgi",
                         "mesaj": "TSG-PILOT-20 olcumu; VKN/MERSIS bu turde "
                                  "kapanmadi (tabloda sutun yok)"},
                    ],
                    "turetilen": {"anahtar": anahtar},
                },
                "olcum": {"company_id": k["company_id"],
                          "sira": k["sira"],
                          "il_turu_ham": satir[6] if satir else None},
            }
            (KANIT / f"{anahtar}.json").write_text(
                json.dumps(govde, ensure_ascii=False, indent=2), encoding="utf-8")
            yazilan += 1
        atlanan += 0

    print(f"kanit yazildi : {yazilan}")
    print(f"dizin         : {KANIT}")
    print(f"olcum zamani  : {veri['zaman']}")


if __name__ == "__main__":
    main()
