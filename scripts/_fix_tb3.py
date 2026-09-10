path = "C:/Projeler/Huginn Data Insights/src/company_master/orchestrator/task_board.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("f\"| {t['task_id']} | {t['baslik']} | {t['sahip']} | {t.get('bitis', '-')} |\")", "f\"| {t['task_id']} | {t['baslik']} | {t['sahip']} | {(t.get('bitis') or '-')} |\")")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("fixed3")
