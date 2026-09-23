# Ajan Chat Sistemi — Tasarım Belgesi (D-192)

## Karar Özeti

**Konum:** `data/orchestrator/ajan-chat.jsonl` (append-only log)  
**Türü:** Lightweight JSONL, CLI entegre, Lock mekanizması ile  
**Amaç:** Ajanlar sorunları alıntıla → çözüm yolları sun → karar oluştur  
**Başlama:** Phase 1 (JSONL + CLI, 1-2 gün)  
**Evrim:** Phase 2 (2 hafta + 10+ problem + 20+ çözüm olursa — SQLite + Dashboard)

---

## 1. Problem Tanımı

Şu anda:
- Ajanlar hata bulduğu zaman rapor dosyasında yalnız kendi çözümünü yazar
- Diğer ajanlar bu hatayı görmüyor → tekrar yapabiliyor
- Çözüm önerileri merkezi değil, rapor dosyalarına dağınık
- Öğrenme yavaş: D-70 (self-lock guard) gibi hatalar kaydedilmiyor, gelecekte benzer hata yapılabilir
- **Orkestratör:** Hata + çözüm + görüş merkezi değil; görüş & eleştiriler tek yerde toplanmıyor

**Sonuç:** Ajanlar birbirinin sorunlarından ve çözümlerinden faydalanmıyor. Orkestratör KAHİN tavsiyelerine ulaşamıyor.

---

## 2. Çözüm: Phase 1 (Lightweight)

### 2.1 Veri Yapısı

**Dosya:** `data/orchestrator/ajan-chat.jsonl`

Her satır JSON (append-only), 2 alan: **sorun** + **çözüm**

```json
{
  "timestamp": "2026-09-23T14:20:00Z",
  "ajan": "yasu",
  "task_id": "ALTYAPI-KILIT-OTOMATIK-01",
  "sorun": "D-70 Self-lock Guard: task_board.py L-329 sahip alanı hatalı geçti",
  "cozum": "task_board.py gorev_guncelle() 'sahip' alanını koruyacak şekilde düzelt — test 9/9 geçer",
  "durum": "cokundurmus",
  "link": "data/orchestrator/ALTYAPI-KILIT-OTOMATIK-01_rapor_2026-09-23_yasu.md"
}
```

**Alanlar:**

| Alan | Tip | Örnek | Amaç |
|------|-----|-------|------|
| `timestamp` | ISO8601 | `2026-09-23T14:20:00Z` | Chronological order |
| `ajan` | enum: ihsan\|utku\|salih\|yasu | `yasu` | Kim bildirdi |
| `task_id` | string | `ALTYAPI-KILIT-01` | Hangi görevde bulundu |
| `sorun` | string (1-200 char) | "D-70 sahip alanı hatalı geçişi" | **Alıntı**: Sorunu 1 cümle, spesifik |
| `cozum` | string (1-300 char) | "task_board.py:329 koruma ekle" | **Çözüm yolu**: Neyi yap (1-2 adım) |
| `durum` | enum: acik\|cokundurmus\|cozuldu | `cokundurmus` | Sorun durumu: açık/çözüm bekleniyor/çözüldü |
| `link` | string (path) | `data/orchestrator/..._rapor.md` | Detay rapor dosyası |

---

### 2.2 Durum Semantiği

| Durum | Anlam | Kimin Yazması | Tetik |
|-------|-------|---------------|-------|
| `acik` | Hata bulundu, çözüm henüz yok | Bulan ajan (yasu/utku/salih) | ihsan'a CH-PROBLEM tetik |
| `cokundurmus` | Çözüm önerildi, test bekleniyor | Çözüm sunan ajan | Sahibine: PR açtı mı? Test geçti mi? |
| `cozuldu` | Çözüm tamamlandı, D-XX kararına eklendi | Orkestratör (ihsan) | Kapalı — analitik konusunda saklanan |

---

### 2.3 CLI Komutlar (Phase 1)

**Script:** `scripts/ajan_chat.py`

**4 Temel Komut + 1 Özet:**

```bash
# 1. PROBLEM AÇMA (Hata bulunca)
python scripts/ajan_chat.py ac \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun "D-70 Self-lock: sahip field geçişi task_board.py:329" \
  --cozum "gorev_guncelle() method'ında sahip koruma ekle"
  # Çıktı: ajan-chat.jsonl'e satır eklendi (durum=acik)
  # Tetik: ihsan'a "CH-PROBLEM-KILIT" tetik düştü

# 2. ÇÖZÜM GÖNDERME (Çözüm bulunca)
python scripts/ajan_chat.py guncelle \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun-index 0 \
  --cozum-guncel "task_board.py:329-335 sahip koruma loop + 9/9 test pass" \
  --durum cokundurmus
  # Tetik: Sahip ajanına "CH-COZUM-ONAY-01" tetik düştü

# 3. ÇÖZDÜ İŞARETLE (Kapalı — archiv)
python scripts/ajan_chat.py kapat \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun-index 0 \
  --karar "D-70 added to AGENTS.md decision_log (2026-09-23)"
  # Durum: cozuldu → analitik hesaplamada dahil (çözüm süresi = T-kapalı - T-acik)

# 4. CHAT OKU (Task veya son N mesaj)
python scripts/ajan_chat.py oku --task-id ALTYAPI-KILIT-OTOMATIK-01
python scripts/ajan_chat.py oku --son 10

# 5. ÖZET (Severity breakdown)
python scripts/ajan_chat.py ozet --durum acik
# Çıktı: Açık sorunlar / Çözüm beklenenler / Çözenler
```

**Bulgula Komutu (Ayrı Araç — Phase 1+ ):**

```bash
# Tasarımda eleştiri / görüş / öneri
python scripts/ajan_chat.py bulgula \
  --konu "Tasarım Belgesi (D-192)" \
  --bulgu "CLI komutları karışık, ac + guncelle 2 komut olması yeterli"
  # Çıktı: data/orchestrator/ajan-chat-bulgular.jsonl'e yazılır
  # Tetik: ihsan'a CH-BULGULAR-TASARIM
```

---

### 2.4 Entegrasyonlar

#### 2.4.1 Rapor Dosyalarında Referans

**data/orchestrator/ALTYAPI-KILIT-OTOMATIK-01_rapor_2026-09-23_yasu.md:**

```markdown
## Bulgular — Chat Entegrasyonu

### D-70: Self-lock Guard (AÇIK → ÇÖZÜLDÜ)

**Sorun (alıntı):**
> D-70 Self-lock: task_board.py:329 sahip field geçişi hatalı

**Çözüm (önerildi):**
> gorev_guncelle() method'ında sahip koruma loop ekle

**Durum:** [chat:0] (2026-09-23 14:20 yasu → 14:25 utku → 14:30 yasu)

**Karar:** D-70 kural eklendi ve AGENTS.md'ye yazıldı (cozuldu)

**Tasarımda İyileştirme Önerisi?**
Lütfen [`data/orchestrator/AJAN-CHAT-SISTEM-TASARIMI-2026-09-23.md`](AJAN-CHAT-SISTEM-TASARIMI-2026-09-23.md) üzerinde `ajan_chat.py bulgula` komutunu kullanarak eleştiri ekleyin.
```

#### 2.4.2 Tetik Otomasyonu — rapor_postala() Kancası

**trigger.py → rapor_postala():**

```python
# Architect rapor yazıldı → sorun var mı?
if rapor_severity >= "WARNING":
    # Otomatik problem açtır
    from company_master.chat import ac
    
    ac(
        ajan=architect_ajan,
        task_id=task_id,
        sorun=rapor_bulgusu_alinti,  # "D-70 self-lock bug"
        cozum=""  # Henüz yok
    )
    # Tetik: ihsan → CH-PROBLEM-{task_id}
```

#### 2.4.3 Dashboard Widget

**web_dashboard/tabs/admin_panel.py:**

```python
@st.experimental_fragment
def render_chat_summary() -> None:
    """Son hataları + çözüm oranını göster."""
    from company_master.chat import ozet
    
    acik = ozet(durum="acik")
    cokundurmus = ozet(durum="cokundurmus")
    cozuldu = ozet(durum="cozuldu")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Açık Sorunlar", len(acik))
    col2.metric("Çözüm Bekleniyor", len(cokundurmus))
    col3.metric("Çözüldü", len(cozuldu))
    
    st.subheader("Son Açılan Sorunlar")
    for msg in acik[-3:]:
        st.write(f"🔴 [{msg['ajan']}] {msg['sorun']} → {msg['task_id']}")
        st.caption(f"Çözüm önerisi: {msg['cozum']}")
```

---

### 2.5 Lock Mekanizması (D-68 Uyum)

```python
# ajan_chat.py — sorun açma
def ac(ajan: str, task_id: str, sorun: str, cozum: str = "") -> dict[str, Any]:
    """Sorun kayıt (append-only, atomic D-68 tarzı)."""
    
    log_yolu = data_dir / "ajan-chat.jsonl"
    
    satir = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "ajan": ajan_normalize(ajan),
        "task_id": task_id,
        "sorun": sorun[:200],  # Max 200 char (alıntı)
        "cozum": cozum[:300],  # Max 300 char (çözüm)
        "durum": "acik",
        "link": ""
    }
    
    satir_json = json.dumps(satir, ensure_ascii=False) + "\n"
    
    # Atomic append (D-68)
    with lock_ajan_chat():
        with log_yolu.open("a", encoding="utf-8") as f:
            f.write(satir_json)
        gunluk_log_yaz({"islem": "chat_ac", "task_id": task_id})
    
    # Tetik
    trigger.tetik_ekle("ihsan", f"CH-PROBLEM-{task_id}")
    
    return satir
```

---

## 3. Senaryo: ALTYAPI-KILIT-OTOMATIK-01

### T=14:20 (Yasu — Denetim)
```bash
python scripts/ajan_chat.py ac \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun "D-70 Self-lock: sahip field hatalı geçişi" \
  --cozum "task_board.py:329 koruma loop ekle"

# Sonuç:
# ajan-chat.jsonl:
# {"timestamp":"2026-09-23T14:20:00Z","ajan":"yasu",...,"durum":"acik"}
# tetik: ihsan -> CH-PROBLEM-KILIT-01
```

### T=14:25 (Utku — Üretim)
```bash
# Tetik gördü, kodda düzeltme yaptı
python scripts/ajan_chat.py guncelle \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun-index 0 \
  --cozum-guncel "task_board.py L329-335: sahip koruma, 9/9 test pass" \
  --durum cokundurmus

# ajan-chat.jsonl'de aynı satırın cozum + durum güncellendi
# tetik: sahip ajanına -> CH-COZUM-ONAY-01
```

### T=14:30 (Yasu — Denetim)
```bash
# Review tamamlandı
python scripts/ajan_chat.py kapat \
  --task-id ALTYAPI-KILIT-OTOMATIK-01 \
  --sorun-index 0 \
  --karar "D-70 eklendi + test 100%"

# Durum: cozuldu
# Analytics: çözüm süresi = 10 dakika
```

**Chat log açık:**
```
acik    (14:20) yasu:   D-70 Self-lock → task_board.py koruma
  └── cokundurmus (14:25) utku: 9/9 test pass
  └── cozuldu (14:30) yasu: D-70 added
```

---

## 4. Dosya ve Kod Haritası

### Phase 1 (1-2 gün)

| Dosya | Amaç | Satır |
|-------|------|-------|
| `scripts/ajan_chat.py` | CLI (ac/guncelle/kapat/oku/ozet) | ~120 |
| `src/company_master/chat.py` | Kütüphane (append, lock, filter, format) | ~80 |
| `data/orchestrator/ajan-chat.jsonl` | Append-only log | — |
| `data/orchestrator/ajan-chat-bulgular.jsonl` | Eleştiri + feedback log (bulgula) | — |
| `tests/test_ajan_chat.py` | Unit + concurrent append | ~70 |

### Entegrasyon Noktaları (hafif)

| Dosya | Değişiklik | Neden |
|-------|-----------|-------|
| `src/company_master/orchestrator/trigger.py` | `rapor_postala()` sonunda `from company_master.chat import ac` → chat.ac() çağır | Architect rapor → auto-problem tetik |
| `web_dashboard/tabs/admin_panel.py` | Chat widget (3 metric + 3 son sorun) | İhsan görüş alanı |
| `scripts/ajan_chat.py` | Kendi başında; gorev_kutusu'dan independent | Bağlantı yok — modüler |

---

## 5. Test Stratejisi

```python
# tests/test_ajan_chat.py

def test_ac_sorun_acilir():
    """Sorun satırı append edilir, durum=acik."""
    
def test_guncelle_sorun_indexle():
    """Aynı sorunun çözümü güncellenir (aynı satır)."""
    
def test_kapat_durum_cozuldu():
    """Sorun kapatılır, durum=cozuldu."""
    
def test_oku_task_id_filtresi():
    """--task-id ALTYAPI-01 → yalnız o görevin sorunları."""
    
def test_ozet_durum_breakdown():
    """--durum acik → açık sorunlar sayısı."""
    
def test_lock_concurrent_ac():
    """3 parallel ac() → tüm sorunlar kaydedilir (lock safe)."""
    
def test_tetik_ch_problem():
    """Problem açılınca tetik ihsan'a düşer."""
    
def test_bulgula_tasarim_feedbacki():
    """Bulgula komutu ajan-chat-bulgular.jsonl'e yazılır."""
```

---

## 6. Orkestratör Günlük Rutini (D-192)

**İhsan'ın Sorumlulukları — Her Gün (15 min):**

```markdown
### Görevi: Ajan Chat Feedback'lerini Değerlendir & Çözüm Planı Yap

1. **Açık Sorunları Kontrol Et** (ajan-chat.jsonl)
   ```bash
   python scripts/ajan_chat.py ozet --durum acik
   ```
   - Sorun sayısı > 3 mi? Artan trend var mı?
   - Hangi görevlerde tekrarlayan hatalar?

2. **Çözüm Beklenenler Gözden Geçir**
   ```bash
   python scripts/ajan_chat.py ozet --durum cokundurmus
   ```
   - 24 saate yaklaşan çözümler var mı?
   - Test engelleri var mı?

3. **Bulgular (Görüş & Eleştiriler) Topla**
   ```bash
   python scripts/ajan_chat.py bulgula --list
   # ajan-chat-bulgular.jsonl'deki son 5 giriş
   ```
   - Tasarımda hata var mı?
   - CLI kullanıcı şikayeti var mı?
   - Performance sorun var mı?

4. **Haftalık Karar Defteri**
   - Çözülen sorunlar: D-XX kuralı eklendi
   - Tekrarlayan hatalar: KAHİN müzakeresine ver
   - Sistem iyileştirme: Sonraki sprint'e ekle

5. **KAHİN Tavsiyesi İste (Gerekirse)**
   - Şu problemi çözmek için mimari değişiklik gerek: ...
   - Ajanlar N kez aynı hatayı yaptı, nedenini araştır
   - Çözüm süresi uzun, kritik görev olabilir

---

### Hedef: KAHİN'e Gelen Sorular Azalsın

Orkestratör hata/görüş/çözümü merkezi topla → karar ver → rapor et.
KAHİN yalnız stratejik karar ver (mimari, öncelik, proje sınırı).
```

---

## 7. Eleştiri & Geri Bildirim Portalı

Tasarımda iyileştirme, hata, veya soru varsa:

```bash
python scripts/ajan_chat.py bulgula \
  --konu "Tasarım Belgesi (D-192)" \
  --bulgu "CLI komutları çok, ac + guncelle 2 yeterli" \
  --link "data/orchestrator/AJAN-CHAT-SISTEM-TASARIMI-2026-09-23.md"
```

**Bulgular:**
- `data/orchestrator/ajan-chat-bulgular.jsonl`'ye yazılır (append-only)
- İhsan'a tetik düşer: `CH-BULGULAR-TASARIM`
- Tasarım gözden geçirilir ve revize edilir
- Karar Defteri'ne D-192.revize kaydı düşer

---

## 8. Phase 2 (Başarılı Olursa)

**Aktivasyon Koşulu:** 2 hafta + 10+ gerçek sorun + 20+ çözüm + widget aktif kullanım

→ Evrimleştir:
- SQLite migration (indexleme)
- Thread başlıkları (konuşma gruplayıcı)
- Analytics: çözüm süresi, ajan katkısı, hata trendi
- Real-time WebSocket (instant bildirim)

---

## 9. AGENTS.md Güncellemesi (D-192)

```markdown
## Ajan Chat Sistemi (D-192 — KAHİN kararı 2026-09-23)

- **JSONL:** `data/orchestrator/ajan-chat.jsonl` (append-only)
- **Yapı:** sorun (1-200 char) + çözüm (1-300 char) + durum (acik|cokundurmus|cozuldu)
- **CLI Phase 1:** `python scripts/ajan_chat.py ac|guncelle|kapat|oku|ozet`
- **CLI Phase 1+:** `python scripts/ajan_chat.py bulgula` (görüş/eleştiri)
- **Lock:** D-68 mekanizması; concurrent append safe
- **Tetikler:** Problem açılınca → ihsan CH-PROBLEM-{task_id}
- **Eleştiri:** ajan_chat.py bulgula → data/orchestrator/ajan-chat-bulgular.jsonl
- **Dashboard:** Admin panel chat widget (3 metrik + son 3 sorun)
- **Orkestratör Rutini:** Günlük 15 min — açık sorunlar + bulgular + haftalık karar
- **Phase 2:** SQLite + threads + analytics (2 hafta + 10+ problem + 20+ çözüm olursa)
```

---

## 10. Başlangıç Adımları

1. ✅ Bu belge yazıldı (D-192) — güncellendi (bulgula + orkestrator rutini)
2. ⏳ `scripts/ajan_chat.py` kodlanacak (CLI ac/guncelle/kapat/oku/ozet + bulgula)
3. ⏳ `src/company_master/chat.py` kütüphanesi (append + lock)
4. ⏳ `tests/test_ajan_chat.py` testleri
5. ⏳ `trigger.py` entegrasyon (rapor → chat.ac)
6. ⏳ Admin panel widget
7. ⏳ AGENTS.md D-192 kuralı
8. ⏳ Live test (3 sorun kaydı + 1 eleştiri)
9. ⏳ İhsan'a orkestratör rutini belgesi (15 min günlük)

---

## Tasarım Prensibi

**Lightweight + Açık + Feedback Loop + Orkestratör Merkezi:**
- JSONL: JSON oku, grep'le, tablo yap → kolay
- CLI: `ac` + `guncelle` + `kapat` + `oku` + `ozet` → 5 komut, 3 durum
- Bulgula: Ayrı komut, görüş/eleştiri merkezi toplama
- Tetikler: Problem açılınca ihsan'a → koordinasyon sağlanır
- Widget: 3 metric + son 3 sorun → görüş alanı 5 saniye
- Alıntı + Çözüm: Sorunu 1 cümle, çözümü 1-2 satır → hafif ve anlaşılır
- **Eleştiri Portalı:** Tasarımda hata bulunursa `bulgula` komutu ile geri bildirim → devam eden geliştirme
- **Orkestratör Merkezi:** Tüm sorun/çözüm/görüş merkezi → KAHİN tavsiyesi azalsın, karar hızlansın

Ajanlar **alıntı okuyup** çözüm **sunabilir**, orkestrator hata/görüş **topla** → karar ver → rapor et.

---

## Karar Kaydı

**D-192: Ajan Chat Sistemi (KAHİN kararı 2026-09-23, güncellendi 2026-09-23 revize 1)**

- Ajanlar sorunları alıntıla, çözüm yolları sun
- Merkezi JSONL log + CLI Phase 1 (ac/guncelle/kapat/oku/ozet) + bulgula (ayrı)
- D-68 lock mekanizması ile safe append
- Architect rapor → auto-problem tetik (ihsan'a)
- Admin panel widget: 3 metric + son 3 sorun
- Eleştiri portalı: ajan_chat.py bulgula komut
- **Orkestratör günlük rutini:** 15 min — açık sorunlar + bulgular + haftalık karar
- **KAHİN tavsiyesi azaltma hedefi:** Orkestrator merkezi → karar merkezleş → tavsiye ihtiyacı azal
- Başarılı olursa Phase 2 (2 hafta + 10+ problem + 20+ çözüm — SQLite + threads + analytics)

**Referanslar:** D-68 (Tetik ↔ Pano), D-66 (Brief), AGENTS.md § Görev Yaşam Döngüsü § Orkestratör Rol Geçişi (D-71)
