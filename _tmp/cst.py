"""Durumu chate yaz, sonra her iki chat kanalini oku."""
import json
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
ISARET = "BEKLEME DURUMU"

sorun = ("BEKLEME: chat_gonder.py commit'i 3 denemede de pre-commit kancasinda "
         "takildi (~20dk). Dogrulanmadi - dusmus mu bilinmiyor.")
cozum = ("Ihtiyac: (1) git log -1 --stat + git status --short ile dogrula; "
         "(2) dustuyse OK, dusmediyse kanca neden donuyor? 3 kez zaman asimi "
         "yasadi, D-337'ye ragmen incelenmeli. D-338 teslim kapisi ise 0724b18b "
         "ve ce8d09aa ile COMMIT'LI ve dogrulandi: salih'e 10 engel -> 0, "
         "kirma kaniti 6/6, regresyon 38 passed 2 skipped.")

k = (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace")
if ISARET in k:
    print("[1] durum kaydi zaten var, ATLANDI")
else:
    sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
    from company_master import chat
    s = chat.ac(ajan="ihsan", task_id="ORCH-KIMLIK-ZINCIRI-01", sorun=sorun,
                cozum=cozum, kimden="yasu", onem="yuksek")
    print(f"[1] yazildi: {s['kimden']}->{s['ajan']} [{s['durum']}] onem={s['onem']}")
    print(f"    sorun {len(s['sorun'])}/200 | cozum {len(s['cozum'])}/300")

print()
print("=" * 70)
print("2) ajan-chat.jsonl — son 8 (D-192 gorev/sooru kanali)")
print("=" * 70)
sat = [json.loads(x) for x in
       (O / "ajan-chat.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
       if x.strip()]
print(f"toplam {len(sat)} kayit")
for r in sat[-8:]:
    print(f"  [{r.get('kimden'):>7s}->{r.get('ajan'):<7s}] {r.get('task_id'):<28s} "
          f"{r.get('durum'):<8s} :: {str(r.get('sorun'))[:62]}")

print()
print("=" * 70)
print("3) chat/messages.jsonl — son 8 (chat_gonder kanali)")
print("=" * 70)
m = O / "chat" / "messages.jsonl"
s2 = [json.loads(x) for x in m.read_text(encoding="utf-8", errors="replace").splitlines()
      if x.strip()]
print(f"toplam {len(s2)} kayit")
for r in s2[-8:]:
    print(f"  [{r.get('kimden'):>7s}->{r.get('kime'):<7s}] {str(r.get('task_id'))[:22]:<22s} "
          f"tur={str(r.get('tur'))[:8]:<8s} :: {str(r.get('mesaj'))[:58]}")

print()
print("=" * 70)
print("4) tur/mahiyet dolulugu (2. katman canli mi?)")
print("=" * 70)
dolu = sum(1 for r in s2 if r.get("tur") or r.get("mahiyet"))
print(f"  {dolu}/{len(s2)} kayit tur/mahiyet tasiyor")