#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multi-OSB merger: combine OSTIM, ASO, and other OSB data."""
import json, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

# OSB data files
OSB_FILES = {
    "ostim": ROOT / "data" / "ostim" / "firmalar_detayli.jsonl",
    "aso": ROOT / "data" / "aso" / "aso_full.jsonl",
    "ivedik": ROOT / "data" / "ivedik" / "firmalar.jsonl",
    "baskent": ROOT / "data" / "baskent" / "firmalar.jsonl",
}

def load_osb_data():
    """Load all OSB data files."""
    all_records = []
    for osb, path in OSB_FILES.items():
        if not path.exists():
            print(f"Skip {osb}: {path} not found")
            continue
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except:
                        pass
        print(f"{osb}: {len(records)} records")
        for r in records:
            r["_osb"] = osb
        all_records.extend(records)
    return all_records

def normalize_name(name):
    """Normalize company name for matching."""
    if not name:
        return ""
    name = name.strip().upper()
    # Remove common suffixes
    suffixes = [" LTD. ŞTİ.", " LTD.ŞTİ.", " LTD.ŞTİ", " LTD. STI.", " LTD.STI.", 
                " A.Ş.", " A.S.", " ANONİM ŞİRKETİ", " ANONIM SIRKETI",
                " SAN. TİC. LTD. ŞTİ.", " SAN.TIC.LTD.ŞTİ.", " SAN. TIC. LTD. STI.",
                " TİCARET LİMİTED ŞİRKETİ", " TICARET LIMITED SIRKETI"]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()

def extract_vkn(record):
    """Extract VKN from record."""
    # Check vergi_no field
    vkn = record.get("vergi_no")
    if vkn and len(vkn) >= 10:
        return vkn
    # Check ticaretSicilNo (ASO)
    ticaret = record.get("ticaretSicilNo")
    if ticaret and len(ticaret) >= 10:
        return ticaret
    # Check unvan for VKN pattern
    unvan = record.get("unvan", "")
    import re
    m = re.search(r'\b(\d{10,11})\b', unvan)
    if m:
        return m.group(1)
    return None

def merge_records(records):
    """Merge records by VKN or normalized name."""
    # Group by VKN first
    vkn_groups = defaultdict(list)
    no_vkn = []
    
    for r in records:
        vkn = extract_vkn(r)
        if vkn:
            vkn_groups[vkn].append(r)
        else:
            no_vkn.append(r)
    
    print(f"VKN gruplari: {len(vkn_groups)}")
    print(f"VKN'suz kayit: {len(no_vkn)}")
    
    # Merge VKN groups
    merged = []
    for vkn, group in vkn_groups.items():
        best = merge_group(group)
        merged.append(best)
    
    # Group no-VKN by normalized name
    name_groups = defaultdict(list)
    for r in no_vkn:
        name = normalize_name(r.get("unvan", ""))
        if name:
            name_groups[name].append(r)
    
    print(f"İsim gruplari: {len(name_groups)}")
    
    for name, group in name_groups.items():
        best = merge_group(group)
        merged.append(best)
    
    return merged

def merge_group(group):
    """Merge a group of records for the same company."""
    # Prioritize by data completeness
    def score(r):
        s = 0
        if r.get("web_sitesi"): s += 3
        if r.get("adres"): s += 3
        if r.get("telefonlar"): s += 2
        if r.get("emailler"): s += 2
        if r.get("vergi_no") or r.get("ticaretSicilNo"): s += 2
        if r.get("naceKod") or r.get("sektor"): s += 1
        return s
    
    best = max(group, key=score)
    
    # Merge data from all records
    merged = dict(best)
    for r in group:
        if r.get("web_sitesi") and not merged.get("web_sitesi"):
            merged["web_sitesi"] = r["web_sitesi"]
        if r.get("adres") and not merged.get("adres"):
            merged["adres"] = r["adres"]
        if r.get("telefonlar") and not merged.get("telefonlar"):
            merged["telefonlar"] = r["telefonlar"]
        if r.get("emailler") and not merged.get("emailler"):
            merged["emailler"] = r["emailler"]
        if (r.get("vergi_no") or r.get("ticaretSicilNo")) and not (merged.get("vergi_no") or merged.get("ticaretSicilNo")):
            merged["vergi_no"] = r.get("vergi_no") or r.get("ticaretSicilNo")
        if r.get("naceKod") and not merged.get("naceKod"):
            merged["naceKod"] = r["naceKod"]
        if r.get("sektor") and not merged.get("sektor"):
            merged["sektor"] = r["sektor"]
    
    merged["_kaynaklar"] = [r.get("_osb") for r in group]
    return merged

def main():
    print("Multi-OSB merger basliyor...")
    
    # Load all data
    records = load_osb_data()
    print(f"Toplam kayit: {len(records)}")
    
    # Merge
    merged = merge_records(records)
    print(f"Birlestirilen firma: {len(merged)}")
    
    # Save result
    output_path = ROOT / "data" / "orchestrator" / "merged_companies.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    print(f"Sonuc kaydedildi: {output_path}")
    
    # Stats
    has_web = sum(1 for r in merged if r.get("web_sitesi"))
    has_adres = sum(1 for r in merged if r.get("adres"))
    has_tel = sum(1 for r in merged if r.get("telefonlar"))
    has_email = sum(1 for r in merged if r.get("emailler"))
    has_vkn = sum(1 for r in merged if r.get("vergi_no") or r.get("ticaretSicilNo"))
    has_nace = sum(1 for r in merged if r.get("naceKod") or r.get("sektor"))
    
    print(f"\nIstatistikler:")
    print(f"  Web: {has_web} ({has_web/len(merged)*100:.1f}%)")
    print(f"  Adres: {has_adres} ({has_adres/len(merged)*100:.1f}%)")
    print(f"  Telefon: {has_tel} ({has_tel/len(merged)*100:.1f}%)")
    print(f"  E-posta: {has_email} ({has_email/len(merged)*100:.1f}%)")
    print(f"  VKN: {has_vkn} ({has_vkn/len(merged)*100:.1f}%)")
    print(f"  NACE: {has_nace} ({has_nace/len(merged)*100:.1f}%)")

if __name__ == "__main__":
    main()
