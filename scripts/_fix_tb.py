path = 'C:/Projeler/Huginn Data Insights/src/company_master/orchestrator/task_board.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if i == 257:
        lines[i] = "                     f\"{(t.get('bitis') or '-')[:10]} |\")`n"
        break
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('done')
