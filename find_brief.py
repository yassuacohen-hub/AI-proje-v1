from pathlib import Path
plans_dir = Path("plans")
if not plans_dir.exists():
    print("plans dir not found")
else:
    matches = [p for p in plans_dir.glob("*.md") if "T-01" in p.read_text(encoding="utf-8")]
    for p in matches:
        text = p.read_text(encoding="utf-8")
        print("--- " + str(p) + " ---")
        print(text[:1000])
        print()
    if not matches:
        print("No T-01 reference found in plans/*.md")
