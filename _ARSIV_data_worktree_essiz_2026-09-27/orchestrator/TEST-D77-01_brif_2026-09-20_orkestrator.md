# TEST-D77-01 Brifi — Pano İşleri Orkestrator'a Aittir (D-77 Test Görev)

## Görev Özet
Orkestrator rolünün merkez konumundaki sorumluluk alanlarını test etmek ve D-77 kuralının işlevselliğini doğrulamak. Bu görev, pano bakım işleri, kilit yönetimi ve görev dağıtımına dair temel kontrol noktalarını sağlar.

## Çalışma Maddeleri

### 1. Kilit Disiplini Denetimi
- [ ] `data/orchestrator/file_locks.json` dosyasını taramalı ve düzeltilmesi gerekli kayıtları tespit etmeli.
- [ ] "sahip" alanı "orkestrator" olan tüm kilitler kontrol edilmeli (D-77 tarafında tüm bakım işleri orkestrator'a ait).
- [ ] Ortak dosyaların (`file_locks.json`, `task_board.json`, `decision_log.jsonl`, `bulgu_defteri.md`) kilit durumunun doğru olduğundan emin olmalı.
- [ ] Tespit edilen kilit çakışmaları ve stale kilitleri `scripts/duzen.py::cakisirma_analizi()` ile taramalı.

### 2. Pano Bakım Operasyonu
- [ ] `data/orchestrator/task_board.json` JSON yapısını `python -m json.tool` ile doğrulamalı.
- [ ] Tüm görevlerin `task_id`, `sahip`, `baslik`, `oncelik` alanları dolu olmalı (ZORUNLU_ALANLAR şeması).
- [ ] Durumu `plan` ama ajan_alma_tarih'i null olmayan görevler tespit edip düzeltmeli.
- [ ] Yapısız/malformed görevler varsa `pano_normalize()` ve `sema_dogrula()` ile temizlemeli.

### 3. Tetik-Pano Tutarlılığı (D-68)
- [ ] Tetik dosyalarındaki (triggers/*.jsonl) tüm görevler pano'da var mı? Yoksa D-68 tutarsızlığı raporla.
- [ ] Ajan postasındaki bekleyen tetikler (`durum: bekliyor`) pano ile eşleşmeli. İtici tetik yok ama pano'da görev var durumları bul.
- [ ] `scripts/duzen.py::pano_bakim()` çalıştırıp otomatik demote işlemlerini logla.

### 4. Görev Zinciri İntegrasyonu Doğrulama
- [ ] Pano'da `zincir` alanı olan görevleri tara (örn. MALIYET-P7-MON-01 → MALIYET-P7-MON-02 → ...).
- [ ] Zincirdeki tamamlanmış görevler (`durum: done`) bir sonraki görevi tetiklemeli. Tetik düştü mü kontrol et.
- [ ] Zincir bekleme durumundaki görevleri (`zincir_bekleme`) bul ve sonraki görev beklenmesi gerekiyorsa onaylı mı? Uyum denetle.

### 5. Orkestrator Devralma Mekanizması (D-58) Kontrol
- [ ] `data/orchestrator/orchestrator.json` dosyası var ve mevcut orkestrator (`ajan` alanı) "ihsan" mı?
- [ ] Anahtar parmak izi (`anahtar_parmak_izi`) SHA256 formatında mı?
- [ ] Yanlış anahtar test: `python scripts/gorev_at.py abrakadabra --ajan utku --anahtar yanlisbir` komutunun `exit 4` döndürmesi gerekir.

## Doğrulama ve Kontroller (Self-Check)

**JSON Yapısı Doğrulama:**
```bash
python -X utf8 -m json.tool data/orchestrator/task_board.json > /dev/null && echo "✓ pano JSON valid" || echo "✗ pano JSON hata"
python -X utf8 -m json.tool data/orchestrator/file_locks.json > /dev/null && echo "✓ locks JSON valid" || echo "✗ locks JSON hata"
```

**Kilit Disiplini Kontrolü:**
```bash
python -c "
import json; 
locks = json.loads(open('data/orchestrator/file_locks.json').read());
orkes_locks = [f for f,d in locks.items() if d.get('sahip')=='ihsan'];
print(f'✓ Orkestrator kilitli dosyalar: {len(orkes_locks)} adet');
"
```

**Pano Doğruluğu:**
```bash
python -X utf8 -c "
from src.company_master.orchestrator import task_board as tb;
tum = tb.gorev_listesi();
plan = [t for t in tum if t['durum']=='plan'];
print(f'✓ Pano: {len(tum)} görev, {len(plan)} plan durumda')
"
```

**Tetik-Pano Tutarlılığı (D-68 Doğrulaması):**
```bash
python -c "
from src.company_master.orchestrator import trigger, task_board as tb;
ajanlar = ['ihsan','utku','salih','yasu'];
for a in ajanlar:
    tet = trigger.bekleyen_tetikler(a);
    if tet:
        for t in tet:
            g = tb.gorev_getir(t['task_id']);
            if not g:
                print(f'✗ {a}/{t[\"task_id\"]}: pano'da YOK (D-68 tutarsızlığı)');
            elif g.get('sahip') != a:
                print(f'✗ {a}/{t[\"task_id\"]}: pano'da başka ajan {g.get(\"sahip\")}');
print('✓ Tetik-pano tutarlılığı doğrulandı')
"
```

**Zincir Operasyonları:**
```bash
python -c "
import json; b = json.loads(open('data/orchestrator/task_board.json').read());
zincirli = [t for t in b if t.get('zincir')];
print(f'✓ Zincirli görevler: {len(zincirli)} adet');
for t in zincirli[:3]:
    nxt = t.get('zincir',{}).get('sonraki');
    print(f'  {t[\"task_id\"]} -> {nxt}')
"
```

**Orkestrator Durumu:**
```bash
python -c "
import json;
import pathlib;
ork = json.loads(pathlib.Path('data/orchestrator/orchestrator.json').read_text());
print(f'✓ Mevcut orkestrator: {ork.get(\"ajan\")}');
print(f'✓ Devralma tarihi: {ork.get(\"devralma_zamani\")}');
"
```

## Beklenen Sonuç

1. ✅ Tüm JSON yapıları valid
2. ✅ Kilit durumları doğru, stale lock yok
3. ✅ Pano görevleri şema uyumlu
4. ✅ Tetik ve pano tutarlı (D-68 ihlali yok)
5. ✅ Zincir görevleri sırada ve tetikleme doğru
6. ✅ Orkestrator merkezi yönetimi çalışıyor
7. ✅ D-77 kuralı uygulanıyor (pano işleri = orkestrator işi)

## Raporlama
Görev bitince `data/orchestrator/TEST-D77-01_rapor_2026-09-20_orkestrator.md` yazmalı:
- Ne yapıldı (5 madde özeti)
- Değişen dosyalar
- Test sonuçları (6 kontrol noktası)
- Bulgular (D-55 renk sınıfı)
- Eksik/Erteleme
