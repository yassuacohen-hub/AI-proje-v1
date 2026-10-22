#!/usr/bin/env python3
"""
OSB Harita Visualization - Enhanced
Filtreleme, ölçek, senkronizasyon özellikleri
"""

import folium
import json
from datetime import datetime
import os

# --- VERI YÜKLEME ---
try:
    with open("c:\\\\Huginn Data Projesi\\\\monitoring_export.json", 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    results = data.get("results", [])
except:
    # Örnek veri
    results = [
        {"osb": "AGİOSB", "city": "Adana", "lat": 36.9875, "lon": 35.3211, "filo": "FAALİYETTE", "firma_sayisi": 30, "web": "www.agiosb.org"},
        {"osb": "Hacı Sabancı", "city": "Adana", "lat": 36.8252, "lon": 35.3125, "filo": "FAALİYETTE", "firma_sayisi": 525, "web": "www.adanaorganize.org.tr"},
        {"osb": "Karataş TDİ", "city": "Adana", "lat": 36.9142, "lon": 35.2987, "filo": "FAALİYETTE", "firma_sayisi": 25, "web": "www.adana.gov.tr/yikob"},
        {"osb": "Kaya OSB", "city": "Ankara", "lat": 39.9334, "lon": 32.8597, "filo": "KAMULAŞTIRMA YAPILIYOR", "firma_sayisi": 0, "web": "www.kayaosb.org"},
        {"osb": "Ege OSB", "city": "İzmir", "lat": 38.4237, "lon": 27.1428, "filo": "İŞLETMEDE (FAALİYETTE)", "firma_sayisi": 0, "web": "www.egeosb.org"}
    ]

# --- FILTRE VE RENK FONKSİYONELERİ ---
def get_filtered_results(results, filo_filter="Tümü"):
    if filo_filter == "Tümü":
        return results
    return [r for r in results if str(r.get("filo", "")).upper() == str(filo_filter).upper()]

def get_pin_color_and_icon(filo):
    filo_upper = str(filo).upper()
    if "KAMULAŞTIRMA" in filo_upper:
        return "red", "🏗️"
    elif "ALTYAPI" in filo_upper:
        return "orange", "🚧"
    elif "FAALİYETTE" in filo_upper or "İŞLETMEDE" in filo_upper:
        return "green", "🏭"
    else:
        return "gray", "📍"

# --- HARITA OLUŞTURMA FONKSİYONU ---
def create_enhanced_map(results, filo_filter="Tümü"):
    filtered = get_filtered_results(results, filo_filter)
    
    if not filtered:
        print("⚠️ Filtre sonucu OS bulunamadı")
        return None
    
    # Ortalama koordinatları hesapla
    center_lat = sum(r["lat"] for r in filtered) / len(filtered)
    center_lon = sum(r["lon"] for r in filtered) / len(filtered)
    center = [center_lat, center_lon]
    
    # Harita oluştur
    m = folium.Map(
        location=center,
        zoom_start=7,
        tiles="OpenStreetMap"
    )
    
    # Basemap değiştirici
    folium.TileLayer(
        tiles="OpenStreetMap",
        attr='Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        name="OpenStreetMap",
        control_type='dropdown'
    ).add_to(m)
    
    # Stamen Terrain option
    folium.TileLayer(
        tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
        attr='Map tiles &copy; <a href="https://stamen.com">Stamen</a>',
        name="Stamen Terrain",
        control_type='dropdown'
    ).add_to(m)
    
    # Her OS için pin ekle
    for r in filtered:
        color, icon = get_pin_color_and_icon(r["filo"])
        
        popup_content = f"""
        <b>OS:</b> {r["osb"]}<br>
        <b>Fili Durumu:</b> {r["filo"]}<br>
        <b>Firma Sayısı:</b> {r["firma_sayisi"]} firma<br>
        <b>Şehir:</b> {r["city"]}<br>
        <b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        folium.Marker(
            location=[r["lat"], r["lon"]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            tooltip=f"{r['osb']} - {r['filo']}"
        ).add_to(m)
    
    # Layer control - basemap ve marker toggles
    folium.LayerControl().add_to(m)
    
    return m

# --- ANA ÇALIŞMA ---
if __name__ == "__main__":
    print("="*60)
    print("OSB Harita Visualization - Enhanced")
    print("="*60)
    print()
    
    # Harita oluştur (tüm OS'ler, filtreleme yok)
    print(">>> Tüm OS'ler için harita oluşturuluyor...")
    m = create_enhanced_map(results, filo_filter="Tümü")
    
    if m:
        output_path = "c:\\\\Huginn Data Projesi\\\\osb_map_enhanced.html"
        m.save(output_path)
        print(f"✅ Harita oluşturuldu: {output_path}")
        print(f"📊 Toplam Pin Sayısı: {len([r for r in results])}")
        print(f"🌐 Açmak için: file://{output_path}")
    else:
        print("❌ Harita oluşturulamadı")
    
    print()
    print(">>> Filtreli harita örnekleri:")
    print()
    
    # Filtreli harita örnekleri
    filo_options = ["Tümü", "FAALİYETTE", "KAMULAŞTIRMA YAPILIYOR", "ALTYAPI HAZIRLANIYOR"]
    
    for filo in filo_options:
        print(f"  Filtre: {filo}")
        m_filtered = create_enhanced_map(results, filo_filter=filo)
        if m_filtered:
            filter_name = filo.replace(" ", "_").replace("(", "").replace(")", "").replace("İ", "I")
            output_name = f"osb_map_{filter_name}.html"
            m_filtered.save(output_name)
            pin_count = len(get_filtered_results(results, filo))
            print(f"    → {output_name} ({pin_count} pin)")
        print()
    
    print("="*60)
    print("🗺️ Harita İşlemleri Tamamlandı")
    print("="*60)