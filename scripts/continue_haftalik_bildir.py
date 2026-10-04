# -*- coding: utf-8 -*-
"""Continue haftalik ucretsiz model taramasi + Windows bildirimi.

Zamanlanmis gorev bu dosyayi cagirir:
 1) `continue_config_kur.py --tara` ile yeni :free modelleri arar
 2) Raporu okur
 3) Yeni model varsa Windows toast bildirimi gosterir

Cift tikla calistirilabilir (elle denemek icin).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SCRIPT = KOK / "scripts" / "continue_config_kur.py"
RAPOR_DIZIN = KOK / "docs" / "raporlar" / "continue"
LOG = KOK / "data" / "_tmp" / "continue_weekly.log"


def yaz(mesaj: str) -> None:
    damga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{damga}] {mesaj}"
    print(satir)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except OSError:
        pass


def tara() -> str:
    """Tarama script'ini calistirir, ham ciktiyi dondurur."""
    yaz("Tarama basliyor...")
    try:
        sonuc = subprocess.run(  # noqa: S603
            [sys.executable, str(SCRIPT), "--tara"],
            cwd=str(KOK), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=900,
        )
    except subprocess.TimeoutExpired:
        yaz("HATA: tarama zaman asimina ugradi")
        return ""
    except OSError as hata:
        yaz(f"HATA: script calistirilamadi -> {hata}")
        return ""
    yaz(f"Tarama bitti (cikis kodu {sonuc.returncode})")
    return sonuc.stdout or ""


def ozet_cikar(cikti: str) -> tuple[int, list[str]]:
    """Ciktidan eklenebilir model sayisini ve slug listesini cikarir."""
    sayi = 0
    m = re.search(r"eklenebilir:\s*(\d+)", cikti)
    if m:
        sayi = int(m.group(1))
    sluglar: list[str] = []
    bolum = cikti.split("Sablona eklenebilir (OK)")[-1] \
        if "Sablona eklenebilir (OK)" in cikti else ""
    for satir in bolum.splitlines():
        m = re.search(r"`([a-z0-9._/\-:]+)`", satir)
        if m and ":" in m.group(1):
            sluglar.append(m.group(1))
    return sayi, sluglar


def bildir(baslik: str, mesaj: str) -> None:
    """Windows toast bildirimi; basarisiz olursa sessizce gecer."""
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager,"
        " Windows.UI.Notifications,"
        " ContentType = WindowsRuntime] | Out-Null;"
        "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
        "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
        "$n=$t.GetElementsByTagName('text');"
        f"$n.Item(0).AppendChild($t.CreateTextNode('{baslik}')) | Out-Null;"
        f"$n.Item(1).AppendChild($t.CreateTextNode('{mesaj}')) | Out-Null;"
        "$x=[Windows.UI.Notifications.ToastNotificationManager]::"
        "CreateToastNotifier('Huginn Data Insights');"
        "$x.Show([Windows.UI.Notifications.ToastNotification]::new($t))"
    )
    try:
        subprocess.run(  # noqa: S603
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def main() -> int:
    cikti = tara()
    if not cikti:
        bildir("Continue Tarama", "Tarama calistirilamadi - loga bakin.")
        return 1

    sayi, sluglar = ozet_cikar(cikti)
    yaz(f"Eklenebilir model: {sayi}")

    bugun = datetime.now().strftime("%Y-%m-%d")
    rapor = RAPOR_DIZIN / f"tarama_{bugun}.md"

    if sayi > 0:
        ilk = ", ".join(sluglar[:3]) if sluglar else "yeni modeller"
        fazla = f" (+{sayi - len(sluglar[:3])})" if sayi > 3 else ""
        bildir(
            "Continue · Yeni ucretsiz model",
            f"{sayi} model eklenecek: {ilk}{fazla}",
        )
        yaz(f"Bildirim gonderildi: {sayi} yeni model")
    else:
        bildir("Continue Tarama", "Yeni ucretsiz model bulunamadi.")
        yaz("Yeni model yok")

    if rapor.exists():
        yaz(f"Rapor: {rapor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
