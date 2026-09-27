# GÖREV BRIËFI: ORCH-02 — Bağımlılık Yönetimi - Görüntü Grafiği

**Atanan:** orkestrator  
**Öncelik:** P1  
**Deadline:** 2026-10-02T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Görev bağımlılıklarını görselleştir. DAG grafiği oluştur, görevleri node olarak göster, ilişkileri edge olarak işaretle. Interaktif visualizer kur.

## Kabul Kriterleri
1. Dependency graph modülü yazılmalı (orchestration/dependency_graph.py)
2. Grafiksel output (SVG/PNG) üretilebilmeli
3. Web dashboard entegrasyonu

## Kaynaklar (SSOT)
- orchestration/dependency_graph.py
- Graphviz/Plotly documentation

## İmplantasyon Notları
- Networkx + Graphviz
- D3.js for interactive viz
- Cycle detection

## Proof-of-Work
File/Output: orchestration/dependency_graph.py + visualizations + integration tests
