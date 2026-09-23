# İHSAN — D-66 Bypass Tetikleme Implementation

**Sprint:** SPRINT-2026-09-23-PANO-DENETIM  
**Tarih:** 2026-09-23  
**Sahip:** İHSAN  
**Başlangıç:** 2026-09-23T12:27:46Z  
**Durum:** plan  
**Aciliyet:** P0 (1-2 gün)

---

## KAHIN Kararı: D-66

**Karar:** Bypass tetikleme mekanizması (pano_denetim.py → tetik_senk.py)

**Problem:** 
- Pano denetimi sırasında reconfigure() hatası referans eski (sistem sağlam)
- 24+ saat blokaj durumunda exit 2 dönüş gerekli
- KAHİN elle tetiklemesi yapılamıyor (otomasyonu kısıtlanmış)

**Çözüm Seçeneği (a):**
1. pano_denetim.py tara() fonksiyonunda 24h+ blocked task tespit
2. Exit 2 dön (tetik_senk'e sinyal gönder)
3. tetik_senk.py exit 2 gördüğünde: AGENT_SYNC.md rapor satırı ekle
4. KAHİN rapor okur ve elle tetikler

---

## Implementation Adımları

### 1. pano_denetim.py Tara Fonksiyonu (30 min)

**Dosya:** src/company_master/orchestrator/pano_denetim.py

**Yapılacaklar:**
- `def tara(self):` fonksiyonuna blokaj detection kodu ekle
- 24+ saat blocked task varsa flag set et: `self.has_long_blocked = True`
- Return: `(total_tasks, completed, assigned, long_blocked=self.has_long_blocked)`

**Pseudokod:**
```python
def tara(self):
    blocked_tasks = []
    now = datetime.now(timezone.utc)
    
    for task in self.tasks:
        if task.status == 'blocked':
            blocked_since = datetime.fromisoformat(task.blocked_at)
            hours_blocked = (now - blocked_since).total_seconds() / 3600
            if hours_blocked > 24:
                blocked_tasks.append({
                    'task_id': task.id,
                    'hours_blocked': hours_blocked
                })
    
    self.has_long_blocked = len(blocked_tasks) > 0
    self.long_blocked_list = blocked_tasks
    
    return (len(self.tasks), self.completed_count, self.assigned_count)
```

**Test:** tests/test_pano_24h_blocked.py

---

### 2. tetik_senk.py Exit 2 Handler (30 min)

**Dosya:** src/company_master/orchestrator/tetik_senk.py

**Yapılacaklar:**
- Main çalıştırma fonksiyonu sonuna exit handler ekle
- pano_denetim.has_long_blocked == True ise: exit 2 dön
- Exit öncesi: AGENT_SYNC.md'ye rapor satırı yaz

**Pseudokod:**
```python
def main():
    pano = PanoDenetim()
    total, completed, assigned = pano.tara()
    
    # ... normal işlemler ...
    
    if pano.has_long_blocked:
        log_to_agent_sync(
            f"[{datetime.now().isoformat()}] Exit 2: {len(pano.long_blocked_list)} "
            f"task(s) blocked >24h. Requires manual trigger."
        )
        sys.exit(2)
    
    sys.exit(0)
```

**Test:** tests/test_tetik_senk_exit2.py

---

### 3. AGENT_SYNC.md Rapor Entry (20 min)

**Dosya:** Huginn Data Insights/AGENT_SYNC.md

**Yapılacaklar:**
- Bilgi: tetik_senk exit 2 durumunda otomatik rapor satırı eklenecek
- Format:
```
## [2026-09-23 12:XX:XX] Tetik Exit 2 — Manual Trigger Required
- Blocked Tasks: N
- Hours Blocked: avg XX.X h
- Status: KAHIN handle needed
- Action: Manually run: npx --yes n8nac push
```

---

### 4. Test Suite (1 saat)

**Dosyalar:**
- tests/test_pano_24h_blocked.py
- tests/test_tetik_senk_exit2.py

**Test Senaryoları:**
1. Blocked task < 24h: exit 0 (normal)
2. Blocked task = 24h: exit 2 (boundary)
3. Blocked task > 24h: exit 2 (trigger)
4. Multiple blocked: exit 2 + all in AGENT_SYNC
5. No blocked: exit 0 (normal)

**Assertion:**
- Exit code correct
- AGENT_SYNC.md updated
- Log entries clean (no errors)

---

### 5. AGENTS.md D-66 Karar Entry (15 min)

**Dosya:** Huginn Data Insights/AGENTS.md

**Yapılacaklar:**
- D-66 karar satırını ekle (D-182, D-190 sonrası)
- Format:

```markdown
### D-66: Bypass Tetikleme Mekanizması (2026-09-23)

**Problem:** 24+ saat blocked task durumunda KAHİN elle tetiklemesi imkansız.

**Karar:** pano_denetim.tara() → blocked >24h tespit → exit 2 → tetik_senk AGENT_SYNC raporla.

**Implementer:** İHSAN (2026-09-23)

**Status:** ✅ Done (2026-09-23)

**Files:**
- src/company_master/orchestrator/pano_denetim.py (tara() updated)
- src/company_master/orchestrator/tetik_senk.py (exit 2 handler)
- tests/test_pano_24h_blocked.py (new)
- tests/test_tetik_senk_exit2.py (new)

**Related:** D-182 (ajan tanım), D-190 (architect rapor)
```

---

## Bağlamsal Bilgi

**Pano Denetimi:** 2026-09-23 12:15-12:27
- 377 görev sınıflandırıldı
- 6 görev atandı (UTKU 3, YASU 3)
- Sistem sağlık: ✅ Tümüyle
- Reconfigure() error: Eski referans (zararsız)

**MIMIR Revizyon:** D-66 bypass strategy ✅
- Orchestrator asistanı, Seviye 1
- Tetikleme mekanizması doğru
- Logging + manual fallback eklenmeli

**D-66 Öncelliği:** P0 → 1-2 gün içinde yapılacak

---

## Sprint Hedefiniz

✅ D-66 bypass implementation (bu task)  
✅ Test suite (4+ test case)  
✅ AGENTS.md karar entry  
✅ Rapor + commit

**Tahmini Süre:** 2-3 saat (paralel UTKU/YASU görevleri ile)

---

## İletişim

Sorun/Bloker: `data/orchestrator/D-66-BYPASS_rapor_2026-09-23_ihsan.md` dosyasına not ekle.

