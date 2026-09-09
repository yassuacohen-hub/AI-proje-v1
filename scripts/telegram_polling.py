"""Telegram bot long-polling ve komut işleyici.



Çalıştırmak için:

    python scripts/telegram_polling.py



Komutlar:

    /start       — Bot tanıtımı

    /status      — Proje durumu

    /gorev       — Aktif ve bekleyen görevler

    /rapor       — Son veri kalite raporu özeti

    /wiki        — Wiki bağlantıları

    /help        — Komut listesi



Karar referansı: V10/10_ankara_osb_sentez Karar 13

"""

from __future__ import annotations



import json

import os

import re

import sys

import time

from pathlib import Path

from typing import Optional
from dotenv import load_dotenv



import requests



# Proje kökünü path'e ekle

ROOT = Path(__file__).resolve().parents[1]

load_dotenv()
sys.path.insert(0, str(ROOT))



from src.company_master.utils.telegram_bot import send_message



API_URL = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}"

TIMEOUT = 60





def _escape_html(text: str) -> str:

    """HTML parse için escape."""

    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")





def cmd_start(chat_id: str) -> None:

    send_message(

        "<b>🤖 Ankara B2B Master Bot</b>\n\n"

        "Merhaba! Bu bot, Huginn Data Insights — Ankara B2B Company Master V1.0 projesinin 11 ajan orkestrasyonunu takip eder.\n\n"

        "Komutlar için /help",

        chat_id=chat_id,

    )





def cmd_help(chat_id: str) -> None:

    send_message(

        "<b>Komutlar — ne işe yarar?</b>\n\n"

        "/start — Botu tanıtır, ilk kullanımda başlatır\n"

        "/status — Proje durumu: firma sayısı, kalite ortalaması, son güncelleme\n"

        "/gorev — Bekleyen/aktif görevler + son 5 tamamlanan (canlı pano)\n"

        "/rapor — Veri kalite özeti: toplam firma, kayıt sayısı, kalite dağılımı\n"

        "/wiki — Önemli doküman sayfalarının bağlantıları\n"

        "/help — Bu liste\n"

        "/set_status [not] — Durum dosyasına (project_state.md) not ekler\n"
        "\n"
        "<b>Bildirimler (Y14) — değişiklik izleme</b>\n"
        "/degisiklik — Son kontrolden beri: yeni firmalar + skoru ±10 değişenler\n"
        "/gunluk — Günlük özet kartı: toplam firma, kayıt, kalite dağılımı\n"
        "/izleme — İzleme durumu: kaç firma izleniyor, son kontrol ne zaman\n"
        "\n"
        "<b>Yönetim</b>\n"
        "/restart_etl — ETL hattını arka planda yeniden başlatır",

        chat_id=chat_id,

    )





def _read_project_state() -> dict:

    """project_state.md'den son durum bilgisini çıkarır."""

    state_file = ROOT / "V10" / "project_state.md"

    result = {

        "version": "bilinmiyor",

        "total_firms": 0,

        "active_tasks": 0,

        "completed_tasks": 0,

        "last_update": "bilinmiyor",

    }

    if not state_file.exists():

        return result

    

    content = state_file.read_text(encoding="utf-8")

    # Son sürüm satırını bul

    m = re.search(r"\*\*Sürüm:\*\*\s*(V[\d\.]+)", content)

    if m:

        result["version"] = m.group(1)

    

    m = re.search(r"\*\*Toplam işletme:\*\*\s*([\d\.,]+)", content)

    if m:

        result["total_firms"] = int(m.group(1).replace(",", "").replace(".", ""))

    

    # Son güncelleme tarihi

    m = re.search(r"##\s+(\d{4}-\d{2}-\d{2})", content)

    if m:

        result["last_update"] = m.group(1)

    

    return result





def cmd_status(chat_id: str) -> None:

    state = _read_project_state()

    jsonl = ROOT / "data" / "ostim" / "firmalar_sayfa1.jsonl"

    live_count = 0

    if jsonl.exists():

        with open(jsonl, "r", encoding="utf-8") as f:

            live_count = sum(1 for _ in f if _.strip())

    

    text = (

        f"<b>📊 Proje Durumu</b>\n\n"

        f"<b>Sürüm:</b> {state['version']}\n"

        f"<b>Canlı OSTİM kaydı:</b> {live_count:,} firma\n"

        f"<b>Wiki notu:</b> {len(list((ROOT / 'V10').rglob('*.md'))):,} dosya\n"

        f"<b>Son güncelleme:</b> {state['last_update']}\n\n"

        f"<b>Arayüz:</b> http://localhost:8501"

    )

    send_message(text, chat_id=chat_id)





def cmd_gorev(chat_id: str) -> None:

    text = (

        "<b>📝 Aktif Görevler</b>\n\n"

        "1. <b>OSTİM scraping:</b> 1 sayfa tamamlandı (~300 firma)\n"

        "2. <b>Tüm OSTİM:</b> 17 sektör × ~200 sayfa (Beklemede)\n"

        "3. <b>ASO firmarehberi scraper:</b> Beklemede\n"

        "4. <b>MERSİS entegrasyonu:</b> Captcha çözümü bekleniyor\n"

        "5. <b>Telegram bot entegrasyonu:</b> Aktif\n\n"

        "Sonraki adımlar için: /wiki"

    )

    send_message(text, chat_id=chat_id)





def cmd_rapor(chat_id: str) -> None:

    rapor = ROOT / "data" / "ostim" / "kalite_raporu.md"

    if not rapor.exists():

        send_message("<b>📋 Kalite Raporu</b>\nHenüz rapor oluşturulmadı.", chat_id=chat_id)

        return

    

    content = rapor.read_text(encoding="utf-8")

    # İstatistik tablolarını çıkar

    toplam_match = re.search(r"\*\*Toplam Kayıt:\*\*\s*([\d\.,]+)", content)

    ort_match = re.search(r"\| Ortalama skor \| \*(\d+\.?\d*)\*", content)

    yuksek_match = re.search(r"\| Yüksek \(80-100\) \| (\d+)", content)

    

    toplam = toplam_match.group(1) if toplam_match else "?"

    ort = ort_match.group(1) if ort_match else "?"

    yuksek = yuksek_match.group(1) if yuksek_match else "?"

    

    text = (

        f"<b>📋 Son Kalite Raporu</b>\n\n"

        f"<b>Toplam kayıt:</b> {toplam}\n"

        f"<b>Ortalama kalite:</b> {ort}/100\n"

        f"<b>Yüksek kalite:</b> {yuksek}\n\n"

        f"Detay: <code>data/ostim/kalite_raporu.md</code>"

    )

    send_message(text, chat_id=chat_id)





def cmd_wiki(chat_id: str) -> None:

    text = (

        "<b>📚 Önemli Wiki Sayfaları</b>\n\n"

        "• 00-Home — Ana sayfa\n"

        "• 10_mvp_kapsamı — MVP kapsam\n"

        "• 10_ankara_osb_sentez — 13 karar\n"

        "• 01_veri_kaynagi_envanteri — 9 kaynak\n"

        "• 04_web_kazima_kaynak_arastirmasi — 12 web kaynağı\n"

        "• 03_kvkk_ve_veri_politikasi — KVKK\n"

        "• 09_telegram_bot_rehberi — Telegram bot\n\n"

        "Tümü: <code>C:\\Projeler\\Huginn Data Insights\\AI proje v1\\V10</code>"

    )

    send_message(text, chat_id=chat_id)

def _check_change_helpers() -> str:
    """change_notify fonksiyon adlarini dogrular (telegram komutlari kirilmasin)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "src"))
    try:
        import change_notify as cn
        need = ["fetch_current", "format_daily", "format_change_message", "diff_snapshots"]
        eksik = [n for n in need if not hasattr(cn, n)]
        return ("OK" if not eksik else "EKSIK:" + ",".join(eksik)) + " rows=" + (
            "var" if hasattr(cn, "diff_snapshots") else "yok")
    except Exception as exc:
        return "HATA:" + str(exc)[:120]


def _notify_state() -> dict:
    """change_notify_state.json icerigi (izleme durumu)."""
    p = ROOT / "data" / "orchestrator" / "change_notify_state.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def cmd_degisklik(chat_id: str) -> None:
    """Son kontrolden beri yeni firma + skoru degisenleri gosterir."""
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from change_notify import diff_snapshots, fetch_current, format_change_message
        cur = fetch_current()
        st = _notify_state()
        if not st.get("rows"):
            send_message("Izleme henuz baslatilmamis. Bilgi icin /izleme", chat_id=chat_id)
            return
        diff = diff_snapshots(st["rows"], cur["rows"])
        n = len(diff["added"]) + len(diff["changed"]) + len(diff["removed"])
        if n == 0:
            send_message("Degisiklik yok. Izlenen firma: %s" % f"{len(cur['rows']):,}", chat_id=chat_id)
        else:
            send_message(format_change_message(diff, cur["rows"], cur["counts"]), chat_id=chat_id)
    except Exception as exc:
        send_message("Degisiklik kontrolu hatasi: %s" % _escape_html(str(exc)[:200]), chat_id=chat_id)


def cmd_gunluk(chat_id: str) -> None:
    """Gunluk ozet karti gonderir."""
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from change_notify import fetch_current, format_daily
        cur = fetch_current()
        send_message(format_daily(cur["counts"]), chat_id=chat_id)
    except Exception as exc:
        send_message("Gunluk ozet hatasi: %s" % _escape_html(str(exc)[:200]), chat_id=chat_id)


def cmd_izleme(chat_id: str) -> None:
    """Izleme durumunu gosterir."""
    st = _notify_state()
    if not st.get("rows"):
        send_message("Izleme baslatilmamis. Sunucuda:\n<code>python scripts/change_notify.py --baseline</code>", chat_id=chat_id)
        return
    send_message(
        "Izleme aktif.\n"
        "Izlenen firma: %s\n"
        "Son kontrol: %s" % (f"{len(st['rows']):,}", st.get("last_run", "?")[:16].replace("T", " ")),
        chat_id=chat_id,
    )






def cmd_set_status(chat_id: str, message: str) -> None:
    """Telegram'dan project_state.md'ye son durumu yazar."""
    state_file = ROOT / "V10" / "project_state.md"
    if not state_file.exists():
        send_message("❌ project_state.md bulunamadı.", chat_id=chat_id)
        return
    
    today = time.strftime("%Y-%m-%d")
    entry = f"- [{today}] {message}"
    
    file_content = state_file.read_text(encoding="utf-8")
    if "### Açık Sorunlar" in file_content:
        file_content = file_content.replace("### Açık Sorunlar", f"### Açık Sorunlar\n\n{entry}")
    else:
        file_content += f"\n\n### Eklenen Notlar\n\n{entry}\n"
    
    state_file.write_text(file_content, encoding="utf-8")
    send_message(f"✅ Durum güncellendi: <i>{_escape_html(message[:100])}</i>", chat_id=chat_id)


def cmd_daily_report() -> None:
    """Sabah 09:00'da otomatik durum raporu gönder."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        return
    
    state = _read_project_state()
    date = time.strftime("%Y-%m-%d %H:%M")
    
    # Veritabanı sayıları
    try:
        from sqlalchemy import text
        from src.company_master.db.connection import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            company_count = conn.execute(text("SELECT count(*) FROM companies")).scalar()
            sr_count = conn.execute(text("SELECT count(*) FROM source_records")).scalar()
            er_count = conn.execute(text("SELECT count(*) FROM entity_resolution")).scalar()
    except Exception:
        company_count = sr_count = er_count = "?"
    
    text_msg = (
        f"📊 <b>Günlük Rapor — {date}</b>\n\n"
        f"🏢 Şirket sayısı: <b>{company_count}</b>\n"
        f"📥 Kayıt (source_records): <b>{sr_count}</b>\n"
        f"🔗 Entity resolution: <b>{er_count}</b>\n"
        f"\nSürüm: {state.get('version', '?')}\n"
        f"Son güncelleme: {state.get('last_update', '?')}"
    )
    send_message(text_msg, chat_id=chat_id)


def handle_command(text: str, chat_id: str) -> None:
    if chat_id != os.environ.get("TELEGRAM_CHAT_ID"):
        send_message("🚫 Yetkisiz erişim.", chat_id=chat_id)
        return

    cmd = text.strip().lower()

    if cmd == "/start":

        cmd_start(chat_id)

    elif cmd == "/help":

        cmd_help(chat_id)

    elif cmd == "/status":

        cmd_status(chat_id)

    elif cmd == "/gorev":

        cmd_gorev(chat_id)

    elif cmd == "/rapor":

        cmd_rapor(chat_id)

    elif cmd == "/wiki":

        cmd_wiki(chat_id)

    elif cmd == "/restart_etl":

        send_message("🔄 ETL tetikleniyor...", chat_id=chat_id)

        import subprocess
        subprocess.Popen([sys.executable, "-m", "company_master.etl.pipeline"])

    elif cmd == "/degisiklik":
        cmd_degisklik(chat_id)

    elif cmd == "/gunluk":
        cmd_gunluk(chat_id)

    elif cmd == "/izleme":
        cmd_izleme(chat_id)

    elif cmd.startswith("/set_status "):

        msg = text.strip()[len("/set_status "):]

        cmd_set_status(chat_id, msg)

    else:

        send_message(f"Bilinmeyen komut: {cmd}\nYardım için /help", chat_id=chat_id)





def poll() -> None:
    # Cron: saat 09:00'da günlük rapor
    daily_report_hour = 9
    daily_report_sent = False


    """Long polling ile Telegram mesajlarını dinler."""

    print(f"[{time.strftime('%H:%M:%S')}] Telegram polling başladı")

    print(f"Token mask: ****")

    print(f"CHAT_ID: {os.environ.get('TELEGRAM_CHAT_ID')}")

    

    offset: Optional[int] = None

    while True:

        try:

            params = {"offset": offset, "limit": 100, "timeout": 30}

            resp = requests.get(

                f"{API_URL}/getUpdates",

                params=params,

                timeout=TIMEOUT,

            )

            resp.raise_for_status()

            data = resp.json()

            

            if not data.get("ok"):

                print(f"[HATA] getUpdates başarısız: {data}")

                time.sleep(5)

                continue

            

            updates = data.get("result", [])

            for update in updates:

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:

                    continue

                

                chat = message.get("chat", {})

                chat_id = str(chat.get("id"))

                text = message.get("text", "")

                

                if text.startswith("/"):

                    print(f"[KOMUT] {chat_id}: {text}")

                    handle_command(text, chat_id)

                else:

                    # Normal mesaj: yankı + yardım

                    send_message(

                        f"Mesaj alındı: <b>{_escape_html(text[:50])}</b>\n"

                        f"Komutlar için /help",

                        chat_id=chat_id,

                    )

            

            if not updates:

                # Long polling bekleme + cron kontrolü
                current_hour = int(time.strftime("%H"))
                if current_hour == daily_report_hour and not daily_report_sent:
                    cmd_daily_report()
                    daily_report_sent = True
                elif current_hour != daily_report_hour:
                    daily_report_sent = False

        except KeyboardInterrupt:

            print("\nDurduruldu.")

            break

        except Exception as exc:

            print(f"[HATA] {exc}")

            time.sleep(5)





if __name__ == "__main__":

    if not os.environ.get("TELEGRAM_BOT_TOKEN"):

        print("HATA: TELEGRAM_BOT_TOKEN ayarlanmamış.")

        print("Önce: .env dosyasını yükleyin veya ortam değişkeni olarak ayarlayın.")

        sys.exit(1)

    

    if not os.environ.get("TELEGRAM_CHAT_ID"):

        print("HATA: TELEGRAM_CHAT_ID ayarlanmamış.")

        sys.exit(1)

    

    poll()