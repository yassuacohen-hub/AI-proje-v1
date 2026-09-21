# BRIF-03: Copilot Mimari Kararları Okuyup Öneriler Yaz

## Görev Özeti
`AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md` dosyasında yer alan mimari kararları oku, henüz uygulanmayan önerileri tespit et ve kritik gözlemler yaz.

## Çıktı
`data/orchestrator/BRIF-03_rapor_<tarih>_ihsan.md` dosyasına D-55 formatında rapor:
- **Ne yapıldı:** Mimari belge okundu, bölüm başlıkları ve kararlar özet edildi
- **Değişen dosyalar:** Sadece rapor dosyası
- **Test sonuçları:** N/A (araştırma görevi)
- **Bulgular:** Uygulanmayan 3+ karar, risk analizi, implementasyon sırası önerisi
- **Eksik / erteleme:** Varsa not düşülsün

## Kurallar
- D-55: Rapor 5 başlık zorunlu, Bulgular boş bırakılamaz
- D-184: Rapor içinde `[[D-XX]]` wikilink'leri (kararlar için)
- D-183: Dosya adı `_ihsan` sonekli

## Kendi Sahibi
**SALİH** — otomatik onay (D-78, P1)

## Teslim
```bash
python scripts/gorev_kutusu.py teslim --task-id BRIF-03 --rapor data/orchestrator/BRIF-03_rapor_2026-09-21_ihsan.md
```

## Test
```bash
python -c "import json; d=json.load(open('data/orchestrator/task_board.json')); g=[x for x in d if x['task_id']=='BRIF-03'][0]; print('Durum:', g['durum'], '| Sahip:', g['sahip'])"
```
