# ORKESTRA-DUPLIK-KAPAYANIM-01 Brif

**Görev:** [ORKESTRA] Çakışan görevleri araştır → bulgu raporu (30m)

## İş Maddeleri

1. **ADMIN-UX-MENUTREE-01 (plan, ihsan)** ve **UI-MENUTREE-02 (done, utku)** arasında çakışma var. Her ikisi de dosya hedefi `web_dashboard/tabs/__init__.py` aynı.
   - ADMIN-UX-MENUTREE-01: "Sol menu agaci yeniden gruplama; Ayarlar sekmesi menuden kalkar" (plan durumunda, basladı ama bitirilmedi)
   - UI-MENUTREE-02: done (utku teslim etti mi? task_board kontrol et)
   
2. **Araştır:** task_board.json'da her iki görev var mı? İkisinin de durum/tarihini oku.

3. **Karar ver:**
   - Eğer UI-MENUTREE-02 done ise → ADMIN-UX-MENUTREE-01 stale, arşivle (iptal + not yaz: "UI-MENUTREE-02 tarafından yapıldı")
   - Eğer ikisi de aktif ise → çakışma var, raporla: kim kimi override ediyor, hangi dosya güncel
   - Eğer ikisi de plan ise → aynı işi mi yoksa farklı mi? Raporla

4. **Rapor yaz:** `data/orchestrator/ORKESTRA-DUPLIK-KAPAYANIM-01_rapor_2026-09-20_denetim.md`
   - Ne bulundu (çakışma tipi: duplicate/stale/conflict)
   - Alınan karar (iptal/arşiv/merge)
   - task_board.json tarafında yapılacak işlem

## Sonuç Dosyası

- Rapor: `data/orchestrator/ORKESTRA-DUPLIK-KAPAYANIM-01_rapor_2026-09-20_denetim.md`
- task_board.json'a "not" alanı güncelle (stale görev iptal ise)
- Yeni görev açılmadı

## Test Komutu

```bash
python -X utf8 -c "import json; tasks = json.load(open('data/orchestrator/task_board.json')); menutree = [t for t in tasks if 'MENUTREE' in t.get('task_id','')]; print(f'Bulundu: {len(menutree)} görev'); [print(f\"  {t['task_id']}: {t['durum']}\") for t in menutree]"
```
