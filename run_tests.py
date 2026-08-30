"""Test Runner - Unittest Raporlama Sistemi.

Test sonuçlarını JSON, HTML ve TXT formatlarında kaydeder.
Her çalışma için tarih-saat klasörü oluşturur.
"""

import os
import sys
import json
import unittest
from datetime import datetime
from pathlib import Path
from io import StringIO


def run_tests_with_reporting():
    """Test suite'i çalıştır ve raporları kaydet."""
    
    # Rapor dizini oluştur
    reports_dir = Path("test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Timestamp klasörü
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = reports_dir / timestamp
    run_dir.mkdir(exist_ok=True)
    
    # Test suite'i yükle
    sys.path.insert(0, str(Path.cwd() / "src"))
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    
    # StringIO ile çıktıyı yakala
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Test sonuçlarını hazırla
    test_output = stream.getvalue()
    
    report_data = {
        "timestamp": timestamp,
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures),
        "error_count": len(result.errors),
        "success": result.wasSuccessful(),
        "failures": [
            {
                "test": str(test),
                "message": msg
            }
            for test, msg in result.failures
        ],
        "errors": [
            {
                "test": str(test),
                "message": msg
            }
            for test, msg in result.errors
        ],
    }
    
    # 1. JSON raporu kaydet
    json_file = run_dir / "test_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # 2. TXT raporu kaydet
    txt_file = run_dir / "test_results.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(test_output)
    
    # 3. HTML raporu oluştur
    html_file = run_dir / "test_results.html"
    html_content = generate_html_report(report_data, test_output)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 4. Özet raporu (summary.json) - geçmiş takibi
    summary_file = reports_dir / "summary.json"
    summaries = []
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            summaries = json.load(f)
    
    summaries.append({
        "timestamp": timestamp,
        "total": report_data["total_tests"],
        "passed": report_data["passed"],
        "failed": report_data["failed"],
        "errors": report_data["error_count"],
        "success": report_data["success"]
    })
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    
    # Console'da göster
    print("\n" + "="*60)
    print(f"📊 Test Raporu: {timestamp}")
    print("="*60)
    print(f"Toplam Test: {report_data['total_tests']}")
    print(f"✅ Geçen: {report_data['passed']}")
    print(f"❌ Başarısız: {report_data['failed']}")
    print(f"⚠️  Hata: {report_data['error_count']}")
    print(f"Sonuç: {'✓ BAŞARILI' if report_data['success'] else '✗ BAŞARISIZ'}")
    print("="*60)
    print(f"\n📁 Raporlar kaydedildi: {run_dir}")
    print(f"   - {json_file.name}")
    print(f"   - {txt_file.name}")
    print(f"   - {html_file.name}")
    print(f"\n📈 Geçmiş özet: {summary_file}")
    print("\n")
    
    return result.wasSuccessful()


def generate_html_report(report_data, test_output):
    """HTML formatında test raporu oluştur."""
    
    status_class = "success" if report_data["success"] else "failure"
    status_text = "✓ BAŞARILI" if report_data["success"] else "✗ BAŞARISIZ"
    
    failures_html = ""
    for failure in report_data["failures"]:
        failures_html += f"""
        <div class="failure-item">
            <h4>❌ {failure['test']}</h4>
            <pre>{failure['message']}</pre>
        </div>
        """
    
    errors_html = ""
    for error in report_data["errors"]:
        errors_html += f"""
        <div class="error-item">
            <h4>⚠️ {error['test']}</h4>
            <pre>{error['message']}</pre>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Raporu - {report_data['timestamp']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .status {{
            background: white;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            border-left: 5px solid;
        }}
        .status.success {{
            border-left-color: #10b981;
            background-color: #f0fdf4;
        }}
        .status.failure {{
            border-left-color: #ef4444;
            background-color: #fef2f2;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            padding: 20px;
            background: #f9fafb;
        }}
        .stat-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e5e7eb;
        }}
        .stat-box h3 {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-box p {{
            font-size: 12px;
            color: #6b7280;
        }}
        .failures, .errors {{
            padding: 20px;
            margin: 0 20px;
        }}
        .failures h2, .errors h2 {{
            margin-bottom: 15px;
            font-size: 18px;
            color: #1f2937;
        }}
        .failure-item, .error-item {{
            background: #fef2f2;
            border: 1px solid #fee2e2;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .failure-item h4, .error-item h4 {{
            color: #dc2626;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .failure-item pre, .error-item pre {{
            background: #f3f4f6;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            color: #1f2937;
            font-family: 'Courier New', monospace;
        }}
        .footer {{
            background: #f9fafb;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Raporu</h1>
            <p>{report_data['timestamp']}</p>
        </div>
        
        <div class="status {status_class}">
            <h2>{status_text}</h2>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>{report_data['total_tests']}</h3>
                <p>Toplam Test</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #10b981;">{report_data['passed']}</h3>
                <p>✅ Geçen</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #ef4444;">{report_data['failed']}</h3>
                <p>❌ Başarısız</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #f59e0b;">{report_data['error_count']}</h3>
                <p>⚠️ Hata</p>
            </div>
        </div>
        
        {f'<div class="failures"><h2>❌ Başarısız Testler</h2>{failures_html}</div>' if report_data['failed'] > 0 else ''}
        {f'<div class="errors"><h2>⚠️ Hatalar</h2>{errors_html}</div>' if report_data['error_count'] > 0 else ''}
        
        <div class="footer">
            <p>Rapor türleri: JSON • HTML • TXT | 📁 test_reports/ klasöründe kaydedildi</p>
        </div>
    </div>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    success = run_tests_with_reporting()
    sys.exit(0 if success else 1)
