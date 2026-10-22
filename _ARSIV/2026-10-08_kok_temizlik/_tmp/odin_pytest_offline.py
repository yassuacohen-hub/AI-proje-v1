"""Offline pytest: evren_anahtari bos -> hakem aga gitmez (kanit: mandal agsiz calisir mi)."""
import sys, time
from pathlib import Path
R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.path.insert(0, str(R / "scripts"))
import odin_prompt_injection_test as mod
_orig = mod.evren_anahtari
# yalniz hakemin argumansiz cagrisi bos doner; test_anahtar_9router gercek fonksiyonu kullanir
mod.evren_anahtari = lambda *a, **k: "" if not a and not k else _orig(*a, **k)
import pytest
t0 = time.time()
rc = pytest.main(["-q", "-p", "no:cacheprovider", "-p", "no:randomly",
                  str(R / "tests/test_odin_prompt_injection.py")])
print(f"RC={rc} SURE={time.time()-t0:.1f}s")
sys.exit(rc)
