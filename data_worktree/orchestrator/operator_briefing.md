# Operatör Bildirimi

**Tarih**: 2026-09-19 07:11:07 UTC

## Özet
Bu bildirim, orkestrasyon sisteminin mevcut durumu ve önerilen eylemleri içerir.

## Güncel Durum
- **Aktif Gruplar**: 1
- **Kritik Darboğazlar**: 1
- **Orta Darboğazlar**: 1

## Gruplar

### Grup: grup_ZN-01_1789801782
- **Üyeler**: salih, yasu, utku
- **Zincir ID**: ZN-01
- **Durum**: DEPLOYED
- **Oluşturma Zamanı**: 2026-09-19T07:09:42Z
- **Görevler**:
  - ADMIN-UX-PROFILMENU-01: AWAITING_TRIGGER
  - RESEARCH-PONYTALE: AWAITING_TRIGGER
  - ADMIN-UX-AYARLAR-SAYFA-01: AWAITING_TRIGGER
  - ADMIN-UX-MENUTREE-01: AWAITING_TRIGGER
  - REVIEW-ONAY-KUYRUGU-01: AWAITING_TRIGGER
  - UI-AYARLAR-SAYFA-01: AWAITING_TRIGGER
  - V10-BELGE-01: AWAITING_TRIGGER

## Darboğaz Analizi
### Kritik Darboğazlar
- **ihsan**: Puan 150.0 - Yüksek iş yükü (aktif/review görevi maksimum kapasitenin %70'ini aşiyor)
### Orta Darboğazlar
- **utku**: Puan 66.67 - Orta iş yükü (kapasitenin %40-%70 arası kullanılıyor)

## Önerilen Eylemler
- **ihsan**: Görevleri diğer ajanlara yeniden dağıt veya bekleyen görevleri ertele (Etki: İş yükü dengelemesi, darboğaz puanını düşürme, Hedef Puan: 30.0)
- **utku**: Görevleri diğer ajanlara yeniden dağıt veya bekleyen görevleri ertele (Etki: İş yükü dengelemesi, darboğaz puanını düşürme, Hedef Puan: 30.0)

## Planlanan Zincirler

### Zincir: ZN-01
- **Öncelik**: P0
- **Görev Sayısı**: 7
- **Atanan Grup**: grup_salih_yasu_utku_1789801742
- **Zincir Tipi**: seri
- **Risk Tamponu**: 30 dakika

## Metrikler
- **estimated_makespan_min**: 210
- **load_balance_variance**: 987.75
- **priority_adherence**: 0.29

## Eylem Talimatları
Dağıtımı başlatmak için aşağıdaki komutu çalıştırın:
```
python scripts/trigger_deployment.py --deployment-id deploy_20260919_001 --all --confirm
```
