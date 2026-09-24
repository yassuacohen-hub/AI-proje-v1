# -*- coding: utf-8 -*-
"""P4-5: Duplicate temizleme (merge + delete).

Strateji:
  A) Unvan duplicate: normalize unvani ayni olanlar -> en yuksek skorlu "kazanan" tutulur,
     kazananin bos alanlari kaybedenden doldurulur, kaybeden silinir.
  B) VKN duplicate: ayni VKN'yi tasiyanlar. Tercih: tasfiye("TASF") icermeyen kayit.
  C) Web duplicate: PORTAL domainler duplicate DEGIL -> islem yapilmaz (report-only).

Guvenlik:
  - Varsayilan DRY-RUN. Uygulamak icin: --apply
  - Tek transaction; hata olursa tam geri alinir.
  - Tum islemler logs/dedup_audit_*.csv dosyasina yazilir.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine

MERGE_FIELDS = ["trade_name", "tax_number", "vergi_no", "website_domain",
                "primary_phone", "primary_email", "nace_code", "osb_parsel", "adres"]

_TR = str.maketrans({'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'ı': 'I'})


def norm_name(s: str) -> str:
    if not s:
        return ""
    s = s.upper().translate(_TR)
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    for suffix in ('ANONIM SIRKETI', 'LIMITED SIRKETI', 'LTD STI', 'LIMITED', 'LTD',
                   'ANONIM', 'A S', 'AS', 'TICARET', 'SANAYI', 'TIC', 'SAN'):
        if s.endswith(' ' + suffix):
            s = s[: -len(suffix) - 1].strip()
    return s


def is_tasfiye(r: dict) -> bool:
    return 'TASF' in (r.get('legal_name') or '').upper()


def filled_count(r: dict) -> int:
    return sum(1 for f in MERGE_FIELDS if (r.get(f) or '').strip())


def pick_winner(group: list[dict]) -> tuple[dict, list[dict]]:
    def key(r):
        return (
            0 if is_tasfiye(r) else 1,
            r['data_quality_score'] or 0,
            filled_count(r),
        )
    ranked = sorted(group, key=key, reverse=True)
    return ranked[0], ranked[1:]


def main(apply: bool) -> None:
    engine = get_engine()
    audit_rows: list[list] = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with engine.connect() as conn:
        rows = [dict(r) for r in conn.execute(text("""
            SELECT company_id, legal_name, trade_name, tax_number, vergi_no,
                   website_domain, primary_phone, primary_email,
                   nace_code, osb_parsel, adres, data_quality_score
            FROM companies
        """)).mappings().all()]

        name_map: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            n = norm_name(r.get('legal_name') or '')
            if n:
                name_map[n].append(r)
        name_groups = [rs for rs in name_map.values() if len(rs) > 1]

        vkn_map: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            v = (r.get('tax_number') or r.get('vergi_no') or '').strip()
            if v and v != '0':
                vkn_map[v].append(r)
        vkn_groups = [rs for rs in vkn_map.values() if len(rs) > 1]

        actions: list[tuple[str, dict, list[dict]]] = []
        seen_ids: set = set()

        for rs in name_groups:
            w, losers = pick_winner(rs)
            losers = [l for l in losers if str(l['company_id']) not in seen_ids]
            if losers:
                seen_ids.add(str(w['company_id']))
                actions.append(('UNVAN', w, losers))
                seen_ids.update(str(l['company_id']) for l in losers)

        for rs in vkn_groups:
            rs2 = [r for r in rs if str(r['company_id']) not in seen_ids]
            if len(rs2) < 2:
                continue
            w, losers = pick_winner(rs2)
            losers = [l for l in losers if str(l['company_id']) not in seen_ids]
            if losers:
                seen_ids.add(str(w['company_id']))
                actions.append(('VKN', w, losers))
                seen_ids.update(str(l['company_id']) for l in losers)

        total_delete = sum(len(ls) for _, _, ls in actions)
        mode = "APPLY (gercek temizlik)" if apply else "DRY-RUN (degisiklik yok)"
        print(f"Mod: {mode}")
        print(f"Islem grubu: {len(actions)}, silinecek firma: {total_delete}\n")

        try:
            for gtype, winner, losers in actions:
                for loser in losers:
                    merged = []
                    for f in MERGE_FIELDS:
                        if (winner.get(f) or '').strip() or not (loser.get(f) or '').strip():
                            continue
                        val = (loser.get(f) or '').strip()
                        # UNIQUE alanlar (tax_number): ayni deger baska kayitta varsa tasima
                        if f == 'tax_number' and apply:
                            dup = conn.execute(text(
                                "SELECT COUNT(*) FROM companies WHERE tax_number = :v AND company_id <> :w"
                            ), {"v": val, "w": winner['company_id']}).scalar()
                            if dup:
                                continue
                        merged.append(f)
                        winner[f] = val  # bellek icinde kazanan guncellenir
                    wid, lid = str(winner['company_id']), str(loser['company_id'])
                    print(f"[{gtype}] '{(winner.get('legal_name') or '')[:40]}' <- silinecek: '{(loser.get('legal_name') or '')[:40]}' (merge: {merged or '-'})")
                    audit_rows.append([stamp, gtype, wid, lid, (winner.get('legal_name') or '')[:80],
                                       (loser.get('legal_name') or '')[:80], ",".join(merged)])

                    if apply:
                        for f in merged:
                            conn.execute(text(f"UPDATE companies SET {f} = :v WHERE company_id = :w"),
                                         {"v": (loser.get(f) or '').strip(), "w": winner['company_id']})
                        conn.execute(text(
                            "UPDATE entity_resolution SET company_id = :w WHERE company_id = :l"
                        ), {"w": winner['company_id'], "l": loser['company_id']})
                        conn.execute(text("DELETE FROM companies WHERE company_id = :l"),
                                     {"l": loser['company_id']})

            if apply:
                conn.commit()
                print(f"\nOK COMMIT: {total_delete} firma silindi, alanlar kazananlara tasindi.")
            else:
                print("\n(DRY-RUN) Uygulamak icin: python scripts/dedup_apply.py --apply")
        except Exception as e:
            if apply:
                conn.rollback()
                print(f"\nROLLBACK: {e}")
            raise

    with engine.connect() as conn:
        remaining = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    print(f"Kalan firma sayisi: {remaining}")

    if audit_rows:
        log_path = ROOT / 'logs' / f'dedup_audit_{stamp}.csv'
        log_path.parent.mkdir(exist_ok=True)
        with open(log_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['zaman', 'grup_tipi', 'kazanan_id', 'silinen_id', 'kazanan_unvan', 'silinen_unvan', 'tasinan_alanlar'])
            w.writerows(audit_rows)
        print(f"Denetim kaydi: {log_path.name} ({len(audit_rows)} satir)")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
