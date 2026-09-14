# -*- coding: utf-8 -*-
"""UX-01: Bileşen kütüphanesinin CSS katmanı.

Tüm renk/boşluk/yarıçap değerleri `tokens.py`'deki CSS değişkenlerine
(`var(--hg-...)`) referans verir. Hiçbir yerde sabit hex kullanılmaz —
böylece UX-03'te tema değişimi yalnızca `:root` bloğu değiştirilerek yapılır.

Kullanım (Streamlit):
    from company_master.ui import stil_enjekte
    stil_enjekte()   # sayfa başında bir kez
"""
from __future__ import annotations

from company_master.ui.tokens import kok_css

_BUTON_CSS = """
.hg-btn{display:inline-flex;align-items:center;justify-content:center;
gap:var(--hg-space-2);border:1px solid transparent;cursor:pointer;
font-family:var(--hg-font-font-family);font-weight:var(--hg-font-weight-medium);
line-height:var(--hg-font-line-tight);border-radius:var(--hg-radius-button);
transition:background var(--hg-transition-fast),border-color var(--hg-transition-fast),
color var(--hg-transition-fast);text-decoration:none;white-space:nowrap}
.hg-btn:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus)}
.hg-btn-sm{padding:var(--hg-space-1) var(--hg-space-3);font-size:var(--hg-font-size-xs)}
.hg-btn-md{padding:var(--hg-space-2) var(--hg-space-4);font-size:var(--hg-font-size-sm)}
.hg-btn-lg{padding:var(--hg-space-3) var(--hg-space-5);font-size:var(--hg-font-size-md)}
.hg-btn-block{width:100%}
/* ADMIN-UI-11: Dolgu butonlarda metin rengi artik `on-*` token'larindan gelir.
   `text-inverse` kullanmak aydinlik temada beyaz-ustu-sari (2.15:1) gibi
   okunmaz kombinasyonlar uretiyordu. `on-*` tema bagimsizdir, cunku dolgu
   rengi de tema bagimsizdir. */
.hg-btn-primary{background:var(--hg-color-primary-solid);color:var(--hg-color-on-primary)}
.hg-btn-primary:hover{background:var(--hg-color-primary-solid-hover)}
.hg-btn-primary:active{background:var(--hg-color-primary-solid-active)}
.hg-btn-secondary{background:var(--hg-color-surface-2);color:var(--hg-color-text);
border-color:var(--hg-color-border-interactive)}
.hg-btn-secondary:hover{border-color:var(--hg-color-border-strong);
background:var(--hg-color-surface-3)}
.hg-btn-success{background:var(--hg-color-success);color:var(--hg-color-on-success)}
.hg-btn-warning{background:var(--hg-color-warning);color:var(--hg-color-on-warning)}
.hg-btn-danger{background:var(--hg-color-danger);color:var(--hg-color-on-danger)}
.hg-btn-danger:hover{filter:brightness(1.08)}
.hg-btn-info{background:var(--hg-color-info);color:var(--hg-color-on-info)}
.hg-btn-ghost{background:transparent;color:var(--hg-color-text-muted)}
.hg-btn-ghost:hover{background:var(--hg-color-surface-2);color:var(--hg-color-text)}
.hg-btn-disabled,.hg-btn[disabled]{opacity:.5;cursor:not-allowed;pointer-events:none}
.hg-btn-label{display:inline-flex;line-height:1}
.hg-btn-loading{cursor:progress}
.hg-spinner{width:12px;height:12px;border-radius:var(--hg-radius-full);
border:2px solid currentColor;border-top-color:transparent;
animation:hg-spin .7s linear infinite}
@keyframes hg-spin{to{transform:rotate(360deg)}}
.hg-actions{display:flex;align-items:center;gap:var(--hg-space-2);flex-wrap:wrap}
.hg-actions-sol{justify-content:flex-start}
.hg-actions-sag{justify-content:flex-end}
.hg-actions-arali{justify-content:space-between;width:100%}
@media (max-width:640px){
.hg-actions{width:100%}
.hg-actions .hg-btn{flex:1 1 auto}
}
"""

_INPUT_CSS = """
.hg-input-group{display:flex;flex-direction:column;gap:var(--hg-space-1);
font-family:var(--hg-font-font-family)}
.hg-input-label{font-size:var(--hg-font-size-sm);color:var(--hg-color-text);
font-weight:var(--hg-font-weight-medium)}
.hg-input-required{color:var(--hg-color-danger-text);margin-left:2px}
/* ADMIN-UI-11: Form kontrollerinin sinirı `border` degil `border-interactive`.
   WCAG 1.4.11 geregi etkilesimli bilesen siniri yuzeye karsi >= 3:1 olmali;
   `border` bilincli olarak dusuk kontrastli dekoratif ayractir. */
.hg-input-field{background:var(--hg-color-surface);color:var(--hg-color-text);
border:1px solid var(--hg-color-border-interactive);border-radius:var(--hg-radius-button);
font-family:inherit;width:100%;
transition:border-color var(--hg-transition-fast),box-shadow var(--hg-transition-fast)}
.hg-input-field::placeholder{color:var(--hg-color-text-muted)}
.hg-input-field:focus{outline:none;border-color:var(--hg-color-primary);
box-shadow:var(--hg-shadow-focus)}
.hg-input-sm{padding:var(--hg-space-1) var(--hg-space-2);font-size:var(--hg-font-size-xs)}
.hg-input-md{padding:var(--hg-space-2) var(--hg-space-3);font-size:var(--hg-font-size-sm)}
.hg-input-lg{padding:var(--hg-space-3) var(--hg-space-4);font-size:var(--hg-font-size-md)}
.hg-input-error{border-color:var(--hg-color-danger)}
.hg-input-error:focus{box-shadow:0 0 0 3px var(--hg-color-danger-soft)}
.hg-input-field[disabled]{opacity:.5;cursor:not-allowed}
.hg-input-message{font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted)}
.hg-input-message-error{font-size:var(--hg-font-size-xs);color:var(--hg-color-danger-text)}
textarea.hg-input-field{min-height:96px;resize:vertical}
"""

_SELECT_CSS = """
.hg-select-group{display:flex;flex-direction:column;gap:var(--hg-space-1);
font-family:var(--hg-font-font-family)}
.hg-select-label{font-size:var(--hg-font-size-sm);color:var(--hg-color-text);
font-weight:var(--hg-font-weight-medium)}
.hg-select-field{background:var(--hg-color-surface);color:var(--hg-color-text);
border:1px solid var(--hg-color-border-interactive);border-radius:var(--hg-radius-button);
font-family:inherit;width:100%;z-index:var(--hg-z-dropdown)}
.hg-select-field:focus{outline:none;border-color:var(--hg-color-primary);
box-shadow:var(--hg-shadow-focus)}
.hg-select-sm{padding:var(--hg-space-1) var(--hg-space-2);font-size:var(--hg-font-size-xs)}
.hg-select-md{padding:var(--hg-space-2) var(--hg-space-3);font-size:var(--hg-font-size-sm)}
.hg-select-lg{padding:var(--hg-space-3) var(--hg-space-4);font-size:var(--hg-font-size-md)}
.hg-select-field[disabled]{opacity:.5;cursor:not-allowed}
.hg-select-message{font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted)}
"""

_BADGE_CSS = """
.hg-badge{display:inline-flex;align-items:center;gap:var(--hg-space-1);
border-radius:var(--hg-radius-full);font-family:var(--hg-font-font-family);
font-weight:var(--hg-font-weight-medium);line-height:var(--hg-font-line-tight);
white-space:nowrap}
.hg-badge-sm{padding:2px var(--hg-space-2);font-size:var(--hg-font-size-xs)}
.hg-badge-md{padding:var(--hg-space-1) var(--hg-space-3);font-size:var(--hg-font-size-sm)}
.hg-badge-lg{padding:var(--hg-space-2) var(--hg-space-4);font-size:var(--hg-font-size-md)}
.hg-badge-dot{width:6px;height:6px;border-radius:var(--hg-radius-full);
background:currentColor;flex:0 0 auto}
/* ADMIN-UI-11: Yumusak zemin uzerindeki rozet metni `*-text` turevini kullanir
   (dolgu tonu metin olarak her iki temada da AA'yi dusuruyordu). */
.hg-badge-primary{background:var(--hg-color-primary-soft);color:var(--hg-color-primary-text)}
.hg-badge-secondary{background:var(--hg-color-surface-2);color:var(--hg-color-text-muted)}
.hg-badge-success{background:var(--hg-color-success-soft);color:var(--hg-color-success-text)}
.hg-badge-warning{background:var(--hg-color-warning-soft);color:var(--hg-color-warning-text)}
.hg-badge-danger{background:var(--hg-color-danger-soft);color:var(--hg-color-danger-text)}
.hg-badge-info{background:var(--hg-color-info-soft);color:var(--hg-color-info-text)}
.hg-badge-ghost{background:transparent;color:var(--hg-color-text-muted);
border:1px solid var(--hg-color-border-interactive)}
.hg-badge-solid.hg-badge-primary{background:var(--hg-color-primary-solid);color:var(--hg-color-on-primary)}
.hg-badge-solid.hg-badge-success{background:var(--hg-color-success);color:var(--hg-color-on-success)}
.hg-badge-solid.hg-badge-warning{background:var(--hg-color-warning);color:var(--hg-color-on-warning)}
.hg-badge-solid.hg-badge-danger{background:var(--hg-color-danger);color:var(--hg-color-on-danger)}
.hg-badge-solid.hg-badge-info{background:var(--hg-color-info);color:var(--hg-color-on-info)}
.hg-badge-solid.hg-badge-secondary{background:var(--hg-color-border-strong);color:var(--hg-color-text)}
"""

_CARD_CSS = """
.hg-card{background:var(--hg-color-surface);border:1px solid var(--hg-color-border);
border-radius:var(--hg-radius-card);font-family:var(--hg-font-font-family);
color:var(--hg-color-text);overflow:hidden;
transition:border-color var(--hg-transition-fast),box-shadow var(--hg-transition-fast)}
.hg-card:hover{border-color:var(--hg-color-border-strong)}
.hg-card-accent{border-left:3px solid var(--hg-color-primary);box-shadow:var(--hg-shadow-sm)}
.hg-card-header{display:flex;align-items:center;gap:var(--hg-space-2);
padding:var(--hg-space-4);border-bottom:1px solid var(--hg-color-border);
font-weight:var(--hg-font-weight-bold);font-size:var(--hg-font-size-md)}
.hg-card-icon{flex:0 0 auto}
.hg-card-body{padding:var(--hg-space-4);font-size:var(--hg-font-size-sm);
line-height:var(--hg-font-line-normal)}
.hg-card-footer{padding:var(--hg-space-3) var(--hg-space-4);
border-top:1px solid var(--hg-color-border);color:var(--hg-color-text-muted);
font-size:var(--hg-font-size-xs)}
.hg-metric{background:var(--hg-color-surface);border:1px solid var(--hg-color-border);
border-left:3px solid var(--hg-color-border-strong);border-radius:var(--hg-radius-card);
padding:var(--hg-space-4);font-family:var(--hg-font-font-family);
display:flex;flex-direction:column;gap:var(--hg-space-1)}
.hg-metric-customer{border-left-color:var(--hg-color-metric-customer)}
.hg-metric-system{border-left-color:var(--hg-color-metric-system)}
.hg-metric-neutral{border-left-color:var(--hg-color-border-strong)}
.hg-metric-label{font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted);
text-transform:uppercase;letter-spacing:.04em}
.hg-metric-value{font-size:var(--hg-font-size-2xl);font-weight:var(--hg-font-weight-bold);
line-height:var(--hg-font-line-tight);color:var(--hg-color-text)}
/* ADMIN-UI-11: Metrik degeri buyuk punto olsa da `*-text` turevi kullanilir;
   sol kenar cizgisi (dekoratif) dolgu tonunda kalir. */
.hg-metric-customer .hg-metric-value{color:var(--hg-color-metric-customer-text)}
.hg-metric-system .hg-metric-value{color:var(--hg-color-metric-system-text)}
.hg-metric-delta{font-size:var(--hg-font-size-xs);font-weight:var(--hg-font-weight-medium)}
.hg-metric-delta-yukari{color:var(--hg-color-success-text)}
.hg-metric-delta-asagi{color:var(--hg-color-danger-text)}
.hg-metric-delta-notr{color:var(--hg-color-text-muted)}
.hg-metric-hint{font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted)}
.hg-metric-question{font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted);
font-style:italic}
"""

_TABLE_CSS = """
.hg-table-wrapper{overflow-x:auto;border:1px solid var(--hg-color-border);
border-radius:var(--hg-radius-card);font-family:var(--hg-font-font-family)}
.hg-table{width:100%;border-collapse:collapse;font-size:var(--hg-font-size-sm);
color:var(--hg-color-text)}
.hg-table-th{background:var(--hg-color-surface-2);color:var(--hg-color-text-muted);
font-size:var(--hg-font-size-xs);text-transform:uppercase;letter-spacing:.04em;
padding:var(--hg-space-3) var(--hg-space-4);
border-bottom:1px solid var(--hg-color-border);position:sticky;top:0;
z-index:var(--hg-z-base)}
.hg-table-td{padding:var(--hg-space-3) var(--hg-space-4);
border-bottom:1px solid var(--hg-color-border);
font-variant-numeric:tabular-nums}
.hg-table tbody tr:last-child td{border-bottom:none}
.hg-table-zebra tbody tr:nth-child(even){background:var(--hg-color-surface-2)}
.hg-table tbody tr:hover{background:var(--hg-color-primary-soft)}
.hg-table-dense .hg-table-th,
.hg-table-dense .hg-table-td{padding:var(--hg-space-1) var(--hg-space-2)}
.hg-table-empty{padding:var(--hg-space-6);text-align:center;
color:var(--hg-color-text-muted);font-size:var(--hg-font-size-sm);
background:var(--hg-color-surface);border:1px dashed var(--hg-color-border);
border-radius:var(--hg-radius-card);font-family:var(--hg-font-font-family)}
.hg-table-more{padding:var(--hg-space-2) var(--hg-space-4);
font-size:var(--hg-font-size-xs);color:var(--hg-color-text-muted);
background:var(--hg-color-surface-2);border-top:1px solid var(--hg-color-border)}
"""

_MODAL_CSS = """
.hg-modal-backdrop{position:fixed;inset:0;display:flex;align-items:center;
justify-content:center;padding:var(--hg-space-5);
background:rgba(10,14,23,.72);z-index:var(--hg-z-modal-backdrop)}
.hg-modal-backdrop[hidden]{display:none}
.hg-modal{background:var(--hg-color-surface);color:var(--hg-color-text);
border:1px solid var(--hg-color-border);border-radius:var(--hg-radius-modal);
box-shadow:var(--hg-shadow-lg);font-family:var(--hg-font-font-family);
width:100%;max-height:85vh;display:flex;flex-direction:column;
z-index:var(--hg-z-modal)}
.hg-modal-sm{max-width:380px}
.hg-modal-md{max-width:560px}
.hg-modal-lg{max-width:820px}
.hg-modal-full{max-width:96vw}
.hg-modal-kapali{display:none}
.hg-modal-header{display:flex;align-items:flex-start;justify-content:space-between;
gap:var(--hg-space-3);padding:var(--hg-space-4);
border-bottom:1px solid var(--hg-color-border)}
.hg-modal-title{margin:0;font-size:var(--hg-font-size-lg);
font-weight:var(--hg-font-weight-bold);line-height:var(--hg-font-line-tight)}
.hg-modal-subtitle{margin:var(--hg-space-1) 0 0;font-size:var(--hg-font-size-xs);
color:var(--hg-color-text-muted)}
.hg-modal-close{background:transparent;border:none;color:var(--hg-color-text-muted);
font-size:var(--hg-font-size-lg);line-height:1;cursor:pointer;
padding:var(--hg-space-1);border-radius:var(--hg-radius-sm)}
.hg-modal-close:hover{color:var(--hg-color-text);background:var(--hg-color-surface-2)}
.hg-modal-close:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus)}
.hg-modal-body{padding:var(--hg-space-4);overflow-y:auto;
font-size:var(--hg-font-size-sm);line-height:var(--hg-font-line-normal)}
.hg-modal-footer{display:flex;justify-content:flex-end;gap:var(--hg-space-2);
padding:var(--hg-space-3) var(--hg-space-4);
border-top:1px solid var(--hg-color-border);background:var(--hg-color-surface-2)}
"""

_TOOLTIP_CSS = """
.hg-tooltip{position:relative;display:inline-flex;
font-family:var(--hg-font-font-family)}
.hg-tooltip:focus{outline:none}
.hg-tooltip:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus);
border-radius:var(--hg-radius-sm)}
.hg-tooltip-trigger{cursor:help;border-bottom:1px dotted var(--hg-color-border-strong)}
.hg-tooltip-bubble{position:absolute;opacity:0;visibility:hidden;
background:var(--hg-color-surface-2);color:var(--hg-color-text);
border:1px solid var(--hg-color-border-strong);border-radius:var(--hg-radius-md);
box-shadow:var(--hg-shadow-md);padding:var(--hg-space-2) var(--hg-space-3);
font-size:var(--hg-font-size-xs);line-height:var(--hg-font-line-normal);
max-width:220px;width:max-content;z-index:var(--hg-z-tooltip);
transition:opacity var(--hg-transition-fast),visibility var(--hg-transition-fast);
pointer-events:none}
.hg-tooltip-wide .hg-tooltip-bubble{max-width:360px}
.hg-tooltip:hover .hg-tooltip-bubble,
.hg-tooltip:focus .hg-tooltip-bubble,
.hg-tooltip:focus-within .hg-tooltip-bubble{opacity:1;visibility:visible}
.hg-tooltip-top .hg-tooltip-bubble{bottom:calc(100% + var(--hg-space-2));
left:50%;transform:translateX(-50%)}
.hg-tooltip-bottom .hg-tooltip-bubble{top:calc(100% + var(--hg-space-2));
left:50%;transform:translateX(-50%)}
.hg-tooltip-left .hg-tooltip-bubble{right:calc(100% + var(--hg-space-2));
top:50%;transform:translateY(-50%)}
.hg-tooltip-right .hg-tooltip-bubble{left:calc(100% + var(--hg-space-2));
top:50%;transform:translateY(-50%)}
"""

# ADMIN-UI-01: Sayfa iskeleti (PageHeader / Section / SectionNav).
# Amaç: her ekranda aynı punto ve boşluk hiyerarşisi. Tüm değerler semantik
# tipografi token'larına bağlıdır; ekran bazlı "elle punto" yasaktır.
_PAGE_CSS = """
.hg-page-head{display:flex;align-items:flex-start;justify-content:space-between;
gap:var(--hg-space-4);margin:0 0 var(--hg-space-5);
padding-bottom:var(--hg-space-4);
border-bottom:1px solid var(--hg-color-border);
font-family:var(--hg-font-font-family)}
.hg-page-head-main{min-width:0;flex:1 1 auto}
.hg-page-eyebrow{margin:0 0 var(--hg-space-1);
font-size:var(--hg-font-size-label);font-weight:var(--hg-font-weight-medium);
letter-spacing:var(--hg-font-tracking-wide);text-transform:uppercase;
color:var(--hg-color-text-muted)}
.hg-page-title{margin:0;font-size:var(--hg-font-size-h1);
font-weight:var(--hg-font-weight-bold);line-height:var(--hg-font-line-tight);
letter-spacing:var(--hg-font-tracking-tight);color:var(--hg-color-text);
display:flex;align-items:center;gap:var(--hg-space-3)}
.hg-page-icon{flex:0 0 auto;font-size:var(--hg-font-size-h2);line-height:1}
.hg-page-lead{margin:var(--hg-space-2) 0 0;max-width:68ch;
font-size:var(--hg-font-size-lead);font-weight:var(--hg-font-weight-normal);
line-height:var(--hg-font-line-relaxed);color:var(--hg-color-text-muted)}
.hg-page-actions{display:flex;align-items:center;gap:var(--hg-space-2);
flex:0 0 auto;flex-wrap:wrap;justify-content:flex-end}

.hg-section{margin:var(--hg-space-6) 0 var(--hg-space-4);
font-family:var(--hg-font-font-family)}
.hg-section-ruled{padding-top:var(--hg-space-5);
border-top:1px solid var(--hg-color-border)}
.hg-section-title{margin:0;color:var(--hg-color-text);
line-height:var(--hg-font-line-tight);
display:flex;align-items:center;gap:var(--hg-space-2);
scroll-margin-top:var(--hg-space-6)}
.hg-section-h2{font-size:var(--hg-font-size-h2);
font-weight:var(--hg-font-weight-semibold);
letter-spacing:var(--hg-font-tracking-tight)}
.hg-section-h3{font-size:var(--hg-font-size-h3);
font-weight:var(--hg-font-weight-semibold);
color:var(--hg-color-text-muted)}
.hg-section-icon{flex:0 0 auto;line-height:1}
.hg-section-desc{margin:var(--hg-space-2) 0 0;max-width:72ch;
font-size:var(--hg-font-size-body);line-height:var(--hg-font-line-relaxed);
color:var(--hg-color-text-muted)}

.hg-nav{background:var(--hg-color-surface);
border:1px solid var(--hg-color-border);border-radius:var(--hg-radius-card);
padding:var(--hg-space-3) var(--hg-space-4);margin:0 0 var(--hg-space-5);
font-family:var(--hg-font-font-family)}
.hg-nav-title{margin:0 0 var(--hg-space-2);
font-size:var(--hg-font-size-label);font-weight:var(--hg-font-weight-semibold);
letter-spacing:var(--hg-font-tracking-wide);text-transform:uppercase;
color:var(--hg-color-text-muted)}
.hg-nav-vertical{display:flex;flex-direction:column;gap:var(--hg-space-1)}
.hg-nav-horizontal{display:flex;flex-wrap:wrap;align-items:center;
gap:var(--hg-space-2)}
.hg-nav-horizontal .hg-nav-title{width:100%;margin-bottom:var(--hg-space-1)}
.hg-nav-link{display:inline-block;text-decoration:none;
font-size:var(--hg-font-size-body);line-height:var(--hg-font-line-normal);
color:var(--hg-color-text-muted);border-radius:var(--hg-radius-sm);
padding:var(--hg-space-1) var(--hg-space-2);
border-left:2px solid transparent;
transition:color var(--hg-transition-fast),
background var(--hg-transition-fast),
border-color var(--hg-transition-fast)}
.hg-nav-link:hover{color:var(--hg-color-text);
background:var(--hg-color-primary-soft);
border-left-color:var(--hg-color-primary)}
.hg-nav-link:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus);
color:var(--hg-color-text)}
.hg-nav-l2{font-weight:var(--hg-font-weight-medium)}
.hg-nav-l3{padding-left:var(--hg-space-4);font-size:var(--hg-font-size-help)}
.hg-nav-horizontal .hg-nav-link{border-left:none;
border-bottom:2px solid transparent}
.hg-nav-horizontal .hg-nav-link:hover{border-left-color:transparent;
border-bottom-color:var(--hg-color-primary)}
.hg-nav-horizontal .hg-nav-l3{padding-left:var(--hg-space-2)}

@media (max-width: 900px){
.hg-nav-vertical{flex-direction:row;flex-wrap:wrap;gap:var(--hg-space-2)}
.hg-nav-vertical .hg-nav-title{width:100%}
.hg-nav-vertical .hg-nav-l3{padding-left:var(--hg-space-2)}
}
@media (max-width: 640px){
.hg-page-head{flex-direction:column;align-items:stretch;
gap:var(--hg-space-3)}
.hg-page-title{font-size:var(--hg-font-size-h2)}
.hg-page-lead{font-size:var(--hg-font-size-body)}
.hg-page-actions{justify-content:flex-start}
.hg-section-h2{font-size:var(--hg-font-size-h3)}
}
"""

_TOPBAR_CSS = """
.hg-topbar{display:flex;align-items:center;justify-content:space-between;
gap:var(--hg-space-4);padding:var(--hg-space-3) 0;
font-family:var(--hg-font-font-family);
border-bottom:1px solid var(--hg-color-border)}
.hg-topbar-sol{display:flex;flex-direction:column;gap:2px;min-width:0}
.hg-topbar-etiket{font-size:var(--hg-font-size-label);
color:var(--hg-color-text-muted);text-transform:uppercase;
letter-spacing:var(--hg-font-tracking-wide);
font-weight:var(--hg-font-weight-semibold)}
.hg-topbar-baslik{font-size:var(--hg-font-size-h3);color:var(--hg-color-text);
font-weight:var(--hg-font-weight-semibold);line-height:var(--hg-font-line-tight);
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hg-topbar-sag{display:flex;align-items:center;gap:var(--hg-space-2);
flex-shrink:0}
.hg-theme-toggle{display:inline-flex;align-items:center;gap:var(--hg-space-2);
padding:var(--hg-space-2) var(--hg-space-3);
border:1px solid var(--hg-color-border-interactive);border-radius:var(--hg-radius-full);
background:var(--hg-color-surface-2);color:var(--hg-color-text);
font-size:var(--hg-font-size-label);font-weight:var(--hg-font-weight-medium);
line-height:1;text-decoration:none;cursor:pointer;
transition:background var(--hg-transition-fast),
border-color var(--hg-transition-fast)}
.hg-theme-toggle:hover{background:var(--hg-color-surface-3);
border-color:var(--hg-color-border-strong)}
.hg-theme-toggle:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus)}
.hg-theme-toggle-ikon{font-size:var(--hg-font-size-sm);line-height:1}
.hg-theme-toggle-metin{line-height:1}
@media (max-width:640px){
.hg-topbar{flex-direction:column;align-items:stretch;gap:var(--hg-space-3)}
.hg-topbar-sag{justify-content:flex-end}
.hg-theme-toggle-metin{display:none}
}
"""

_CHAT_CSS = """
.hg-chat-fab{position:fixed;right:var(--hg-space-5);bottom:var(--hg-space-5);
z-index:var(--hg-z-dropdown);display:inline-flex;align-items:center;
justify-content:center;width:48px;height:48px;
border-radius:var(--hg-radius-full);background:var(--hg-color-primary-solid);
color:var(--hg-color-on-primary);text-decoration:none;
box-shadow:var(--hg-shadow-md);
transition:background var(--hg-transition-fast)}
.hg-chat-fab:hover{background:var(--hg-color-primary-solid-hover)}
.hg-chat-fab:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus)}
.hg-chat-fab-ikon{font-size:var(--hg-font-size-lg);line-height:1}
.hg-chat-panel{position:fixed;right:var(--hg-space-5);bottom:var(--hg-space-5);
z-index:var(--hg-z-dropdown);display:flex;flex-direction:column;
width:320px;max-height:60vh;overflow:hidden;
font-family:var(--hg-font-font-family);
background:var(--hg-color-surface);border:1px solid var(--hg-color-border);
border-radius:var(--hg-radius-modal);box-shadow:var(--hg-shadow-lg)}
.hg-chat-bas{display:flex;align-items:center;justify-content:space-between;
gap:var(--hg-space-2);padding:var(--hg-space-3) var(--hg-space-4);
border-bottom:1px solid var(--hg-color-border);
background:var(--hg-color-surface-2)}
.hg-chat-baslik{font-size:var(--hg-font-size-h3);color:var(--hg-color-text);
font-weight:var(--hg-font-weight-semibold);line-height:var(--hg-font-line-tight)}
.hg-chat-kapat{color:var(--hg-color-text-muted);text-decoration:none;
font-size:var(--hg-font-size-sm);line-height:1;padding:var(--hg-space-1);
border-radius:var(--hg-radius-sm)}
.hg-chat-kapat:hover{color:var(--hg-color-text);
background:var(--hg-color-surface-3)}
.hg-chat-kapat:focus-visible{outline:none;box-shadow:var(--hg-shadow-focus)}
.hg-chat-govde{display:flex;flex-direction:column;gap:var(--hg-space-2);
padding:var(--hg-space-4);overflow-y:auto;flex:1 1 auto}
.hg-chat-bos{margin:0;font-size:var(--hg-font-size-body);
color:var(--hg-color-text-muted);line-height:var(--hg-font-line-normal)}
.hg-chat-mesaj{padding:var(--hg-space-2) var(--hg-space-3);
border-radius:var(--hg-radius-card);font-size:var(--hg-font-size-body);
line-height:var(--hg-font-line-normal);max-width:85%;word-break:break-word}
.hg-chat-mesaj-ai{align-self:flex-start;background:var(--hg-color-surface-2);
color:var(--hg-color-text)}
.hg-chat-mesaj-kullanici{align-self:flex-end;background:var(--hg-color-primary-solid);
color:var(--hg-color-on-primary)}
.hg-chat-not{margin:0;padding:var(--hg-space-2) var(--hg-space-4)
var(--hg-space-3);font-size:var(--hg-font-size-help);
color:var(--hg-color-text-muted);border-top:1px solid var(--hg-color-border)}
@media (max-width:640px){
.hg-chat-panel{right:var(--hg-space-3);left:var(--hg-space-3);width:auto;
bottom:var(--hg-space-3)}
.hg-chat-fab{right:var(--hg-space-3);bottom:var(--hg-space-3)}
}
"""

_ERISIM_CSS = """
@media (prefers-reduced-motion: reduce){
.hg-btn,.hg-card,.hg-input-field,.hg-select-field,.hg-tooltip-bubble,
.hg-nav-link,.hg-theme-toggle,.hg-chat-fab{transition:none}
.hg-spinner{animation:none}
}
"""

#: Bileşen CSS blokları (token bloğu hariç).
_BLOKLAR: tuple[str, ...] = (
    _BUTON_CSS,
    _INPUT_CSS,
    _SELECT_CSS,
    _BADGE_CSS,
    _CARD_CSS,
    _TABLE_CSS,
    _MODAL_CSS,
    _TOOLTIP_CSS,
    _PAGE_CSS,
    _TOPBAR_CSS,
    _CHAT_CSS,
    _ERISIM_CSS,
)


def bilesen_css() -> str:
    """Yalnızca bileşen kurallarını döndürür (token bloğu olmadan)."""
    return "\n".join(blok.strip() for blok in _BLOKLAR)


def tum_css(secici: str = ":root", tema: str = "karanlik") -> str:
    """Token bloğu + tüm bileşen CSS'i.

    Args:
        secici: Token değişkenlerinin yazılacağı kök seçici.
        tema: ``"karanlik"`` veya ``"aydinlik"``. Bileşen kuralları tema
            bağımsızdır; yalnız token değerleri değişir.
    """
    return f"{kok_css(secici, tema)}\n{bilesen_css()}"


def stil_etiketi(secici: str = ":root", tema: str = "karanlik") -> str:
    """`<style>` etiketiyle sarmalanmış tam CSS."""
    return f"<style>\n{tum_css(secici, tema)}\n</style>"


def stil_enjekte(container=None, secici: str = ":root", tema: str = "karanlik") -> str:
    """Streamlit sayfasına stilleri bir kez enjekte eder.

    Aynı oturumda tekrar çağrılırsa yeniden yazmaz — **ancak tema değişirse**
    yeniden yazar (aksi halde gece/gündüz düğmesi etkisiz kalırdı).
    """
    import streamlit as st  # yerel import: test ortamı Streamlit istemez

    hedef = container if container is not None else st
    bayrak = "_hg_stil_tema"
    if getattr(st, "session_state", None) is not None:
        if st.session_state.get(bayrak) == tema:
            return ""
        st.session_state[bayrak] = tema
    css = stil_etiketi(secici, tema)
    hedef.markdown(css, unsafe_allow_html=True)
    return css
