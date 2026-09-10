path = "C:/Projeler/Huginn Data Insights/src/company_master/orchestrator/task_board.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("[:10]} |\")`n    if handoffs:", "[:10]} |\")\n    if handoffs:")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("fixed")
