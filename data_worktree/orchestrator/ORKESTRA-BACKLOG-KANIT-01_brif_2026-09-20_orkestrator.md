# ORKESTRA-BACKLOG-KANIT-01 Briefi

## GÖREV TANIMI
Bu turda backlog'a iki yanlış iş kaydı düştü (5 ve 6 numaralı madde, sözleşmeye göre):
- "ALTYAPI-WEB-MONITOR-01 bozuk JSON" — araştırıldı, JSON geçerli, yanlış kayıt.
- "4 talimatsız brif tespit" — araştırıldı, talimat alan bulunamadı, yanlış kayıt.

**Kök neden:** backlog_maddelerine kanıt satırı (dosya + satır no) yazılmamış → ajanlar gerçek olmayan işi kovaladı, zaman harcandı.

## İŞ MADDELERİ

1. **AGENTS.md D-66 sezione (Brifsiz Atama Yasak) güncelle:** backlog kuralı ekle
   - Kural: Backlog'a görev kaydeden her madde mutlaka `kanıt: <dosya>:<satır>` alanı taşıyacak.
   - Kanıt olmayan görev panoya **girilmez** (pano_bakim() kontrol eder).
   - Kontrol komut: `scripts/backlog_validate.py` yaz (ZORUNLU alan: `kanit`)
   
2. **`data/orchestrator/task_board.json` şemaya kanıt alanı ekle:**
   - Şema: `kanit: "data/orch.md:15"` formatında
   - Varolan backlog maddelerine retroaktif kanıt ekle (git history'den veya raporlardan çıkar)

3. **`scripts/gorev_at.py at` komutu güncelleştir:**
   - Backlog madde oluştururken kanıt parametre zorunlu: `--kanit "dosya:satır"`
   - Kanıt parametre boş ise hata + exit 1

4. **Backlog_defteri.md (D-67 bulgu tablosu) kanıt sütunu ekle:**
   - Bulgu her satırda: `kanit` alanına sahip görev ID yalnız kaydedilir.

## KENDİ-KONTROL

```bash
# 1. Şema doğrulaması
python -m pytest tests/test_backlog_kanit_schema.py -q

# 2. Retroaktif kanıt verisi
grep -n "ALTYAPI-WEB-MONITOR-01" data/orchestrator/task_board.json
# Output: 5213-5239 satırında yer almalı, kanıt alanı eksik bulunmalı

# 3. Komut testi
python scripts/gorev_at.py at --task-id TEST-KANIT-01 --ajan utku --baslik "TEST KANIT" --kanit ""
# Should fail with "kanit gerekli" mesajı

python scripts/gorev_at.py at --task-id TEST-KANIT-02 --ajan utku --baslik "TEST KANIT" --kanit "data/orch.md:100"
# Should succeed

# 4. Pano bakım testi
python scripts/gorev_kutusu.py pano-bakim
# Kanıt olmayan madde sil veya uyar
```

## BEKLENEN ÇIKTI
- `AGENTS.md` D-66 güncellendi, kuralı oku
- `task_board.json` şema = `kanit` alanı.
- `scripts/backlog_validate.py` mevcut, doğrulama kodu çalışıyor.
- Test dosyası `tests/test_backlog_kanit_schema.py` yeşil.
- Varolan backlog maddeleri kanıt veri taşıyor.
- `gorev_at.py` kanıt parametresi enforseı çalışıyor.
