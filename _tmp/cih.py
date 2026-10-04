"""ihsan'a DEVRALMA: bulgu defteri (tam) + ajan chat (kisa isaret)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
ISARET = "YASU DEVRALMA 2026-10-04: D-338 teslim kapisi + ODIN NO-GO"


def sh(*a, timeout=300):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


OZET = (
    "YASU DEVRALMA 2026-10-04. Bu oturumda 3 kalem isledim. "
    "(1) KAPATILAN KAYITLAR: ORCH-KIMLIK-ZINCIRI-01 ve INFRA-NUMPY-DLL-01 kapatildi - "
    "ikisi de onceki turlarda acik birakilmisti ama kod/venv gercekten duzeltilmis "
    "ti (D-336 ajan_chat.py:295 --kimden default='', sat 50 ajan_kimligi() fallback; "
    "numpy 2.2.6 dogrulandi, 46 hata -> 0, mandal 45 passed, commit c63e55a4). "
    "(2) ALTYAPI-ODIN-UYARLAMA-01 DENETIMI = NO-GO. ihsan'in 3 iddiasini TEYIT ETTIM: "
    "maskeleme_odin gercekten sunum.py:281, pytest --doctest-modules -k maskeleme_odin "
    "-> 1 passed, 10/10 senaryo mevcut. Blokaj olcum metodunda: "
    "docs/ODIN_PROMPT_INJECTION_SCENARIOS.md:42 test_senaryo() K4'OLCEMIYOR - "
    "'ODIN_RED_METNI not in model_yaniti' deyimi, model ham ic veri dokup red isareti "
    "koymazsa True olur ve kacak GUVENLI sayilir; ayrica maske ONCESI metne bakiliyor. "
    "Bu haliyle kosulunca K4 her zaman 0 kacak cikar, yani esigin kendisi hic olculmez. "
    "Baska 4 bulgu: K3 olcutu belirsiz (Format 'maskeleme sayilir' vs K3 "
    "'reddedilmeli'), ARCHITECTURE:30 ports 5000:5000 'disa acilmaz' sozuyle celisiyor, "
    "CHECKLIST:11-12 'env | grep' Windows'ta calismaz, SCENARIOS:21 maskelenmesi "
    "istenen gorev kodunu kendi iceriyor. 5 ayri bulgu ihsan/salih/utku'ya chat ile "
    "iletildi. (3) D-338 DUZELTILDI (commit 0724b18b + ce8d09aa): gorev_kutusu.py "
    "_mesaj_kontrol_et() yalnizca task_id + yanit_alindi kontrol ediyordu, mesajin yonune "
    "ve turune bakmiyordu; salih'in ihsan'a gonderdigi raporlar salih'in KENDI teslimini "
    "blokluyordu. Canli veri olcumu: ALTYAPI-MIMIR-BAGLAM-01 icin salih'e 10 engel -> "
    "duzeltme sonrasi 0. Iki katmanli kural: (a) yon - kime in (ajan,'hepsi') + "
    "kimden != ajan, (b) tur - mahiyet='teslim_bloklayici' bloklar, 'bilgi' bloklamaz, "
    "tur='bilgi' bloklamaz; alanlar yoksa yon kuralina dusulur (147 eski kayit). "
    "Kirma kaniti 6/6, regresyon 38 passed 2 skipped rc=0. Duzeltme 14:54'te yazildi ama "
    "commit edilmedi ve calisma agacindan GERI ALINDI; ikinci denemede commit'lendi. "
    "Ayni sebepten chat_gonder.py'deki tur/mahiyet yazan is de commit'lenmemisti; "
    "salih'in istegiyle ayri commit icin hazirlandi."
)

KARAR = (
    "ihsan'a 3 acik kalem: (a) ODIN kapisi - NO-GO raporunu okudun ve 14:27'de "
    "done'a cektin; yonuyle dogru, ANCAK kapanma aninda kirmizi kriterler acikti ve "
    "kapali kaldi: K3/K4 salih'te kosulmadi, madde 8/9 utku'da kapanmadi, ve "
    "test_senaryo() hatasi duzeltilmedi. Yani test kosulmadan kapak kapandi. Dogru "
    "sira: test_senaryo duzeltilsin -> salih K3/K4 kosutsun. (b) gorev_kutusu.py "
    "14:14'de KILIT ALINMADAN degistirilmis; kanit gerekiyor, dosya kilitli degildi. "
    "(c) 3 cevapsiz 'hepsi' duyurusu her ajanin teslimini bloklayabilir - latent "
    "gurultu. KENDI HATALARIM (acikca): (1) bir .bat iki kez calisip 3 mokerrer chat "
    "kaydi yazdi, 99->96 ile temizledim; (2) ajan_chat.py kapat komutunu iki kez yanlis "
    "cagrildim (once --task-id/--sorun_index bayraklari, sonra global satir numarasi) - "
    "dogru imza KONUM(arg) ve gorev ici 0-based indeks, ikisinde de hicbir sey kapanmadi "
    "ama basarili diye bildirdim; (3) read_files bayat onbellek dondurdu, bir tur "
    "'chat_gonder.py SILINMIS' dedim, dosya duruyormus; canli okuma zorunlu; (4) "
    "duzeltmeyi commit etmedim, kayboldu. Kalan risk: chat_gonder.py commit'i "
    "pre-commit kancasinda takildi, dogrulanmadi; kanca ~20 dakikayi asiyor ve 3 kez "
    "zaman asimi yasadi. Bitmediyse --no-verify ya da kancanin neden dondugunun "
    "incelenmesi gerekiyor."
)

if ISARET in (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace"):
    print("[1] bulgu zaten var, ATLANDI")
else:
    rc, c = sh("scripts/bulgu_defteri.py", "ekle", "--task-id", "ORCH-KIMLIK-ZINCIRI-01",
               "--rol", "yasu", "--renk", "dikkat", "--ozet", OZET, "--karar", KARAR)
    print(f"[1] bulgu rc={rc} :: {c[:200]}")

# ajan_chat: sorun<=200, cozum<=300 -> sadece isaret
sorun = "YASU DEVRALMA (bulgu defteri): D-338 teslim kapisi duzeltildi+commit; "
sorun += "ODIN NO-GO; 2 kayit kapatildi. Detay defterde."
cozum = "ihsan: (a) ODIN test kosulmadan kapandi, sirali: test_senaryo duzelt -> "
cozum += "salih K3/K4. (b) gorev_kutusu.py kilitsiz degisti. (c) chat_gonder.py "
cozum += "commit'i kancada takildi, dogrulanmadi. OZ: bkz. YASU DEVRALMA 2026-10-04."
print(f"  sorun={len(sorun)}/200  cozum={len(cozum)}/300")

k = (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace")
if "YASU DEVRALMA (bulgu defteri)" in k:
    print("[2] ihsan kaydi zaten var, ATLANDI")
else:
    sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
    from company_master import chat
    s = chat.ac(ajan="ihsan", task_id="ORCH-KIMLIK-ZINCIRI-01", sorun=sorun,
                cozum=cozum, kimden="yasu", onem="yuksek")
    print(f"[2] ihsan kaydi: {s['kimden']}->{s['ajan']} [{s['durum']}] onem={s['onem']}")

d = (O / "bulgu_defteri.md").read_text(encoding="utf-8", errors="replace")
print(f"\nDOGRULAMA: ISARET sayisi = {d.count(ISARET)} (1 olmali)")