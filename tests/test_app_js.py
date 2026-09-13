from __future__ import annotations

import json
import subprocess
from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "web_dashboard" / "js" / "app.js"


def test_app_js_helper_functions():
    script = f"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8');
const storage = new Map();
const context = {{
  window: {{ location: {{ origin: 'https://example.test', search: '' }}, addEventListener: () => {{ }} }},
  document: {{
    cookie: '',
    addEventListener: () => {{ }},
    createElement: () => ({{
      textContent: '',
      get innerHTML() {{
        return this.textContent.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\"/g, '&quot;');
      }}
    }})
  }},
  localStorage: {{
    getItem: key => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, String(value))
  }},
  console: {{ log: () => {{}}, warn: () => {{}}, error: () => {{}} }},
  setInterval: () => {{}},
  setTimeout: () => {{}},
  URLSearchParams,
  Date,
  Set,
  JSON,
  Math
}};
vm.createContext(context);
vm.runInContext(source, context);
if (context.apiUrl('/api/kpi') !== 'https://example.test/api/kpi') throw new Error('apiUrl path failed');
if (context.apiUrl('/api/kpi?x=1') !== 'https://example.test/api/kpi?x=1') throw new Error('apiUrl query failed');
if (context.esc('<b>firma</b>') !== '&lt;b&gt;firma&lt;/b&gt;') throw new Error('esc failed');
if (context.fmt(1234567) !== '1,234,567') throw new Error('fmt failed');
if (context.watchKeyOf({{ company_id: '42', legal_name: 'Firma' }}) !== '42') throw new Error('company id key failed');
if (context.watchKeyOf({{ legal_name: 'Firma' }}) !== 'Firma') throw new Error('legal name key failed');
console.log('ok');
"""

    result = subprocess.run(
        ["node", "-e", script],
        cwd=APP_JS.parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
