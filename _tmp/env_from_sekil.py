# -*- coding: utf-8 -*-
"""SMTP_FROM / ADMIN_EMAIL sekil kontrolu (deger yazdirmaz)."""
E = {}
for ln in open(r"c:\Huginn Data Projesi\Huginn Data Insights\.env", encoding="utf-8-sig"):
    if "=" in ln and not ln.startswith("#"):
        k, _, v = ln.partition("=")
        E[k.strip()] = v.strip().strip('"').strip("'")
for ad in ("SMTP_FROM", "ADMIN_EMAIL", "SMTP_USER"):
    v = E.get(ad, "")
    print(ad, "| uzunluk", len(v), "| @ var", "@" in v, "| <> var", "<" in v, "| bosluk var", " " in v)
