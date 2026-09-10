#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
lines = [l for l in open('data/aso/aso_full.jsonl', encoding='utf-8') if l.strip()]
recs = [json.loads(l) for l in lines]
print('ASO records:', len(recs))
has_ticaret = sum(1 for r in recs if r.get('ticaretSicilNo'))
print('With ticaretSicilNo:', has_ticaret)
for r in recs[:5]:
    print('  unvan:', r.get('unvan', '')[:50])
    print('  ticaretSicilNo:', r.get('ticaretSicilNo'))
    print('  naceKod:', r.get('naceKod'))
    print()
