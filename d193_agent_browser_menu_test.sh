#!/bin/bash
# D-193: Agent-Browser Menu E2E Test
# Tüm menü öğelerini tıkla, screenshot al, hata yakalama

BASE_URL="http://localhost:8501"
OUTPUT_DIR="d193_screenshots"
TIMEOUT=30

mkdir -p "$OUTPUT_DIR"

echo "D-193: Agent-Browser Menu E2E Test"
echo "========================================"
echo "Base URL: $BASE_URL"
echo "Screenshot Dir: $OUTPUT_DIR"
echo ""

# Menu items: (name, url, icon)
MENU_ITEMS=(
  "ana_kontrol:/ana-kontrol:🏠"
  "musteriler:/musteriler:👥"
  "paketler:/paketler:📦"
  "pazarlama:/pazarlama:📢"
  "abrakadabra:/abrakadabra:🤖"
  "destek:/destek:🎫"
  "kpi:/kpi:📊"
  "karar_defteri:/karar-defteri:📔"
  "ajan_sohbet:/ajan-sohbet:💬"
  "rapor_listesi:/rapor-listesi:📋"
  "kalite:/kalite:✅"
  "export:/export:💾"
  "hatalar:/hatalar:⚠️"
  "teknik_altyapi:/teknik-altyapi:🧭"
  "maliyet:/maliyet:💰"
  "api:/api:🔌"
)

PASSED=0
FAILED=0
ERRORS=""

for item in "${MENU_ITEMS[@]}"; do
  IFS=':' read -r name url icon <<< "$item"
  full_url="${BASE_URL}${url}"
  screenshot_file="${OUTPUT_DIR}/d193_${name}.png"
  
  echo -n "[TEST] $icon $name ($url)... "
  
  # Navigate + screenshot
  if timeout $TIMEOUT agent-browser screenshot "$screenshot_file" --navigate "$full_url" 2>/dev/null; then
    echo "✓ PASS"
    ((PASSED++))
  else
    echo "✗ FAIL"
    ERRORS="${ERRORS}\n- $name: Screenshot failed or timeout"
    ((FAILED++))
  fi
done

echo ""
echo "========================================"
echo "Results: $PASSED PASSED, $FAILED FAILED"
echo "Screenshots: $OUTPUT_DIR"
if [ -n "$ERRORS" ]; then
  echo -e "\nErrors:$ERRORS"
fi
