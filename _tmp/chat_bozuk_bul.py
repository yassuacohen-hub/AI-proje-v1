# -*- coding: utf-8 -*-
import json
import sys

for i, s in enumerate(open(sys.argv[1], encoding="utf-8"), 1):
    if s.startswith(("<<<<<<<", ">>>>>>>", "=======")) or not s.strip():
        continue
    try:
        json.loads(s)
    except Exception as e:
        print(i, repr(s[:200]), e)
