import pathlib
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
mig = sorted(p.name for p in R.glob("src/company_master/schema/migrations/*.sql"))
out = []
out.append("SON_GOC " + str(mig[-3:]))
out.append("0060_VAR " + ("x" if (R/"src/company_master/schema/migrations/0060_osb_master_15.sql").exists() else "y"))
out.append("0047_VAR " + ("x" if (R/"src/company_master/schema/migrations/0047_entity_graph.sql").exists() else "y"))
routers = R/"src/company_master/api/routers"
out.append("ROUTERS " + (str([p.name for p in routers.glob("*.py")]) if routers.exists() else "YOK"))
seed = R/"src/company_master/seed"
out.append("SEED " + (str([p.name for p in seed.glob("*.py")]) if seed.exists() else "YOK"))
api = R/"src/company_master/api"
out.append("API_DOSYA " + (str([p.name for p in api.glob("*.py")]) if api.exists() else "YOK"))
for rel in ["src/company_master/api/scope.py","src/company_master/api/rate_limiter.py","src/company_master/engine/source_registry.py","web_app.py","src/company_master/schema/companies.sql"]:
    out.append(("VAR " if (R/rel).exists() else "YOK ") + rel)
text = "\n".join(out)
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\olcum_sonuc.txt").write_text(text, encoding="utf-8")
