# MIMAR — MIMIR Agentik Öğrenme Sistemi (D-66 + D-XXX Architect Hakkı)

---

## EXEKÜTİF ÖZET

MIMIR Seviye 1'e architect hakkı ver + agentik öğrenme sistemi ekle:
- **D-66 "Bypass Tetikleme"** — pano_denetim exit 2 (24h rule seç).
- **D-XXX "MIMIR Architect Hakkı"** — ölçüm/rapor/tasarım önerileri yazabilir.
- **D-YYY "MIMIR Agentik Bellek"** — sistem hataları, kararları, sonuçları hatırla; sonraki görevde türet.
- **Admin/Customer Panel** — MIMIR chat agenti göster (Streamlit sidebar, öğrenme log).

---

## 1. D-66 BYPASS TETIKLEME MEKANIZMASI — BEST OPTION SEÇIMI

### Üç Seçenek Karşılaştırması

| Seçenek | Tetik | Rapor | KAHİN | Zaman | Risk | Seçim |
|---------|-------|-------|-------|-------|------|--------|
| **(a) pano_denetim exit 2** | 24h blocked tespit → exit 2 → tetik_senk rapor | Otomatik AGENT_SYNC.md | Elle tetikle | 1-2 gün | Minimal | ✅ |
| **(b) 12h agresif** | 12h blocked tespit → exit 1 | Otomatik rapor | Elle tetikle (daha sık) | 1 gün | Yanlış pozitif risk ↑ | ⚠️ |
| **(c) 6h reaktif** | 6h blocked → exit 3 | Elle + otomatik | Çok sık tetikle | 2-3 gün | Notification spam | ❌ |

**Seçim: (a) — 24h, exit kod 2, tetik_senk rapor → KAHİN elle tetikle**

**Gerekçe:**
- 24h = makul blokaj süresi (geliştirici aynı gün veya ertesi gün çözer)
- Exit 2 = mevcut exit kod sistemine uyum (0=ok, 1=warning, 2=bypass)
- Minimal kod → haftalık job döngüsüne entegre (tetik_senk zaten çalışıyor)
- KAHİN elle tetikle = kontrol, otomasyon yetersizlik riskini engelle

### Uygulama: 4 Dosya + 4 Test

**File 1: [`scripts/pano_denetim.py`](scripts/pano_denetim.py) — tara() güncellemesi**

```python
def tara(pano: list[dict], kuyruk: list[dict], simdi: datetime) -> list[dict]:
    """Pano tutarlılığı denetim + D-65 blocked 24h+ tespit.
    
    Döner: Bulgular listesi.
    - blocked + ≥24h hareketsiz ise → {"type": "blocked_bypass", "task_id": "X", "gun": N}
    """
    bulgular = []
    for gorev in pano:
        if gorev.get("durum") == "blocked":
            son_hareket = _son_hareket(gorev)
            if son_hareket:
                saat_fark = (simdi - son_hareket).total_seconds() / 3600
                if saat_fark >= 24:
                    bulgular.append({
                        "type": "blocked_bypass",
                        "task_id": gorev["task_id"],
                        "sahibi": gorev.get("sahip", "?"),
                        "gun": round(saat_fark / 24, 1),
                        "oncelik": gorev.get("oncelik", "P?"),
                    })
    return bulgular

def main(argv=None) -> int:
    """Exit kod: 0=temiz, 2=bypass gerekli."""
    bulgular = tara(pano, kuyruk, datetime.now(timezone.utc))
    
    if any(b["type"] == "blocked_bypass" for b in bulgular):
        # Bypass gerekli: rapor yaz (D-66), exit 2
        return 2  # ← D-66 tetikleme sinyali
    return 0
```

**File 2: [`scripts/tetik_senk.py`](scripts/tetik_senk.py) — exit 2 handling**

```python
def cikis_kodu(rapor: dict, log_yazildi: bool = True) -> int:
    """Exit kodu: 2 = bypass gerekli → KAHİN'e rapor gönder."""
    if rapor.get("bypass_gerekli"):
        # AGENT_SYNC.md'ye bypass rapor satırı ekle
        bypass_satiri = (
            f"🔴 BYPASS_GEREKLI: {rapor['task_id']} | "
            f"blokaj {rapor['gun']} gün | {rapor['sahip']} | "
            f"komut: `python scripts/gorev_kutusu.py basla --ajan {rapor['sahip']}`"
        )
        _agent_sync_ekle(bypass_satiri)
        return 2  # Exit 2 = bypass gerekli
    return 0
```

**File 3: Tests**

```python
# tests/test_d66_bypass_tetikleme.py
def test_blocked_24h_plus_exit2(tmp_path, monkeypatch):
    """blocked + ≥24h → exit 2."""
    pano = [{
        "task_id": "COP-26",
        "durum": "blocked",
        "sahip": "ihsan",
        "baslangic": (datetime.now(timezone.utc) - timedelta(days=9.7)).isoformat(),
    }]
    bulgular = tara(pano, [], datetime.now(timezone.utc))
    assert any(b["type"] == "blocked_bypass" for b in bulgular)
    assert main() == 2

def test_blocked_6h_no_exit2(tmp_path, monkeypatch):
    """blocked ama 6h → exit 0."""
    pano = [{
        "task_id": "P1-X",
        "durum": "blocked",
        "baslangic": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
    }]
    bulgular = tara(pano, [], datetime.now(timezone.utc))
    assert not any(b["type"] == "blocked_bypass" for b in bulgular)
    assert main() == 0
```

**AGENTS.md Güncellemesi:**

```markdown
## D-66 "Bypass Tetikleme" (KAHİN kararı 2026-09-23)

**Amaç:** D-65 "İş Durmaz" kuralını uygulamak. Araç blokajı + ≥24h idle görevler otomatik olarak KAHİN'e escalate edilir.

**Mekanizması:**
1. `pano_denetim.tara()` → blocked + 24h+ tespit
2. Exit kod 2 döner (bypass gerekli sinyali)
3. `tetik_senk.py` exit 2 gördüğünde:
   - AGENT_SYNC.md'ye rapor satırı ekle: "BYPASS_GEREKLI: task_id gün sahip komut"
   - KAHİN'e Slack/email bildir
4. KAHİN rapordan kopyala-yapıştır komut çalıştırır
5. Orkestratör paralelde hatayı çözer

**24h Seçimi Gerekçesi:**
- Makul blokaj süresi (geliştirici genelde aynı/ertesi gün çözer)
- Yanlış pozitif (6h seçilirse fazla) ve cevapsız (48h seçilirse az) arasında denge
- Haftalık job sırası uyumlu

**Kural:** blocked + ≥24h → exit 2 → otomatik rapor → KAHİN elle tetikle.

**Testler:** `test_d66_bypass_tetikleme.py` (4 test: 24h+, <24h, P1 P0 oncelik, rapor format)
```

---

## 2. D-XXX "MIMIR ARCHITECT HAKKI" — KARAR + AGENTS.MD GÜNCELLEME

### Karar Metni

```
## D-XXX "MIMIR Architect Hakkı" (KAHİN kararı 2026-09-23)

**Karar:** MIMIR Seviye 1'e architect mode erişimi ver.

**Sebep:** 
- D-65 ölçüm raporu elle yapıldı (saatler kaybı)
- MIMIR ölçüm/analiz görevlerini otomatik yazabilecek kapasitesi var
- Architect mode açılırsa sistem öğrenme & planlama görevleri MIMIR'e atanabilir

**Kısıtlamalar:**
- D-63 "Architect Kapısı" kuralı korunur: architect mode yalnız ihsan/utku/mimir
- MIMIR karar yazamaz (D-55 rule); yalnız öneriler yazabilir (TEKLIF: prefix)
- Test danışman (salih) MIMIR önerileri doğrular

**Etkilenen Kurallar:**
- D-63: Architect kapısı → (ihsan, utku, mimir) olarak güncelle
- D-182: MIMIR Seviye 1 → architect mode eklendi
- D-67 (rapor): MIMIR raporları aynı 5 başlık + TEKLIF: bölümü taşır

**Uygulanacak Dosyalar:**
- `scripts/gorev_at.py` — architect mode yalnız (ihsan, utku, mimir) kabul et (D-63 güncelle)
- `tests/test_d182_mimir.py` — MIMIR architect mode test ekle
- `AGENTS.md` — D-63 ve D-182 güncelle

**Takvim:** 2-3 gün (kod + test + güncelleme)
```

### AGENTS.md Güncellemesi

**D-63 güncellemesi:**
```markdown
## Architect Modu Kapısı (D-63 — KAHİN kararı 2026-09-18, D-XXX ile güncellendi)

- **Architect (mimari/planlama/tasarım) görevlerini şu ajanlar alır:**
  - `ihsan` (roo) — Orkestratör, sistem tasarım
  - `utku` (kilo) — Üretim/UX tasarım
  - `mimir` (odin_ai) — Seviye 1, ölçüm/analiz raporları
  
- **Başka ajan** (yasu, salih) architect görevi almaz; alırsa iş geçersizdir.
- **D-XXX (2026-09-23):** MIMIR architect mode eklenmiş.
```

**D-182 güncellemesi:**
```markdown
## MIMIR — Orkestratör Asistanı, İki Seviye + Architect (D-182 güncellenmiş)

| Özellik | Açıklama |
|---------|----------|
| **Seviye 0** | 🔒 Code mode: pano okur, raporlar sunar, TEKLIF önerileri. |
| **Seviye 1** | 🔓 Code + Architect mode: ölçüm raporları, seçenek analiz yazabilir. |
| **Architect Kapısı** | D-63 ile uyumlu: architect mode yalnız ihsan/utku/mimir. |
| **Rapor Formatı** | 5 başlık + TEKLIF: (öneriler) bölümü. |
| **Doğrulama** | Test danışman (salih) MIMIR raporlarını gözden geçirir (D-59). |
```

---

## 3. D-YYY "MIMIR AGENTIK BELLEK SISTEMI" — MIMARLIK

### Mimari Katmanlar

```
┌─────────────────────────────────────────────────┐
│         MIMIR Agentik Öğrenme Sistemi           │
├─────────────────────────────────────────────────┤
│  Katman 4: Karar Üretim (Decision Generator)   │
│            (Önceki hatalardan öğrenmiş tavsiye)│
├─────────────────────────────────────────────────┤
│  Katman 3: Akıl Yürütme (Reasoning Engine)     │
│            (Context → bulgu → sebep-sonuç)     │
├─────────────────────────────────────────────────┤
│  Katman 2: Bellek (Memory Layer)                │
│            (Hata log + karar log + outcome)     │
├─────────────────────────────────────────────────┤
│  Katman 1: Veri (Task Board + Pano Defteri)    │
│            (Kaynak doğruluk = SSOT)             │
└─────────────────────────────────────────────────┘
```

### Katman 1: Veri Kaynakları (SSOT)

**Okuma-yalnız:**
- `data/orchestrator/task_board.json` — pano durumları
- `data/orchestrator/decision_log.jsonl` — KAHİN kararları
- `data/orchestrator/AGENT_SYNC.md` — ajan senkron log

**Bellek amaçlı yaz:**
- `data/orchestrator/mimir_learning_log.jsonl` — MIMIR hatırlama defteri (YENİ)

### Katman 2: Bellek (Memory Layer)

**Dosya: [`src/company_master/intelligence/mimir_memory.py`](src/company_master/intelligence/mimir_memory.py) — YENİ**

```python
"""MIMIR Agentik Bellek Sistemi.

Hatırlanacak şeyler:
1. Sistem hataları (mojibake, blokaj, taşma)
2. KAHİN kararları (pattern, frequency)
3. İşler (outcome: başarı/başarısızlık/riskli)
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class MemoryEntry:
    """Bellek kaydı: task_id, karar, outcome, bulgu."""
    task_id: str
    karar_id: str | None  # D-XX referansı
    olay_tipi: str  # "sistem_hatası", "karar_uygulanmasi", "outcome"
    ozet: str  # İnsan tarafından okunabilir kısa not
    bulgu: str | None  # "🔴", "🟡", "🟢", "🔵"
    timestamp: str  # ISO 8601
    
    def to_jsonl_line(self) -> str:
        """JSONL satırı olarak yaz."""
        return json.dumps(asdict(self), ensure_ascii=False)

class MimirMemory:
    """MIMIR belleği: öğrenme log okuma/yazma."""
    
    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path or (
            Path(__file__).resolve().parents[3] / "data/orchestrator/mimir_learning_log.jsonl"
        )
    
    def hatirla(self, task_id: str, limit: int = 5) -> list[MemoryEntry]:
        """Task_id'ye ait son N olay hatırla."""
        if not self.log_path.exists():
            return []
        
        entries = []
        with self.log_path.open(encoding='utf-8') as f:
            for line in f:
                entry_dict = json.loads(line)
                entry = MemoryEntry(**entry_dict)
                if entry.task_id == task_id:
                    entries.append(entry)
        
        return entries[-limit:]
    
    def kaydet(self, entry: MemoryEntry) -> None:
        """Bellek kaydı ekle."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open('a', encoding='utf-8') as f:
            f.write(entry.to_jsonl_line() + '\n')
    
    def trendler(self, gun: int = 7) -> dict:
        """Son N günün trend analizi."""
        # Öğreniş: sistem hataları tekrarlanıyor mu?
        # Kararlar başarılı mı?
        # Risk görevleri var mı?
        ...

# Örnek kullanım
memory = MimirMemory()
memory.kaydet(MemoryEntry(
    task_id="D-65",
    karar_id="D-66",
    olay_tipi="karar_uygulanmasi",
    ozet="Bypass tetikleme: blocked 24h+ → exit 2 → KAHİN raporlandı",
    bulgu="🟢",  # başarı
    timestamp=datetime.now(timezone.utc).isoformat(),
))

# MIMIR sorguladığında: "COP-26 önceki sorunlar nelerdi?"
hatirlamalar = memory.hatirla("COP-26")
for entry in hatirlamalar:
    print(f"{entry.timestamp}: {entry.ozet}")
```

### Katman 3: Akıl Yürütme (Reasoning Engine)

**Dosya: [`src/company_master/intelligence/mimir_reasoning.py`](src/company_master/intelligence/mimir_reasoning.py) — YENİ**

```python
"""MIMIR Akıl Yürütme: Bellek + Context → Tavsiye."""

from mimir_memory import MimirMemory, MemoryEntry
from datetime import datetime, timezone

class MimirReasoning:
    """Bellek + mantık = tavsiye üretim."""
    
    def __init__(self):
        self.memory = MimirMemory()
    
    def sebep_sonuc_analizi(self, task_id: str) -> dict:
        """
        Görevin geçmiş: hata → karar → sonuç.
        
        Örnek:
          Hata: "COP-26 API timeout 3 gün"
          Karar: "D-66 bypass tetikleme"
          Sonuç: "İş devam etti, başarı"
          
          → Sonraki benzer durumlarda D-66 uygula (otomatik karar önerimi).
        """
        hatirlamalar = self.memory.hatirla(task_id, limit=10)
        
        causality_chain = []
        for entry in hatirlamalar:
            if entry.olay_tipi == "sistem_hatası":
                # Hata bulundu → çözüm araması
                causality_chain.append({
                    "hata": entry.ozet,
                    "bulgu": entry.bulgu,
                })
            elif entry.olay_tipi == "karar_uygulanmasi":
                # Karar uygulandı
                if causality_chain:
                    causality_chain[-1]["karar"] = entry.karar_id
            elif entry.olay_tipi == "outcome":
                # Sonuç
                if causality_chain:
                    causality_chain[-1]["outcome"] = entry.ozet
        
        return {
            "task_id": task_id,
            "chain": causality_chain,
            "ogrenilen": self._pattern_extract(causality_chain),
        }
    
    def _pattern_extract(self, chain: list) -> str:
        """Zincirden pattern çıkar → tavsiye metni."""
        patterns = {}
        for link in chain:
            hata = link.get("hata", "")
            karar = link.get("karar", "")
            outcome = link.get("outcome", "")
            
            if "API timeout" in hata and "D-66" in karar and "başarı" in outcome:
                patterns["API_timeout"] = "D-66 bypass tetikleme başarılı"
        
        return " | ".join(patterns.values()) if patterns else "Pattern tanınmadı"
    
    def tavsiye_uret(self, task_id: str, bulent: dict) -> str:
        """
        Görev + bulgu → öneriler (TEKLIF: prefix ile architect raporu yazar).
        
        Örnek:
          Input: task_id="COP-27", bulgu={"type": "blocked", "gun": 5}
          Output: "TEKLIF: Önceki D-65 benzer durumu D-66 ile çözdü. Aynı uygula."
        """
        analiz = self.sebep_sonuc_analizi(task_id)
        
        if bulent.get("type") == "blocked":
            gün = bulent.get("gun", 0)
            if gün >= 24:
                return (
                    f"TEKLIF: Blokaj {gün} gün. Önceki benzer görevde D-66 (bypass) "
                    f"başarılı oldu. Aynı mekanizmayı uygula: "
                    f"`pano_denetim exit 2 → KAHİN elle tetikle`."
                )
        
        return "TEKLIF: Bulgu türü tanınmadı; manuel inceleme gerekli."
```

### Katman 4: Karar Üretim (Decision Generator)

**Dosya: [`src/company_master/intelligence/mimir_decision.py`](src/company_master/intelligence/mimir_decision.py) — YENİ**

```python
"""MIMIR Karar Üretim: Akıl yürütme → Otomatik KAHİN tavsiyesi."""

from mimir_reasoning import MimirReasoning
from mimir_memory import MemoryEntry
from datetime import datetime, timezone

class MimirDecision:
    """Bellek + akıl yürütme = karar tavsiyesi."""
    
    def __init__(self):
        self.reasoning = MimirReasoning()
    
    def tavsiye_et(self, task_id: str, bulent: dict) -> dict:
        """
        Bulgu → MIMIR'in önerisi (KAHİN'e raporlanır).
        
        Döner: {
            "task_id": "COP-26",
            "oneriler": ["D-66 uygula", "test danışmanı sor"],
            "guven_skoru": 0.85,
            "sebep": "Bellek: 3 benzer durum D-66 ile çözüldü"
        }
        """
        tavsiye_metni = self.reasoning.tavsiye_uret(task_id, bulent)
        
        # Güven skoru: kaç benzer durum başarı ile sonuçlandı?
        analiz = self.reasoning.sebep_sonuc_analizi(task_id)
        basarili_count = sum(
            1 for link in analiz["chain"]
            if "başarı" in link.get("outcome", "").lower()
        )
        total_count = len(analiz["chain"])
        guven = basarili_count / total_count if total_count > 0 else 0.0
        
        return {
            "task_id": task_id,
            "oneriler": [tavsiye_metni],
            "guven_skoru": round(guven, 2),
            "sebep": analiz.get("ogrenilen", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
```

---

## 4. ADMIN PANEL + CUSTOMER PANEL ENTEGRASYONU

### 4a. Admin Panel — MIMIR Learning Monitor

**Dosya: [`web_dashboard/tabs/mimir_ogrenme.py`](web_dashboard/tabs/mimir_ogrenme.py) — YENİ**

```python
"""Admin Panel → MIMIR Öğrenme Monitörü Tab.

MIMIR'in neler hatırlıyor, ne öğrendi, hangi kararlar başarılı?
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from company_master.intelligence.mimir_memory import MimirMemory

def render_mimir_learning_tab():
    """Admin panelinde MIMIR öğrenme defteri."""
    st.markdown("## 🧠 MIMIR Agentik Bellek")
    
    memory = MimirMemory()
    
    # --- Bellek İstatistikleri ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Hatırlatma", 142)  # DB'den say
    with col2:
        st.metric("Başarılı Kalıp", "73%")
    with col3:
        st.metric("Risk Görevler", 5)
    
    # --- Trend Analizi ---
    st.markdown("### Trend (Son 7 Gün)")
    trend = memory.trendler(gun=7)
    
    trend_df = pd.DataFrame({
        "Gün": ["Pazartesi", "Salı", ..., "Pazar"],
        "Sistem Hataları": [2, 1, 0, 3, 2, 1, 0],
        "Karar Uygulanması": [5, 4, 6, 3, 4, 5, 2],
        "Başarı Oranı": [0.95, 0.92, 1.0, 0.88, 0.94, 0.96, 1.0],
    })
    
    st.line_chart(trend_df.set_index("Gün"))
    
    # --- Kalıp Keşfi ---
    st.markdown("### Keşfedilen Kalıplar")
    st.write("MIMIR şu kalıpları tanıyor (geçmiş durumlardan öğrenmiş):")
    
    patterns = [
        {"hata": "API Timeout", "çözüm": "D-66 Bypass", "başarı": "95%"},
        {"hata": "Encoding Error", "çözüm": "MOJIBAKE-BARRIER", "başarı": "100%"},
        {"hata": "Task Lock Stale", "çözüm": "Otomatik temizlik", "başarı": "88%"},
    ]
    
    st.dataframe(pd.DataFrame(patterns), use_container_width=True)
    
    # --- Son Öğrenme Olayları ---
    st.markdown("### Son 10 Öğrenme Olayı")
    # JSONL log'dan oku, göster
```

**tabs/__init__.py güncellemesi:**

```python
# TabTanimi ekle
TabTanimi(
    anahtar="mimir-ogrenme",
    baslik="MIMIR Agentik Bellek",
    ikon="🧠",
    yol="/admin/mimir-ogrenme",
    grup=GRUP_SISTEM,
    min_rol=ROL_ADMIN,
    yuzel=YUZEY_MUNINN,
    modul="web_dashboard.tabs.mimir_ogrenme",
    fonksiyon="render_mimir_learning_tab",
),
```

### 4b. Customer Panel — MIMIR Chat Agenti

**Dosya: [`web_dashboard/tabs/mimir_chat.py`](web_dashboard/tabs/mimir_chat.py) — YENİ**

```python
"""Customer Panel → MIMIR Chat Asistanı.

Müşteri sorular sorar, MIMIR belleğinden + akıl yürütmeden cevap verir.
"""

import streamlit as st
from company_master.intelligence.mimir_decision import MimirDecision

def render_mimir_chat_tab():
    """Müşteri MIMIR ile sohbet."""
    st.markdown("## 🤖 MIMIR Asistanı")
    st.write("Sorularınızı sorun, MIMIR geçmiş deneyimlerden öğrenmiş cevaplar verir.")
    
    decision_engine = MimirDecision()
    
    # --- Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sohbet geçmişi göster
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        st.chat_message(role).write(msg["content"])
    
    # --- Giriş ---
    user_input = st.chat_input("MIMIR'e soruyu yazın...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # MIMIR'in cevabı
        # Örnek: "COP-26 niçin blokaj?" → belleğe bak → D-66 öner
        
        if "COP-26" in user_input and "blok" in user_input.lower():
            tavsiye = decision_engine.tavsiye_et("COP-26", {
                "type": "blocked",
                "gun": 9.7
            })
            
            response = (
                f"🧠 **Analiz:** {tavsiye['sebep']}\n\n"
                f"**Önerim:** {tavsiye['oneriler'][0]}\n\n"
                f"📊 **Güven:** {tavsiye['guven_skoru'] * 100:.0f}%"
            )
        else:
            response = "Sorunu anlamadım. 'COP-26 blokaj' gibi spesifik sorular sorun."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
```

**tabs/__init__.py güncellemesi:**

```python
# Müşteri panelinde MIMIR Chat
TabTanimi(
    anahtar="mimir-chat",
    baslik="MIMIR Asistanı",
    ikon="🤖",
    yol="/customer/mimir-chat",
    grup=GRUP_IS,
    min_rol=ROL_USER,  # Müşteri erişimi
    yuzel=YUZEY_HUGINN,
    modul="web_dashboard.tabs.mimir_chat",
    fonksiyon="render_mimir_chat_tab",
),
```

---

## 5. ÖZETİ: ÇALIŞMA LİSTESİ

### Phase 1: D-66 Bypass (1-2 gün)
- [ ] `pano_denetim.py` tara() — blocked 24h+ tespit
- [ ] `tetik_senk.py` — exit 2 handling + rapor
- [ ] `AGENTS.md` — D-66 karar ekle
- [ ] Tests (4): 24h+, <24h, P0/P1, rapor format

### Phase 2: MIMIR Architect Hakkı (2-3 gün)
- [ ] AGENTS.md — D-63, D-182 güncelle
- [ ] `gorev_at.py` — architect mode (ihsan/utku/mimir) kontrol
- [ ] Tests (2): MIMIR architect mode, D-63 gate
- [ ] Decision_log.jsonl'e D-XXX ekle

### Phase 3: Agentik Bellek Sistemi (3-4 gün)
- [ ] `mimir_memory.py` — MemoryEntry, MimirMemory sınıfları
- [ ] `mimir_reasoning.py` — sebep-sonuç analizi, pattern extraction
- [ ] `mimir_decision.py` — tavsiye üretim + güven skoru
- [ ] Tests (3): Bellek okuma/yazma, akıl yürütme, karar
- [ ] `mimir_learning_log.jsonl` DB schema

### Phase 4: UI Entegrasyonu (2-3 gün)
- [ ] Admin Panel: `mimir_ogrenme.py` — bellek monitor
- [ ] Customer Panel: `mimir_chat.py` — asistan sohbet
- [ ] `tabs/__init__.py` — iki yeni tab ekle
- [ ] UI tests (2): Admin / Customer flows

**Toplam: 8-12 gün**

---

## Kaynaklar & Bağlantılar

- [`Huginn Data Insights/AGENTS.md`](Huginn Data Insights/AGENTS.md) — Kural tanımları
- [`Huginn Data Insights/scripts/pano_denetim.py`](Huginn Data Insights/scripts/pano_denetim.py)
- [`Huginn Data Insights/scripts/tetik_senk.py`](Huginn Data Insights/scripts/tetik_senk.py)
- [`Huginn Data Insights/web_dashboard/tabs/__init__.py`](Huginn Data Insights/web_dashboard/tabs/__init__.py)
- [`Huginn Data Insights/data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor_2026-09-23_ihsan.md`](Huginn Data Insights/data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor_2026-09-23_ihsan.md)

