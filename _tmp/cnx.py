"""1) ihsan'a TASHIH (geri cekilen bulgu)  2) pano + chat kontrolu"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
ISARET = "TASHIH D-338: V3 bulgusu geri cekildi, asil bulgu zorunlu kapida"


def sh(*a, timeout=300):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


if ISARET in (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace"):
    print("[1] tashih zaten var, ATLANDI")
else:
    rc, c = sh("scripts/bulgu_defteri.py", "ekle", "--task-id",
               "ALTYAPI-ODIN-UYARLAMA-01", "--rol", "yasu", "--renk", "acil",
               "--ozet",
               "TASHIH: 'ODIN musteri endpoint'i (V3) maskelemesiz' bulgumu GERI "
               "CEKTIYOM. Olcum yanltti. (1) sunum.py genel_maske()'de kaynak='V3' "
               "icin BILINCLI 'return None' var; yorumu 'V3 metinleri zaten "
               "maskeden gecmis musteri ciktisidir'. Yani V3 maskesiz degil, "
               "maskelenmis. (2) 'V3' degeri tum kod tabaninda SADECE sunum.py:50'de "
               "geciyor; HICBIR cagiran yok, musteri endpoint'i henuz yazilmadi, "
               "canli sizinti yok. Bu yuzden acilacak ALTYAPI-ODIN-MASKE-V3-01 "
               "gorevi yeniden yazildi: 'V3'te maskeyi acmak bir URUM "
               "REGRESYONU olurdu.",
               "--karar",
               "GERCEK BULGU TERS YONDE: ARCHITECTURE.md musteri endpoint'i icin "
               "cikis kapisini maskeleme_odin(metin, hedef='musteri') ZORUNLU "
               "tanimliyor. O cagri kaynak vermedigi icin kaynak='' olur ve genel "
               "maske tam calisir. Canli olcum: musterinin KENDI NACE kodu 74.90, "
               "VKN 1234567890 ve personel sayisi 45 -> '[NACE MASKELENDI]' vb "
               "ile silindi. Dokumanin zorunlu kilavuzu uretime birakilirsa "
               "musteri kendi verisini goremez. V3 dali ('zaten maskelenmis') de "
               "tam bu yuzden var: veri tabanda musteri_id ile filtreli. ihsan'a "
               "onerim: ARCHITECTURE.md cikis kapisi satiri ya 'kaynak=V3 ile "
               "cagir' ya da 'veri kaynagi filtreli + metin maskesi YOK' olarak "
               "yeniden tanimlansin. Kapsam: bu bir tasarim karari, yasu "
               "dayatmadi. D-338 zaten tuzagi yakaliyor - k4_gecerli(kaynak='V3') "
               "-> guvenli=False, yani endpoint yazilsa bile V3 maskesiz kalirsa "
               "K4 gecemez; ayri kod degisikligi gerekmiyor.")
    print(f"[1] tashih rc={rc} :: {c[:180]}")

k = (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace")
if "TASHIH: V3 bulgumu geri" in k:
    print("[2] ihsan kaydi zaten var, ATLANDI")
else:
    sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
    from company_master import chat
    s = chat.ac(ajan="ihsan", task_id="ALTYAPI-ODIN-UYARLAMA-01",
                sorun="TASHIH: V3 bulgumu geri cektim. V3 zaten maskelenmis "
                      "(bilincil return None), hicbir cagir yok, canli sizinti yok.",
                cozum="ASIL BULGU: ARCHITECTURE.md'deki ZORUNLU musteri cikis kapisi "
                      "kaynak vermedigi icin tam maske calistiriyor -> musterinin "
                      "KENDI NACE/VKN'si siliniyor. Dokuman duzeltilmeli "
                      "(kaynak=V3 ile cagir, ya da metin maskesi YOK de). Gorev: "
                      "ALTYAPI-ODIN-MASKE-V3-01 yeniden yazildi.",
                kimden="yasu", onem="yuksek")
    print(f"[2] {s['kimden']}->{s['ajan']} [{s['durum']}] onem={s['onem']}")
    print(f"    sorun {len(s['sorun'])}/200 | cozum {len(s['cozum'])}/300")

print()
print("=" * 66)
print("3) PANO — benim acik kalan / yeni var mi?")
print("=" * 66)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v["gorevler"]
for g in gs:
    if g.get("durum") in ("yeni", "atanmis") or g.get("ajan") == "yasu" and \
            g.get("durum") in ("aktif", "devam"):
        print(f"  [{g.get('durum'):8s}] {g.get('id')} ajan={g.get('ajan')}")
say = {}
for g in gs:
    say[g.get("durum")] = say.get(g.get("durum"), 0) + 1
print(f"  pano: {say}")

print()
print("=" * 66)
print("4) CHAT — acik kayitlarim")
print("=" * 66)
sat = [json.loads(x) for x in
       (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
       if x.strip()]
for r in sat:
    if r.get("kimden") == "yasu" and r.get("durum") == "acik":
        print(f"  -> {r.get('ajan'):<7s} {r.get('task_id'):<28s} onem={r.get('onem')}")
print(f"  toplam acik: {sum(1 for r in sat if r.get('kimden')=='yasu' and r.get('durum')=='acik')}")