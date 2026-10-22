import os, json
root = r'c:\Huginn Data Projesi'
# List top-level dirs
print("Top-level dirs:")
for item in os.listdir(root):
    full = os.path.join(root, item)
    if os.path.isdir(full):
        print(f"  {item}")
        # Check docs subdir
        docs = os.path.join(full, 'docs')
        if os.path.exists(docs):
            print(f"    docs exists, contents: {os.listdir(docs)[:30]}")
        # Check data dir
        data = os.path.join(full, 'data')
        if os.path.exists(data):
            print(f"    data exists")
            # Check orchestrator
            orch = os.path.join(data, 'orchestrator')
            if os.path.exists(orch):
                print(f"    orchestrator: {os.listdir(orch)[:30]}")