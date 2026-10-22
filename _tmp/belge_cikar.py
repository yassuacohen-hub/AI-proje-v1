import re, zipfile, pathlib
Y = pathlib.Path("yedekler")
out = pathlib.Path("_tmp")
full = (Y / "güvenlik full.md").read_text(encoding="utf-8", errors="replace")
heads = [(i + 1, l.strip()[:160]) for i, l in enumerate(full.splitlines()) if l.lstrip().startswith("#")]
(out / "full_basliklar.txt").write_text("\n".join(f"{n}: {h}" for n, h in heads), encoding="utf-8")
z = zipfile.ZipFile(Y / "Altyapı alan adı pazarlama stratejimiz.docx")
xml = z.read("word/document.xml").decode("utf-8")
paras = [re.sub(r"<[^>]+>", "", p) for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)]
paras = [p.strip() for p in paras if p.strip()]
(out / "docx_metin.txt").write_text("\n".join(paras), encoding="utf-8")
print("full satir", len(full.splitlines()), "baslik", len(heads), "| docx paragraf", len(paras), "karakter", sum(map(len, paras)))
