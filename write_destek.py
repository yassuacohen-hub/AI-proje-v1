open('src/company_master/destek.py', 'w', encoding='utf-8').write('''# -*- coding: utf-8 -*-
\"\"\"Destek Merkezi MVP — Ticket CRUD + durum makinesi.\"\"\"
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
DEPPO_PATH = ROOT / "data" / "destek" / "tickets.json"

GECERLI_GECISLER = {
    "acik": {"inceleniyor"},
    "inceleniyor": {"cozuldu", "acik"},
    "cozuldu": {"kapali"},
    "kapali": set(),
}

@dataclass(frozen=True)
class Ticket:
    id: str
    tenant_id: str
    baslik: str
    aciklama: str
    durum: str = "acik"
    olusturma: str = ""
    guncelleme: str = ""

    def __post_init__(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        object.__setattr__(self, "olusturma", self.olusturma or now)
        object.__setattr__(self, "guncelleme", now)

def _yukle():
    if not DEPPO_PATH.exists():
        return {}
    try:
        data = json.loads(DEPPO_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}

def _kaydet(tickets):
    DEPPO_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEPPO_PATH.write_text(json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8")

def _to_dict(ticket):
    return {"id": ticket.id, "tenant_id": ticket.tenant_id, "baslik": ticket.baslik, "aciklama": ticket.aciklama, "durum": ticket.durum, "olusturma": ticket.olusturma, "guncelleme": ticket.guncelleme}

def _from_dict(d):
    return Ticket(id=str(d.get("id","")), tenant_id=str(d.get("tenant_id","")), baslik=str(d.get("baslik","")), aciklama=str(d.get("aciklama","")), durum=str(d.get("durum","acik")), olusturma=str(d.get("olusturma","")), guncelleme=str(d.get("guncelleme","")))

def durum_gecis(ticket, yeni_durum):
    izinli = GECERLI_GECISLER.get(ticket.durum, set())
    if yeni_durum not in izinli:
        raise ValueError(f"Gecersiz gecis: {ticket.durum} -> {yeni_durum}. Izinli: {sorted(izinli)}")
    object.__setattr__(ticket, "durum", yeni_durum)
    object.__setattr__(ticket, "guncelleme", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    return ticket

def ticket_olustur(tenant_id, baslik, aciklama="", ticket_id=None):
    tid = ticket_id or str(uuid.uuid4())[:8]
    t = Ticket(id=tid, tenant_id=tenant_id, baslik=baslik, aciklama=aciklama)
    tickets = _yukle(); tickets[tid] = _to_dict(t); _kaydet(tickets)
    return t

def ticket_getir(ticket_id):
    d = _yukle().get(ticket_id)
    return None if d is None else _from_dict(d)

def ticket_guncelle(ticket_id, **kw):
    tickets = _yukle(); d = tickets.get(ticket_id)
    if d is None: return None
    for k in ("baslik", "aciklama"):
        if k in kw: d[k] = kw[k]
    d["guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    tickets[ticket_id] = d; _kaydet(tickets)
    return _from_dict(d)

def ticket_sil(ticket_id):
    tickets = _yukle()
    if ticket_id not in tickets: return False
    del tickets[ticket_id]; _kaydet(tickets); return True

def ticketlar_listele(tenant_id=None):
    tickets = [ticket_getir(tid) for tid in _yukle()]
    tickets = [t for t in tickets if t is not None]
    if tenant_id is not None: tickets = [t for t in tickets if t.tenant_id == tenant_id]
    tickets.sort(key=lambda t: t.olusturma)
    return tickets

def durum_gecis_depo(ticket_id, yeni_durum):
    t = ticket_getir(ticket_id)
    if t is None: return None
    updated = durum_gecis(t, yeni_durum)
    tickets = _yukle(); tickets[ticket_id] = _to_dict(updated); _kaydet(tickets)
    return updated
''')
print('Done')