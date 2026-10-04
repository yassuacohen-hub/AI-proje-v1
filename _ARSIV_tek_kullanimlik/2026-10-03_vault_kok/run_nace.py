import sys
import os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import subprocess
result = subprocess.run([
    sys.executable, 
    "src/company_master/etl/nace_sozluk_yukle.py"
], env={**os.environ, "PYTHONIOENCODING": "utf-8"})
sys.exit(result.returncode)