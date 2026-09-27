# GÖREV BRIËFI: YASU-04 — Durum Yönetimi - State Management

**Atanan:** yasu  
**Öncelik:** P0  
**Deadline:** 2026-10-01T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Redux veya Zustand kullanarak global state management sistemi kur. User auth state, UI state, data cache'i merkezi olarak yönet.

## Kabul Kriterleri
1. Redux store yapısı yazılmalı (frontend/store/redux_store.ts)
2. 5+ reducer yazılmalı
3. DevTools entegrasyonu

## Kaynaklar (SSOT)
- frontend/store/redux_store.ts
- Redux Toolkit documentation

## İmplantasyon Notları
- Redux Toolkit kullan (boilerplate azalt)
- Redux Thunk for async actions
- Middleware: logger, crash reporter

## Proof-of-Work
File/Output: frontend/store/redux_store.ts + reducers + selectors + integration tests
