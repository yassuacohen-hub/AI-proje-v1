#!/bin/bash
# Dashboard menü taraması — tüm sekmeler ve hata alanları

set -e

echo "=== Dashboard Menü Taraması ==="
echo ""

# Session başlat
export AGENT_BROWSER_SESSION="$(agent-browser session id --scope worktree --prefix scan)"

# Dashboard açılması için bekleme süresi
sleep 3

# 1. Ana sayfa snapshot
echo "1. Ana Kontrol sayfası…"
agent-browser open http://localhost:8501
agent-browser wait --load domcontentloaded
agent-browser wait 2000
agent-browser screenshot ana-kontrol.png
agent-browser snapshot -i > ana-kontrol-structure.txt

# 2. Sidebar menülerini tarama
echo "2. Sidebar menüleri…"

# Müşteri Yönetimi
echo "   → Müşteri Yönetimi sekmesi…"
agent-browser snapshot -i | grep -i "müşteri" || echo "  ! Müşteri Yönetimi bulunamadı"

# Proje Yönetimi
echo "   → Proje Yönetimi sekmesi…"
agent-browser snapshot -i | grep -i "proje" || echo "  ! Proje Yönetimi bulunamadı"

# Veri & Kalite
echo "   → Veri & Kalite sekmesi…"
agent-browser snapshot -i | grep -i "veri\|kalite" || echo "  ! Veri & Kalite bulunamadı"

# Sistem
echo "   → Sistem sekmesi…"
agent-browser snapshot -i | grep -i "sistem" || echo "  ! Sistem bulunamadı"

# Müşteri Önizleme
echo "   → Müşteri Önizleme sekmesi…"
agent-browser snapshot -i | grep -i "müşteri önizleme" || echo "  ! Müşteri Önizleme bulunamadı"

# 3. Sistem sekmesine gir (en kalabalık grup)
echo ""
echo "3. Sistem sekmesi (9 alt sekme — çok kalabalık)…"
agent-browser wait --text "Sistem" 2000 || true
agent-browser snapshot -i > sistem-menu.txt

# Console hatalarını al
echo ""
echo "4. Browser konsol hataları…"
agent-browser eval "console.error.toString()" > console-errors.txt 2>&1 || true

# Tam page kaydet
echo ""
echo "5. Tüm sayfanın ekran görüntüsü…"
agent-browser screenshot --full dashboard-full.png

agent-browser close

echo ""
echo "✓ Tarama tamamlandı."
echo "Dosyalar:"
ls -la *.png *.txt 2>/dev/null || echo "  (Dosya yok)"
