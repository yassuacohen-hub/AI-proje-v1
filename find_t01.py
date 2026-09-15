import json
with open("data/orchestrator/task_board.json", encoding="utf-8") as f:
    data = json.load(f)
def find(obj):
    if isinstance(obj, dict):
        if obj.get("id") == "T-01" or obj.get("task_id") == "T-01":
            print("=== FOUND T-01 ===")
            print(json.dumps(obj, ensure_ascii=False, indent=2))
            return True
        for k, v in obj.items():
            if find(v):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find(item):
                return True
    return False
if not find(data):
    print("T-01 NOT FOUND in task_board.json")
