# -*- coding: utf-8 -*-
"""MAIL-SAGLAYICI-TESTI-01 canli test (D-380: anahtar/adres degeri ASLA yazdirilmaz; yalniz durum kodu).
Kol1 Brevo SMTP | Kol2 MailerLite REST | Kol3 Sender REST. Her koldan 3 deneme -> ADMIN_EMAIL.
ponytail: tek dosya, stdlib; kalici modul gerekirse src/ altina tasi.
"""
import json
import smtplib
import sys
import time
import urllib.error
import urllib.request
from email.message import EmailMessage
from pathlib import Path

ENV = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\.env")
E = {}
for ln in ENV.read_text(encoding="utf-8-sig").splitlines():
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k, _, v = ln.partition("=")
        E[k.strip()] = v.strip().strip('"').strip("'")

import os
ALICI = os.environ.get("MAIL_ALICI") or E.get("ADMIN_EMAIL", "")  # PO 21.10: gmail'e yonlendirme calismadi -> gmail'e dogrudan
from email.utils import parseaddr
GONDEREN = E.get("SMTP_FROM", "") or ALICI
GONDEREN_ADRES = parseaddr(GONDEREN)[1] or ALICI  # Sender "Ad <adres>" kabul etmez, yalniz adres
KONU = "Huginn mail saglayici testi"
GOVDE = "MAIL-SAGLAYICI-TESTI-01 canli test. Yanit gerekmez."


def http(url, yontem="GET", govde=None, token=""):
    h = {"Authorization": "Bearer " + token, "Accept": "application/json",
         "Content-Type": "application/json", "User-Agent": "huginn-mailtest/1"}
    d = json.dumps(govde).encode() if govde is not None else None
    r = urllib.request.Request(url, data=d, headers=h, method=yontem)
    try:
        with urllib.request.urlopen(r, timeout=30) as x:
            return x.status, ""
    except urllib.error.HTTPError as e:
        try:
            m = str(json.loads(e.read().decode("utf-8", "replace")).get("message", ""))[:100]
        except Exception:
            m = ""
        return e.code, m
    except Exception as e:
        return 0, type(e).__name__


def kol1():
    host, port = E.get("SMTP_HOST", ""), int(E.get("SMTP_PORT", "587") or 587)
    user = E.get("SMTP_USER", "")
    for sifre_ad in ("SMTP_PASSWORD", "SMTP_PASS", "BREVO_SMTP_KEY"):
        sifre = E.get(sifre_ad, "")
        if not sifre:
            continue
        for i in range(1, 4):
            m = EmailMessage()
            m["From"], m["To"], m["Subject"] = GONDEREN, ALICI, f"{KONU} Brevo-SMTP #{i}"
            m.set_content(GOVDE)
            try:
                with smtplib.SMTP(host, port, timeout=30) as s:
                    s.starttls()
                    s.login(user, sifre)
                    s.send_message(m)
                print(f"Kol1 Brevo-SMTP #{i} sifre={sifre_ad}: 250 OK")
            except smtplib.SMTPResponseException as e:
                print(f"Kol1 Brevo-SMTP #{i} sifre={sifre_ad}: SMTP {e.smtp_code}")
            except Exception as e:
                print(f"Kol1 Brevo-SMTP #{i} sifre={sifre_ad}: {type(e).__name__}")
            time.sleep(1)
        return
    print("Kol1: sifre anahtari yok")


def kol2():
    t = E.get("MAILERLITE_API_KEY", "")
    # MailerLite v2 (connect.mailerlite.com) tekil islem maili endpointi sunmaz -> yalniz yetki kontrolu olcuyoruz
    for i in range(1, 4):
        print(f"Kol2 MailerLite auth #{i}: {http('https://connect.mailerlite.com/api/subscribers?limit=1', token=t)}")
        time.sleep(1)


def kol3():
    t = E.get("SENDER_API_KEY", "")
    print(f"Kol3 Sender auth: {http('https://api.sender.net/v2/subscribers?limit=1', token=t)}")
    for i in range(1, 4):
        g = {"from": {"email": GONDEREN_ADRES, "name": "Huginn"}, "to": {"email": ALICI, "name": "Admin"},
             "subject": f"{KONU} Sender #{i}", "html": f"<p>{GOVDE}</p>", "text": GOVDE}
        print(f"Kol3 Sender-REST #{i}: {http('https://api.sender.net/v2/message/send', 'POST', g, t)}")
        time.sleep(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("alici_dolu:", bool(ALICI), "| gonderen_dolu:", bool(GONDEREN))
    for kol in sys.argv[1:] or ["1", "2", "3"]:
        {"1": kol1, "2": kol2, "3": kol3}[kol]()
