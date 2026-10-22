#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
os_kontrol.py - OSB Veri Kontrol Scripti
VERI-OSB-HARITA-01 Görevi için Organize Sanayi Bölgeleri verilerini kontrol eder.

FONKSİYONEL:
- OSB listelerinden fiili durum extraction
- STRATEGI-A uyum kontrolü
- KVKK uyumluluğu validation
- RED Ground readiness check
"""

import json
import re
from typing import Dict, List, Optional


def load_onay_kuyrugu(path: str) -> Dict:
    """onay_kuyrugu.json dosyasını yükle"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_strateji_data(path: str) -> Dict:
    """strateji_data.json dosyasını yükle"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_fili_durum_from_text(text: str) -> Optional[str]:
    """
    Metin içinden fiili durum çıkar.
    Örnek değerler: KAMULAŞTIRMA YAPILIYOR, ALTYAPI HAZIRLANIYOR, İŞLETMEDE (FAALİYETTE)
    """
    # KAMULAŞTIRMA YAPILIYOR pattern'i
    kamula_pattern = r'KAMULAŞTIRMA YAPILIYOR'
    # ALTYAPI HAZIRLANIYOR pattern'i
    altyapi_pattern = r'ALTYAPI HAZIRLANIYOR'
    # İŞLETMEDE (FAALİYETTE) pattern'i
    isletme_pattern = r'İŞLETMEDE \(FAALİYETTE\)'
    
    if re.search(kamula_pattern, text):
        return 'KAMULAŞTIRMA YAPILIYOR'
    elif re.search(altyapi_pattern, text):
        return 'ALTYAPI HAZIRLANIYOR'
    elif re.search(isletme_pattern, text):
        return 'İŞLETMEDE (FAALİYETTE)'
    else:
        return None


def validate_red_grounds(onay_kuyrugu: Dict, strateji_data: Dict) -> Dict:
    """
    Tüm RED Ground'leri validate et ve sonucu döndür.
    """
    results = {
        'red_01_bayat_tespit': False,
        'red_02_strategi_secimi': False,
        'red_03_kvkk_uyumu': False,
        'overall_status': 'PENDING',
        'details': {}
    }
    
    # RED-01: Bayat veri tespiti (strateji A ile)
    strategi_secimi = onay_kuyrugu.get('secili_strateji', '')
    results['red_01_bayat_tespit'] = strategi_secimi == 'STRATEGI-A'
    results['details']['red_01'] = {
        'aciklama': 'Bayat veri tespiti strateji A ile yapıldı',
        'strategi': strategi_secimi,
        'status': 'CLEAR' if results['red_01_bayat_tespit'] else 'FAILED'
    }
    
    # RED-02: STRATEGI-A seçildi
    results['red_02_strategi_secimi'] = onay_kuyrugu.get('red_grounds', {}).get('red_02', {}).get('durum') == 'CLEAR'
    results['details']['red_02'] = {
        'aciklama': 'STRATEGI-A seçildi mi?',
        'strategi': strategi_secimi,
        'status': 'CLEAR' if results['red_02_strategi_secimi'] else 'PENDING'
    }
    
    # RED-03: KVKK uyumluluğu
    kvkk_uyumlu = onay_kuyrugu.get('red_grounds', {}).get('red_03', {}).get('kvkk_uyumlu', False)
    results['red_03_kvkk_uyumu'] = bool(kvkk_uyumlu)
    results['details']['red_03'] = {
        'aciklama': 'KVKK uyumlu validate edildi mi?',
        'kvkk_uyumlu': kvkk_uyumlu,
        'status': 'CLEAR' if results['red_03_kvkk_uyumu'] else 'FAILED'
    }
    
    # Genel status
    all_cleared = all([
        results['red_01_bayat_tespit'],
        results['red_02_strategi_secimi'],
        results['red_03_kvkk_uyumu']
    ])
    
    results['overall_status'] = 'APPROVED' if all_cleared else 'PENDING'
    
    return results


def check_osfi_durum_uyumu(onay_kuyrugu: Dict, strateji_data: Dict) -> Dict:
    """
    Fiili durum ile strateji uyumu kontrolü.
    """
    uyanma_durumlari = {
        'KAMULAŞTIRMA YAPILIYOR': ['PLANLAMA AŞAMASINDA', 'ALTYAPI HAZIRLANIYOR'],
        'ALTYAPI HAZIRLANIYOR': ['PLANLAMA AŞAMASINDA', 'ALTYAPI HAZIRLANIYOR'],
        'İŞLETMEDE (FAALİYETTE)': ['FAALİYETTE']
    }
    
    selected_strategy = onay_kuyrugu.get('secili_strateji', '')
    uyum_sonuçları = []
    
    # Strateji verilerinden fiili durumları kontrol et
    stratejiler = strateji_data.get('stratejiler', [])
    for strateji in stratejiler:
        stradi_adi = strateji.get('adi', '')
        fili_durum = strateji.get('fili_durum', '')
        
        uyum_kriterleri = uyanma_durumlari.get(fili_durum, [])
        uyum_durum = fili_durum in [k for k in uyanma_durumlari.keys()]  # Basit kontrol
        
        uyum_sonuçları.append({
            'strateji': stradi_adi,
            'fili_durum': fili_durum,
            'uyum_kriterleri': uyum_kriterleri,
            'uyum_durumu': 'UYUM' if fili_durum in uyanma_durumlari else 'BILGI YOK'
        })
    
    return {
        'uyum_analizi': uyum_sonuçları,
        'genel_uyum': all(s['uyum_durumu'] == 'UYUM' for s in uyum_sonuçları)
    }


def main():
    """Ana yürütme fonksiyonu"""
    print("=" * 60)
    print("VERI-OSB-HARITA-01: OSB Veri Kontrol Sistemi")
    print("=" * 60)
    
    # Dosyaları yükle
    onay = load_onay_kuyrugu('onay_kuyrugu.json')
    strateji = load_strateji_data('strateji_data.json')
    
    print("\n--- RED Ground Validation ---")
    validation = validate_red_grounds(onay, strateji)
    
    for ground, detail in validation['details'].items():
        print(f"RED-{ground.replace('red_', '')}: {detail['status']} - {detail['aciklama']}")
    
    print(f"\nGenel Durum: {validation['overall_status']}")
    
    print("\n--- Fiili Durum Uyumu Kontrolü ---")
    uyum = check_osfi_durum_uyumu(onay, strateji)
    
    for item in uyum['uyum_analizi']:
        str_ad = item.get('strateji', 'Bilinmiyor')
        fili_durum = item.get('fili_durum', 'Bilinmiyor')
        uyum_durumu = item.get('uyum_durumu', 'Bilinmiyor')
        print(f"{str_ad}: {fili_durum} -> {uyum_durumu}")
    
    print(f"\nGenel Uyum: {uyum['genel_uyum']}")
    
    # Başarı mesajı
    if validation['overall_status'] == 'APPROVED':
        print("\n🎉 TÜM RED GROUND'LER TAMAM! GÖREV ONAYLI!")
    else:
        print("\n⏳ HALİNDE: Tüm RED Ground'ler tam değil.")
    
    return validation


if __name__ == '__main__':
    main()