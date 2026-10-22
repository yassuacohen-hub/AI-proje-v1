import re, pathlib
p = pathlib.Path(r"c:/Huginn Data Projesi/Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V9.html")
h = p.read_text(encoding="utf-8")
m = re.findall(r"<script>(.*?)</script>", h, re.S)
print("script blok:", len(m))
pathlib.Path(r"c:/Huginn Data Projesi/_tmp/v9_script.js").write_text("\n".join(m), encoding="utf-8")
ids = re.findall(r'id="([^"]+)"', h)
dup = {i for i in ids if ids.count(i) > 1}
print("tekrar id:", dup)
