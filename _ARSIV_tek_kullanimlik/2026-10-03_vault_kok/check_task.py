import json
with open('C:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    board = json.load(f)
for task in board:
    if 'NACE-COKLU' in task.get('id', ''):
        print(f"ID: {task['id']}")
        print(f"Durum: {task.get('durum')}")
        print(f"Sahip: {task.get('sahip')}")
        print(f"Baslik: {task.get('baslik')}")
        print(f"Not: {task.get('not', '')}")