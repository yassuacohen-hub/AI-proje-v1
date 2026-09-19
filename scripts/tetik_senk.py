#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
"""
Tetik-Pano Senkronizasyonu: Pano durumu ile tetik dosyaları uyum sağla.

Kök sorun: ADMIN-UX-LOGOUT-01 panoda `review` ama tetiği hâlâ `bekliyor`,
nöbetçi sonsuz uyarı üretiyor. Bu script panodaki final durumları tetik dosyalarıyla
eşitler ve sayaçları sıfırlar.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

# Import düzeltme
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.company_master.orchestrator import task_board as tb, trigger as trig


def tetik_senk() -> dict[str, Any]:
    """Pano durumlarını tetik kuyruğu dosyalarıyla senkronize et."""
    rapor = {
        "tarih": datetime.utcnow().isoformat(),
        "basarili": 0,
        "hata": 0,
        "detay": []
    }

    try:
        pano = json.loads(tb.TASK_BOARD.read_text(encoding='utf-8'))
    except Exception as e:
        rapor["hata"] += 1
        rapor["detay"].append(f"❌ Pano okunamadı: {e}")
        return rapor

    # Görev durumlarını ve sahibini ID'ye göre inşa et
    pano_durum_map = {t["task_id"]: {
        "durum": t.get("durum", "plan"),
        "sahip": t.get("sahip", "-"),
        "baslik": t.get("baslik", "")
    } for t in pano}

    # Tetik kuyruğu dosyaları (tüm ajanlar)
    ajanlar = ["ihsan", "utku", "salih", "yasu"]
    data_dir = Path("data/orchestrator")

    for ajan in ajanlar:
        tetik_dosya = data_dir / f"{ajan}.jsonl"
        alarm_dosya = data_dir / f"{ajan}.ALARM.json"

        if not tetik_dosya.exists():
            rapor["detay"].append(f"ℹ️  {ajan}: tetik dosyası yok (posta boş)")
            continue

        # Tetik satırlarını oku
        tetikler = []
        try:
            with tetik_dosya.open(encoding='utf-8') as f:
                for satir in f:
                    if satir.strip():
                        tetikler.append(json.loads(satir))
        except Exception as e:
            rapor["hata"] += 1
            rapor["detay"].append(f"❌ {ajan}.jsonl okunamadı: {e}")
            continue

        # Senkronizasyon: pano durumuna göre tetikleri düzelt
        tetikler_guncel = []
        duzeltilen = []

        for tetik in tetikler:
            task_id = tetik.get("task_id")
            pano_bilgi = pano_durum_map.get(task_id)

            if not pano_bilgi:
                # Pano'da bu görev yok → bekliyor kalır (bayat tetik)
                tetikler_guncel.append(tetik)
                continue

            pano_durum = pano_bilgi["durum"]

            # Pano durumuna göre tetik durumunu güncelle
            if pano_durum in ("done", "blocked", "archive", "reddedildi"):
                # Final durumlar: tetiği kapat
                tetik_eski_durum = tetik.get("durum")
                if tetik_eski_durum == "bekliyor":
                    tetik["durum"] = "kapandi"
                    tetik["kapanma_nedeni"] = f"pano durumu {pano_durum}"
                    duzeltilen.append(f"{task_id}: {tetik_eski_durum} → kapandi")
                tetikler_guncel.append(tetik)
            else:
                # Aktif durumlar: tetik bekleyen kalır veya sahip güncellenirse işle
                eski_ajan = tetik.get("ajan", "")
                # Normalize: "cline" → "yasu"
                yeni_ajan = trig.ajan_normalize(eski_ajan)
                if eski_ajan != yeni_ajan:
                    tetik["ajan"] = yeni_ajan
                    duzeltilen.append(f"{task_id}: ajan '{eski_ajan}' → '{yeni_ajan}'")
                tetikler_guncel.append(tetik)

        # Tetik dosyasına geri yaz
        try:
            with tetik_dosya.open('w', encoding='utf-8') as f:
                for tetik in tetikler_guncel:
                    f.write(json.dumps(tetik, ensure_ascii=False) + '\n')
            rapor["basarili"] += len(duzeltilen)
            if duzeltilen:
                rapor["detay"].append(f"✅ {ajan}: {len(duzeltilen)} düzeltme")
                rapor["detay"].extend([f"   - {d}" for d in duzeltilen])
        except Exception as e:
            rapor["hata"] += 1
            rapor["detay"].append(f"❌ {ajan}.jsonl yazılamadı: {e}")
            continue

        # Alarm dosyasını sıfırla (nöbetçi sayaçları artık gerekli değil)
        if alarm_dosya.exists():
            try:
                alarm_dosya.unlink()
                rapor["detay"].append(f"🧹 {ajan}.ALARM.json temizlendi")
            except Exception as e:
                rapor["detay"].append(f"⚠️  {ajan}.ALARM.json silinemedi: {e}")

    return rapor


if __name__ == "__main__":
    rapor = tetik_senk()

    print("\n" + "="*60)
    print("TETIK-PANO SENKRONİZASYONU")
    print("="*60)
    for satir in rapor["detay"]:
        print(satir)
    print(f"\nSonuç: ✅ {rapor['basarili']} | ❌ {rapor['hata']}")
    print("="*60 + "\n")

    sys.exit(0 if rapor["hata"] == 0 else 1)
