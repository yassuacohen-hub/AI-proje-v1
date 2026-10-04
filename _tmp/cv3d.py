"""Yanlis gorevi duzelt: V3 'acik' degil, asil bulgu ZORUNLU KAPI musteri verisini siliyor."""
import json
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TB = KOK / "data" / "orchestrator" / "task_board.json"
YENI = "ALTYAPI-ODIN-MASKE-V3-01"

v = json.loads(TB.read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v["gorevler"]
g = next((x for x in gs if x.get("id") == YENI), None)
print(f"onceki durum: {g.get('durum')} / ajan={g.get('ajan')}")
print(f"onceki aciklama (ilk 120): {str(g.get('aciklama'))[:120]}...")

g["baslik"] = "ODIN müşteri çıkış kapısı müşterinin KENDİ verisini siliyor"
g["aciklama"] = (
    "TASHİH (yasu olcumu, ilk aciklamam yanlitti): once 'V3 maskesiz, urun acigi' "
    "demistim. OLCUN SONUCU YANLISTIR. (1) genel_maske()'de kaynak='V3' icin "
    "bilincil 'return None' var; yorumu: 'V3 metinleri zaten maskeden gecmis "
    "musteri ciktisidir, tekrar maskelemeye gerek yok'. Yani V3 = MASKELENMIS, "
    "maskesiz degil. (2) 'V3' degeri tum kod tabaninda SADECE sunum.py:50'de "
    "geciyor; HICBIR cagiran kaynak='V3' gecirmiyor. Musteri endpoint'i henuz "
    "yazilmadi, yani canli bir sizinti yok. "
    "GERCEK BULGU TERS YONDE: docs/ODIN_DEPLOYMENT_ARCHITECTURE.md musteri "
    "endpoint'i icin cikis kapisini 'maskeleme_odin(metin, hedef=\"musteri\") "
    "ZORUNLU' olarak tanimliyor. O cagri kaynak vermedigi icin kaynak='' olur ve "
    "genel_maske TAM CALISIR: canli olcumde musterinin KENDI NACE kodu (74.90), "
    "VKN'si ve personel sayisi '[NACE MASKELENDI]' vb ile silindi. Yani dokumanin "
    "zorunlu kilavuzu uretime birakilirsa musteri kendi verisini goremez - bu "
    "bir URUTM REGRESYONU ve tam da V3='zaten maskelenmis' dalesinin var olma "
    "sebebi. IS: dokuman duzeltilsin - musteri endpoint'i ya kaynak='V3' ile "
    "cagirmali (veri tabanda zaten musteri_id ile filtreli, metin tekrar "
    "maskelenmemeli), ya da cikis kapisi 'veri kaynagi filtreli + metin maskesi "
    "YOK' olarak yeniden tanimlanmali. IKI SECENEKten BIRINI SEC, belki ikisini "
    "degil. KABUL: (a) musteri endpoint'i canli testte kendi NACE kodunu "
    "gosteriyor, (b) tests/test_odin_kacak_olcer.py gecer ve kacakli ic metin yine "
    "yakalaniyor, (c) ARCHITECTURE.md cikis kapisi satiri bu kararla uyumlu. "
    "BAGIMLILIK: ALTYAPI-ODIN-EGITIM-PIPELINE (utku) endpoint'i yaziyor. "
    "NOT: V3 dalini 'maskesiz oldugu icin' degistirme - bu musterinin kendi "
    "verisini maskeler ve urunu bozar. D-338 olcumu zaten bu tuzagi yakaliyor: "
    "k4_gecerli(kaynak='V3') -> guvenli=False, yani K4 sifir kacak beklemez."
)
g["onem"] = "yuksek"

gecici = TB.with_suffix(".json.tmp")
gecici.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
gecici.replace(TB)
print("\nyazildi")

v2 = json.loads(TB.read_text(encoding="utf-8"))
gs2 = v2 if isinstance(v2, list) else v2["gorevler"]
g2 = next(x for x in gs2 if x.get("id") == YENI)
print(f"DOGRULAMA: {g2['id']} | {g2['durum']} | {g2['ajan']}")
print(f"  baslik: {g2['baslik']}")
print(f"  aciklama uzunlugu: {len(g2['aciklama'])}")
print(f"  'ZORUNLU' geciyor mu: {'ZORUNLU' in g2['aciklama']}")
print(f"  'ilk aciklamam yanlitti' var mi: {'yanlitti' in g2['aciklama']}")
print(f"  pano toplam: {len(gs2)}")