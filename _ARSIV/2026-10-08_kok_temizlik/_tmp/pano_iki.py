import pathlib, json
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
d = json.load(open(R / "data/orchestrator/task_board.json", encoding="utf-8"))
hedef = ("VERI-OSB-MASTER-LISTE-01","API-V1-NETWORK-REPORT-01","API-PAKET-SCOPE-01","API-V1-COMPANY-FRAUD-01","VERI-ENTITY-GRAPH-01","VERI-UBO-ZINCIR-01")
out = []
for g in d:
    if isinstance(g, dict) and g.get("task_id") in hedef:
        out.append(f"{g.get('task_id'):30} | durum={g.get('durum'):10} | onc={g.get('oncelik')} | atanan={g.get('atanan')} | dep={g.get('bagimlilik') or g.get('dep') or g.get('depends') or []}")
text = "\n".join(out)
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\pano_iki.txt").write_text(text, encoding="utf-8")
