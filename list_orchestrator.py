import os
d = r'c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator'
for f in sorted(os.listdir(d)):
    filepath = os.path.join(d, f)
    if os.path.isfile(filepath):
        print(f"{os.path.getsize(filepath):10d}  {f}")
    else:
        print(f"  <DIR>    {f}")