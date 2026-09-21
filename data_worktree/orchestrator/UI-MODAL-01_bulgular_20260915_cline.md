[[Huginn Data Insights/data/orchestrator/UI-MODAL-01_bulgular_20260915_cline.md]]

# UI-MODAL-01 bulgular (kapsam disi, duzeltme YOK) — 2026-09-15, cline

Arastirma dokumani: `docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15.md`.
Talimat geregi `charts.py` ve `web_dashboard/**` dosyalarina dokunulmadı.

## B-1 (Dusuk): `X` sonekli Python dosyasi gorunumu

`ls` ciktisinda su dosyalar `X` sonekli gorundu:

- `src/company_master/ui/styles.pyX`
- `web_dashboard/tabs/admin_audit.pyX`
- `web_dashboard/tabs/pazarlama.pyX`
- `web_dashboard/tabs/admin_extras.pyX`

Eger gercek uzanti `.pyX` ise bu dosyalar Python import/discovery disi kalir.
Dizin listeleme kirpilmasi da olabilir; teyit edilmeden dokunulmadı.
Oneri: `dir /x` veya bayt duzeyinde uzanti teyidi + gerekiyorsa `.py` rename
(ayri gorev, bu gorev kapsam disi).

## B-2 (Bilgi): `__pycache__` art variants

- `src/company_master/ui/__pycache__`
- `web_dashboard/tabs/__pycache__`

Calisma ortami artigi; `.gitignore` kapsiyorsa sorun yok.

## Dogrulama

- `pip show`: streamlit 1.62.0, plotly 7.0.0, altair 6.2.2 kurulu;
  `streamlit-echarts` kurulu degil.
- Dokuman: UTF-8, BOM yok, NUL yok (asagidaki komutla teyit).
