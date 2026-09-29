import re
import json
import pathlib
import datetime

HEDEF = pathlib.Path("data/kanit_448217_ilan_listesi.html")
CIKTI = pathlib.Path("data/kanit/448217_tobb_ilanlari.json")

ham = HEDEF.read_text(encoding="utf-8")

# Sunucu `charset=UTF-8` diyor ama govalli govdeyi cp1252 uzerinden
# bozmus olarak uretiyor. Bozukluk varsa geri cevir.
if "\u2500" in ham or "\u00c3" not in ham and "┤" in ham:
    duzeltilmis = ham.encode("cp1252", "ignore").decode("utf-8", "replace")
    if "┤" not in duzeltilmis:
        ham = duzeltilmis
        print("KODLAMA DUZELTILDI")
    else:
        print("KODLAMA DUZELTILEMEDI")
else:
    print("KODLAMA TEMIZ")

kayitlar = []
for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", ham, re.S):
    hu = [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", td)).strip()
        for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
    ]
    if len([x for x in hu if x]) < 7:
        continue
    g = re.search(r"Guid=([0-9a-f-]{36})", tr)
    pdf = re.search(r"tmp_gazete/([0-9a-f-]{36})\.pdf", tr)
    kayitlar.append(
        {
            "mudurluk": hu[0],
            "sicil_no": hu[1],
            "unvan": hu[2],
            "yayin_tarihi": hu[3],
            "sayi": hu[4],
            "sayfa": hu[5],
            "ilan_turu": hu[6],
            "ilan_guid": g.group(1) if g else None,
            "pdf_yolu": ("/tmp_gazete/%s.pdf" % pdf.group(1)) if pdf else None,
        }
    )

kanit = {
    "kanit_turu": "tobb_ticaret_sicili_ilan",
    "kaynak": "https://www.ticaretsicil.gov.tr",
    "erisim_yolu": "dogrudan TOBB uyesi (e-Devlet kullanilmadi)",
    "sorgu": {
        "SicilMudurluguId": "18 (ANKARA)",
        "TicSicNo": "448217",
        "Tarih1": "01.01.2026",
        "Tarih2": "02.01.2026",
    },
    "ilan_sayisi": len(kayitlar),
    "ilanlar": kayitlar,
    "pdf_metin_katmani": False,
    "not_pdf": "PDF taranmis gorsel; metin katmani YOK -> OCR gerekir",
    "toplanma_zamani": datetime.datetime.now().isoformat(timespec="seconds"),
}

CIKTI.parent.mkdir(parents=True, exist_ok=True)
CIKTI.write_text(json.dumps(kanit, ensure_ascii=False, indent=2), encoding="utf-8")

print("YAZILDI =", CIKTI, "| ilan =", len(kayitlar))
for k in kayitlar:
    print(
        "  %-8s %-11s %-6s %-5s %s"
        % (k["sicil_no"], k["yayin_tarihi"], k["sayi"], k["sayfa"], k["ilan_turu"][:50])
    )
