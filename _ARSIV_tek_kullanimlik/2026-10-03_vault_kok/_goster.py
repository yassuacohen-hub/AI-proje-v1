import sys
sys.path.insert(0, r"c:\Huginn Data Projesi\Huginn Data Insights\scripts")
import notion_matris as m
print("=== SSOT Ilerleme Matrisi ===")
for x in m.ilerleme_satirlari():
    print(" | ".join([x["alan"].ljust(16), x["olcu"][:40].ljust(40), x["ilerleme"]]))
print()
print("=== Ajan Ilerlemesi ===")
for a in m.ajan_satirlari():
    print("  " + a["ajan"].ljust(7) + " toplam=" + str(a["toplam"]).ljust(3)
          + " calisiyor=" + str(a["calisiyor"]).ljust(3)
          + " onay=" + str(a["onay"]).ljust(3)
          + " plan=" + str(a["plan"]))