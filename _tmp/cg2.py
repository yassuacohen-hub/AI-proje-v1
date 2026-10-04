"""chat_gonder.py AYRI commit (yalnizca bu dosya)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*a, timeout=1200):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


rc, c = git("add", "--", "scripts/chat_gonder.py")
print(f"[add] rc={rc} {c[:80]}")

rc, staged = git("diff", "--cached", "--stat")
print(f"\n[staged]\n  " + (staged or "(bos)").replace("\n", "\n  "))
if "chat_gonder.py" not in staged or staged.count(".py") != 1:
    print("!! beklenmedik staged icerik -> COMMIT ATLANDI")
    sys.exit(1)

mesaj = (
    "feat(chat_gonder): tur/mahiyet alanlari, cevap_index takibi, YESIL/red "
    "gosterimi (D-338)\n\n"
    "Bu dosya commit'lenmemis duruyordu; salih'in istegiyle ayri commit olarak\n"
    "sabitleniyor. Ayni sebepten D-338 teslim kapisi duzeltmesi de iki kez calisma\n"
    "agacindan geri alinmisti - commit'lenmemis is kayboluyor.\n\n"
    "Icerik:\n"
    "  - cevap_index: mesaj gonderdiginde onceki bekleyen mesajin indeksi\n"
    "    yaziliyor; 'sana gelen mesajlari gor' cikti boyle cozuluyor\n"
    "  - kimlik zinciri: ajan_kimligi() + HUGINN_AJAN fallback'i tek kaynak\n"
    "  - tur / mahiyet: her mesaja yaziliyor. mahiyet='teslim_bloklayici' yalnizca\n"
    "    --blok ile; --rapor tur='bilgi'. gorev_kutusu._mesaj_kontrolet() bu\n"
    "    alanlari 2. katman olarak okuyor (0724b18b)\n"
    "  - YESIL/kirmizi sonuc gosterimi + --tur/--mahiyet argumanlari\n"
    "  - tarih alani: eski kayitlara geriye donuk tamamlama\n\n"
    "Uyum notu: bu commit'ten once messages.jsonl'deki 147 kaydin 0'i tur/mahiyet\n"
    "tasiyor. Bu yuzden 2. katman bugune kadar olu koddu ve kapi 1. katman\n"
    "(yon) ile calisti. Bu commit'ten sonra yeni mesajlar alanlari doldurur.\n\n"
    "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
)
rc, c = git("commit", "-m", mesaj)
print(f"\n[commit] rc={rc}")
print("  " + c.replace("\n", "\n  ")[:1200])

rc, c = git("log", "--oneline", "-4")
print(f"\n[log]\n  " + c.replace("\n", "\n  "))

rc, c = git("status", "--short")
print(f"\n[calisma agaci] {c or '(temiz)'}")
rc, c = git("show", "--stat", "HEAD")
print(f"\n[HEAD]\n  " + c[:400].replace("\n", "\n  "))