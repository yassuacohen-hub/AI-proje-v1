import json, pathlib, datetime

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
p = KOK / "data" / "orchestrator" / "ajan-chat.jsonl"
once = len([l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()])

def yuzler(d):
    return sorted(x.relative_to(KOK).as_posix()
                  for x in d.rglob("*")
                  if x.is_file() and not x.read_bytes().endswith(b"\n")
                  and x.suffix in (".py", ".md", ".toml", ".yaml", ".yml"))

def bomlu(d):
    return sorted(x.relative_to(KOK).as_posix()
                  for x in d.rglob("*")
                  if x.is_file() and x.read_bytes().startswith(b"\xef\xbb\xbf")
                  and x.suffix in (".py", ".md", ".toml", ".yaml", ".yml"))

sonu = yuzler(KOK / "scripts") + yuzler(KOK / "tests")
bom = bomlu(KOK / "scripts") + bomlu(KOK / "tests")

mesaj = {
    "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
    "kimden": "orkestrator",
    "ajan": "hepsi",
    "task_id": "ORCH-KODLAMA-IHLAL-01",
    "sorun": ("KODLAMA DENETIMI: 9 dosyada ihlal var, SAHIPLERI BILINMIYOR. "
              "Dosyalar hicbir panoda goreve bagli degil, ajan belgelerinde adi gecmiyor. "
              "Bu yuzden kimseye tek tek atama yapilamadi. "
              "Kural: scripts/kodlama_denetim.py (KR-4). "
              "IHLAL turleri: son satir satir sonu (\\n) ile bitmiyor veya dosya UTF-8 BOM ile basliyor. "
              "DOSYA_SONU -> " + ", ".join(sonu) + ". "
              "UTF8_BOM -> " + (", ".join(bom) if bom else "(yok)") + "."),
    "cozum": ("Sahibi olan ajan dosyayi duzeltip commit'lesin. "
              "Sahiplik bilgisi yoksa AJAN_SAHIPLIK_BILINMIYOR diye cevap ver. "
              "Onarim tek satirlik: dosyanin sonuna satir sonu ekle."),
    "durum": "acik",
    "onem": "orta",
    "link": "scripts/kodlama_denetim.py",
}
with p.open("a", encoding="utf-8") as f:
    f.write(json.dumps(mesaj, ensure_ascii=False) + "\n")

sonra = len([l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()])
print("mesaj once:", once, "-> sonra:", sonra)
print("DOSYA_SONU sayisi:", len(sonu), "| BOM sayisi:", len(bom))