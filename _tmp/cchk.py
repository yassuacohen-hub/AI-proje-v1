"""DUZELTME v2: yon + KAHIN'in tur/mahiyet semantigi (hash korumali)."""
import hashlib
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = KOK / "scripts" / "gorev_kutusu.py"

BEKLENEN = "9849e48a4b8a7dd7"          # canli olcum: duzeltme geri ALINMIS
ham = G.read_bytes()
gercek = hashlib.sha256(ham).hexdigest()[:16]
print(f"hash: {gercek} (beklenen {BEKLENEN})")
if gercek != BEKLENEN:
    print("!! dosya degismis, DOKUNULMADI")
    sys.exit(1)
txt = ham.decode("utf-8")

ESKI = '''def _mesaj_kontrol_et(task_id: str) -> list[str]:
    """messages.jsonl: task_id'ye bagli cevapsiz mesaj var mi (D-210 teslim kapisi).

    D-336 / ORCH-KIMLIK-ZINCIRI-01: chat.teslim_kontrol_et() yalnizca
    ajan-chat.jsonl'yi okur; chat_gonder.py'nin yazdigi messages.jsonl'yi
    gormuyordu. Bu yuzden bazi teslimler "acik soru var" diye reddedildi
    halbuki cevap messages.jsonl'deydi (ya da hic cevap yoktu, kapi bunu
    gormemisti). Ikisi artik birlikte kontrol edilir.
    """'''

YENI = '''def _mesaj_kontrol_et(task_id: str, ajan: str) -> list[str]:
    """task_id'ye bagli, teslimi BLOKLAYAN cevapsiz mesajlar (D-210 teslim kapisi).

    D-336 / ORCH-KIMLIK-ZINCIRI-01: chat.teslim_kontrol_et() yalnizca
    ajan-chat.jsonl'yi okur; chat_gonder.py'nin yazdigi messages.jsonl'yi
    gormuyordu. Ikisi artik birlikte kontrol edilir.

    D-338 (KAHIN teshisi, yasu tarafindan olculdu): onceki kosul yalnizca
    task_id + yanit_alindi kontrol ediyordu; mesajin KIMDEN gelip KIME
    gittigine ve ne tur olduguna hic bakmiyordu. Sonuc: salih'in ihsan'a
    GONDERDIGI raporlar (ALTYAPI-MIMIR-BAGLAM-01) salih'in KENDI teslimini
    blokluyordu - rapor, salih'e sorulan soru degil. Olculmus canli veri:
    o gorev icin salih'e 10 engel; 11 kayit kime==kimden (ihsan->ihsan).

    BLOKLAMA KURALI (iki katman, geriye donuk uyumlu):
      1) YON (her kayit icin gecerli, eski kayitlarda da):
         kime in (ajan, "hepsi")  -> mesaj bu ajana gelmis olmali
         kimden != ajan            -> kendi gonderdigin mesaj kendini bloklamaz
         Bu, _chat_yeni_mesajlar() ile ayni kalip.
      2) MAHIYET/TUR (chat_gonder.py'nin yazdigi yeni alanlar):
         mahiyet == "teslim_bloklayici"  -> bloklar (chat_gonder --blok)
         mahiyet == "bilgi"              -> bloklamaz (rapor/duyuru/bilgi)
         tur == "bilgi"                  -> bloklamaz (--rapor)
         mahiyet/tur YOKSA (147 eski kayidin tamami) -> yon kuralina bakilir.
      NOT: 'type' degil 'tur' yazilir; 'type' alani hic kullanilmaz.
    """'''

if ESKI not in txt:
    print("!! imza blogu bulunamadi, DOKUNULMADI")
    sys.exit(1)
txt = txt.replace(ESKI, YENI, 1)

ESKI_KOSUL = '''        if k.get("task_id") == task_id and not k.get("yanit_alindi"):
            nedenler.append(
                f"{str(k.get('mesaj', ''))[:120]} (kimden: {k.get('kimden', '?')}, chat_gonder)"
            )'''
YENI_KOSUL = '''        if k.get("task_id") != task_id or k.get("yanit_alindi"):
            continue
        kimden, kime = k.get("kimden"), k.get("kime")
        if kime not in (ajan, "hepsi"):
            continue          # baska birine gonderilmis - bu ajani ilgilendirmez
        if kimden == ajan:
            continue          # kendi mesajin kendi teslimini bloklamaz
        mahiyet = str(k.get("mahiyet") or "")
        tur = str(k.get("tur") or "")
        if mahiyet and mahiyet != "teslim_bloklayici":
            continue          # bilgi/rapor teslimi bloklamaz
        if tur == "bilgi":
            continue          # --rapor cikti, soru degil
        nedenler.append(
            f"{str(k.get('mesaj', ''))[:120]} (kimden: {kimden}, "
            f"tur: {tur or 'belirsiz'}, chat_gonder)"
        )'''
if ESKI_KOSUL not in txt:
    print("!! kosul blogu bulunamadi, DOKUNULMADI")
    sys.exit(1)
txt = txt.replace(ESKI_KOSUL, YENI_KOSUL, 1)

for a, b in [("mesaj_nedenleri = _mesaj_kontrol_et(args.task_id)",
              "mesaj_nedenleri = _mesaj_kontrol_et(args.task_id, args.ajan)")]:
    if a not in txt:
        print(f"!! cagri bulunamadi: {a}")
        sys.exit(1)
    txt = txt.replace(a, b, 1)

gecici = G.with_suffix(".py.tmp")
gecici.write_text(txt, encoding="utf-8")
gecici.replace(G)
print("YAZILDI")

import ast
src = G.read_text(encoding="utf-8")
ast.parse(src)
print("AST parse: OK")
print(f"yeni hash: {hashlib.sha256(G.read_bytes()).hexdigest()[:16]}")
for n, ln in enumerate(src.splitlines(), 1):
    if "_mesaj_kontrol_et" in ln and ("def " in ln or "args.ajan" in ln):
        print(f"  {n}: {ln.strip()[:80]}")