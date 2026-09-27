# AI-CHAT-KOORDINASYON-01 — Ajan Arası İletişim Kuralları

## Bağımlılık
Olmadı (MIMIR sohbet motoru + ajan chat sistemi mevcut).

## Çıktı
- **SISTEM_PROMPT güncelleme:** `src/company_master/ai_chat.py`
  - Ajan arası iletişim kuralı + koordinasyon protokolü
  - Mesaj yönlendirme (kimden → kime → görev)

- **Koordinasyon Library:** `src/company_master/ajan_chat_koordinasyon.py`
  - Fonksiyonlar:
    1. `sorun_ac()` — ajan-ajan iletişim kaydı (ac + görev linklemesi)
    2. `sorun_devret()` — sorunu başka ajana ver
    3. `koordinasyon_ozeti()` — aktif ajan arası mesajlar
  - İşlemi chat.py JSONL loguna yaz (append-only)

- **Testler:** `tests/test_ai_chat_koordinasyon.py`
  - Ajan A → Ajan B mesaj, 2-way linklemesi
  - Koordinasyon özetinde görünür
  - Görev teslimi otomatik mesaj kapatması

- **Dok:** `docs/AJAN_ARASI_ILETISIM.md`
  - Protokol: `[AJAN-A] → [AJAN-B] <görev_id> : <mesaj>`
  - Öncelik + durum döngüsü
  - Fallback (ajan yanıt vermezse ortostratöre escalation)

## Kurallar
- Chat.py'deki `ac()` fonksiyonuna `ajan_hedef` parametresi
- Koordinasyon = *yalnızca* açık görevlere link edilir
- Escalation timeout: 24 saat (iş günü sonrası)
- MIMIR kilit sözü ile ajan-ajan mesaj gönderme onaylı

## Teslim
1. SISTEM_PROMPT + parametreler (ai_chat.py)
2. Koordinasyon library (ajan_chat_koordinasyon.py)
3. Test suite + fixtures (test_ai_chat_koordinasyon.py)
4. Dok + örnek senaryo (AJAN_ARASI_ILETISIM.md)

## Zaman Tahmini
- Koordinasyon library: 1 saat
- SISTEM_PROMPT update: 0.5 saat
- Testler: 1 saat
- **Toplam: 2.5 saat (Aciliyet: Sprint 2 seri)**

## İçerik
### Senaryo 1: Basit Ajan Arası Mesaj
```
User: "MIMIR, Yasu'dan Utku'ya: DB migration tamamlandı mı?"
MIMIR: Sorun açmadan coordinasyon_ozeti() → açık mesajlar
        Utku'nun son 3 mesajını gösterir
```

### Senaryo 2: Problem Escalation
```
User: "Utku 24h yanıt vermediyse escalate to ihsan"
MIMIR: sorun_devret(task_id="ALTYAPI-DB-MIGRATION-01", 
                    kimden="utku", kime="ihsan", 
                    mesaj="24h timeout") 
       → ihsan posta kutusuna düşer + chat log
```

### Senaryo 3: Teslim + Otomatik Kapatış
```
User: "Utku: TESLIM ALTYAPI-DB-MIGRATION-01"
MIMIR: İçerik onaylar → teslim_et() çağrılır
        açık koordinasyon mesajları **otomatik kapanır**
        Yasu/İhsan'a notification gönderilir
```
