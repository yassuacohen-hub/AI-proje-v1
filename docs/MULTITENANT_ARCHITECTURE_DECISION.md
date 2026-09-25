# Multi-Tenant Mimari Karar Belgesi

> **Task:** DOC-ADMIN-MULTITENANT-KARAR-28  
> **Tarih:** 2026-09-25  
> **Sahip:** utku (ihsan)  
> **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani` (KK-7)  
> **Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

---

## 1. Amaç

Bu belge, Huginn Company Master sisteminin **multi-tenant (çoklu müşteri)** mimarisine geçişi için karar matrisini, seçilen modelin gerekçesini, migration path'ini ve security checklist'i tanımlar.

**Mevcut Durum:** Single-tenant (tek müşteri)  
**Hedef:** Multi-tenant (çoğu müşteri, izolasyonlu)

---

## 2. Tenant Modelleri Karşılaştırması

| Kriter | A) Row-Level Security (RLS) | B) Schema Separation | C) Dedicated DBs |
|--------|----------------------------|---------------------|------------------|
| **İzolasyon** | Orta (query-level) | Yüksek (schema-level) | Çok Yüksek (DB-level) |
| **Maliyet** | Düşük (tek DB) | Orta (şema sayısı kadar) | Yüksek (DB başına maliyet) |
| **Karmaşıklık** | Orta (policy management) | Yüksek (migration sync) | Çok Yüksek (ops overhead) |
| **Performans** | İyi (tek connection pool) | İyi (şema bazlı optimize) | En İyi (izole kaynaklar) |
| **Operasyonel Yük** | Düşük | Orta | Yüksek (backup/monitoring/DB) |
| **Migration** | Kolay (policy ekle) | Orta (schema copy) | Zor (data migration) |
| **Schema Sync** | Otomatik | Manuel/otomatik | Manuel |

**Skorlar (1-5, 5 en iyi):**

| Kriter | Ağırlık | RLS | Schema Sep | Dedicated DB |
|--------|---------|-----|------------|--------------|
| İzolasyon | 30% | 3 | 4 | 5 |
| Maliyet | 20% | 5 | 3 | 2 |
| Karmaşıklık | 20% | 4 | 3 | 2 |
| Performans | 15% | 4 | 4 | 5 |
| Operasyonel Yük | 15% | 5 | 3 | 2 |
| **Ağırlıklı Toplam** | **100%** | **3.85** | **3.45** | **3.30** |

**Seçim:** **B) Schema Separation** (mid-term) → **C) Dedicated DBs** (scale-up sonrası)

**Gerekçe:** 
- RLS (A) yeterli izolasyon sağlamıyor (cross-tenant leak riski)
- Dedicated DB (C) operasyonel olarak çok pahalı/karmaşık başlangıçta
- Schema Separation (B) dengeli: yeterli izolasyon, yönetilebilir maliyet, PostgreSQL schema'ları native destekler

---

## 3. İmplementasyon Spec

### 3.1 Temel Yapı

```sql
-- Her tabloya tenant_id eklenecek (NOT NULL, default 'default')
ALTER TABLE companies ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE users ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE credit_ledger ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
-- ... tüm tablolar

-- Unique constraint: tenant içinde benzersizlik
ALTER TABLE companies ADD CONSTRAINT uq_companies_tenant_name UNIQUE (tenant_id, legal_name);
ALTER TABLE users ADD CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email);
```

### 3.2 Tenant Tablosu

```sql
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,  -- URL-friendly
    status VARCHAR(20) DEFAULT 'active',  -- active, suspended, trial
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Billing
    billing_email VARCHAR(255),
    billing_cycle VARCHAR(20) DEFAULT 'monthly',  -- monthly, yearly
    tier VARCHAR(20) DEFAULT 'terminal',  -- terminal, strategic, enterprise
    
    -- Limits
    max_users INTEGER DEFAULT 10,
    max_credits_per_month INTEGER DEFAULT 1000,
    max_api_calls_per_day INTEGER DEFAULT 10000,
    
    -- Config
    settings JSONB DEFAULT '{}',  -- tenant-specific settings
    features JSONB DEFAULT '[]'   -- enabled feature flags
);

-- Admin tenant (sistem tenant'ı)
INSERT INTO tenants (tenant_id, name, slug, status, tier) 
VALUES ('00000000-0000-0000-0000-000000000000', 'Huginn Admin', 'admin', 'active', 'enterprise');
```

### 3.3 Schema Yapısı

```
public (shared)
├── tenants (shared)
├── admin_* (shared - admin tables)

tenant_<uuid> (per-tenant schema)
├── companies
├── users
├── credit_ledger
├── user_activity_log
├── admin_audit_log
├── admin_mfa
├── admin_audit_log
├── plan_field_group
├── company_intelligence
└── ... (diğer tenant-specific tablolar)
```

### 3.4 Application-Level Query Wrapper

```python
# src/company_master/api/core/tenant.py

from contextvars import ContextVar
from sqlalchemy import text

# Request-scoped tenant context
_current_tenant: ContextVar[UUID | None] = ContextVar('_current_tenant', default=None)

def set_current_tenant(tenant_id: UUID) -> None:
    """Request başında tenant set et."""
    _current_tenant.set(tenant_id)

def get_current_tenant() -> UUID | None:
    """Mevcut tenant'ı al."""
    return _current_tenant.get()

def with_tenant(query: str, params: dict = None) -> tuple[str, dict]:
    """Query'ye tenant_id filtresi ekle."""
    tenant_id = get_current_tenant()
    if not tenant_id:
        return query, params or {}
    
    # Basit WHERE tenant_id = :tenant_id ekle
    # Gerçek implementasyonda SQL parser kullan
    if 'WHERE' in query.upper():
        query = query.replace('WHERE', f'WHERE tenant_id = :tenant_id AND')
    else:
        query = query + ' WHERE tenant_id = :tenant_id'
    
    params = params or {}
    params['tenant_id'] = str(tenant_id)
    return query, params
```

### 3.5 Middleware (FastAPI)

```python
# web_app.py - middleware ekle
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Subdomain veya header'dan tenant_id çıkar
        tenant_id = self._extract_tenant_id(request)
        if tenant_id:
            set_current_tenant(UUID(tenant_id))
        try:
            response = await call_next(request)
        finally:
            set_current_tenant(None)  # cleanup
        return response
    
    def _extract_tenant_id(self, request: Request) -> str | None:
        # 1. Subdomain: tenant.huginn.local
        host = request.headers.get('host', '')
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain not in ('www', 'api', 'admin'):
                return subdomain
        
        # 2. Header
        return request.headers.get('X-Tenant-ID')
```

---

## 4. Migration Path (4 Faz)

| Faz | Süre | Açıklama | Deliverable |
|-----|------|----------|-------------|
| **Phase 0 (Current)** | 2026 Q3 | Single tenant (default tenant_id='0') | Mevcut sistem |
| **Phase 1 (Schema Ready)** | 2026 Q4 | Schema separation ready, env flag ile aktif | `ALTYAPI-VERI-GORUNURLUK-01` tamamlama |
| **Phase 2 (Multi-Tenant UI)** | 2027 Q1 | Tenant create/manage UI, admin panel | `UI-ADMIN-TENANT-MANAGE` |
| **Phase 3 (Per-Tenant Billing)** | 2027 Q2 | Per-tenant billing, usage tracking | `API-TENANT-BILLING` |

### Phase 1 Detayları (Q4 2026)

```bash
# Migration script
# 1. tenants tablosu oluştur
# 2. Tüm tablolara tenant_id kolonu ekle (default '00000000-0000-0000-0000-000000000000')
# 3. Unique constraints ekle (tenant_id + identifier)
# 3. Default tenant oluştur (admin tenant)
# 4. Mevcut verileri default tenant'a ata
# 5. Index'ler oluştur
```

---

## 5. Security Audit Checklist

| # | Kontrol | Açıklama | Test Yöntemi |
|---|---------|----------|--------------|
| 1 | **Tenant ID Filter** | Tüm query'lerde tenant_id filtresi var mı? | Code review + integration test |
| 2 | **API Endpoint Check** | Tüm endpoint'ler tenant check yapıyor mu? | API test suite |
| 3 | **Audit Log** | Audit log'da tenant_id kaydediliyor mu? | Log inspection |
| 4 | **Cross-Tenant Leak** | Cross-tenant data leak var mı? | Penetration test |
| 5 | **Admin Isolation** | Admin tenant (`_admin`) diğer tenant'lerden izole mi? | Integration test |
| 6 | **RLS/Policy** | Schema separation aktif mi? | Schema inspection |
| 7 | **Tenant ID Injection** | Tenant ID injection mümkün mü? | Fuzzing test |
| 8 | **Data Export** | Export'te tenant filtresi var mı? | Export test |
| 9 | **Backup/Restore** | Tenant bazlı backup/restore çalışıyor mu? | DR test |
| 10 | **Cross-Tenant Query** | Admin cross-tenant query yetkisi kontrol ediliyor mu? | RBAC test |

**Test Case Örnekleri:**

```python
# tests/test_multi_tenant_isolation.py
def test_cross_tenant_leak():
    """Tenant A verisi Tenant B'ye sızmamalı."""
    tenant_a = create_tenant("tenant-a")
    tenant_b = create_tenant("tenant-b")
    
    create_company(tenant_a, "Company A")
    create_company(tenant_b, "Company B")
    
    # Tenant A context
    set_current_tenant(tenant_a.id)
    companies = get_companies()
    assert all(c.tenant_id == tenant_a.id for c in companies)
    
    # Tenant B context
    set_current_tenant(tenant_b.id)
    companies = get_companies()
    assert all(c.tenant_id == tenant_b.id for c in companies)

def test_admin_cross_tenant_access():
    """Admin tenant tüm tenant'ları görebilmeli, normal tenant sadece kendisini."""
    admin_tenant = get_admin_tenant()
    set_current_tenant(admin_tenant.id)
    all_companies = get_companies()  # Tüm tenant'ları içermeli
    
    normal_tenant = create_tenant("normal")
    set_current_tenant(normal_tenant.id)
    companies = get_companies()  # Sadece kendi tenant'ı
```

---

## 6. Kod Örnekleri

### 6.1 Schema Migration (tenant_id ekleme)

```sql
-- migrations/0020_add_tenant_id.sql

-- Tenant tablosu
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    tier VARCHAR(20) DEFAULT 'terminal',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    billing_email VARCHAR(255),
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    settings JSONB DEFAULT '{}',
    features JSONB DEFAULT '[]'
);

-- Admin tenant
INSERT INTO tenants (tenant_id, name, slug, status, tier) 
VALUES ('00000000-0000-0000-0000-000000000000', 'Huginn Admin', 'admin', 'active', 'enterprise');

-- Mevcut tablolara tenant_id ekle
ALTER TABLE companies ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE users ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE credit_ledger ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE user_activity_log ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE admin_audit_log ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
ALTER TABLE admin_mfa ADD COLUMN tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';

-- Unique constraints
ALTER TABLE companies ADD CONSTRAINT uq_companies_tenant_name UNIQUE (tenant_id, legal_name);
ALTER TABLE users ADD CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email);

-- Indexler
CREATE INDEX idx_companies_tenant ON companies(tenant_id);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_credit_ledger_tenant ON credit_ledger(tenant_id);
```

### 6.2 SQLAlchemy Query Wrapper

```python
# src/company_master/api/core/tenant.py

from contextvars import ContextVar
from uuid import UUID
from sqlalchemy import text
from typing import Any

_current_tenant: ContextVar[UUID | None] = ContextVar('_current_tenant', default=None)

def set_current_tenant(tenant_id: UUID | None) -> None:
    _current_tenant.set(tenant_id)

def get_current_tenant() -> UUID | None:
    return _current_tenant.get()

def apply_tenant_filter(query: str, params: dict = None) -> tuple[str, dict]:
    """Query'ye tenant_id filtresi ekle."""
    tenant_id = get_current_tenant()
    if not tenant_id:
        return query, params or {}
    
    params = params or {}
    params['tenant_id'] = str(_current_tenant.get())
    
    # Basit WHERE ekle (gerçekte SQL parser kullanılmalı)
    upper_query = query.upper()
    if 'WHERE' in upper_query:
        # WHERE kelimesini bul ve sonrasına ekle
        idx = upper_query.index('WHERE') + 5
        query = query[:idx] + f' tenant_id = :tenant_id AND' + query[idx:]
    else:
        query = query + ' WHERE tenant_id = :tenant_id'
    
    return query, params

# Kullanım:
# query, params = apply_tenant_filter("SELECT * FROM companies WHERE is_active = TRUE")
# result = conn.execute(text(query), params).mappings().all()
```

### 6.3 FastAPI Middleware

```python
# web_app.py - TenantMiddleware

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from uuid import UUID

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = self._extract_tenant_id(request)
        if tenant_id:
            try:
                set_current_tenant(UUID(tenant_id))
            except ValueError:
                pass  # Invalid UUID, ignore
        
        try:
            response = await call_next(request)
        finally:
            set_current_tenant(None)  # Cleanup
        return response
    
    def _extract_tenant_id(self, request: Request) -> str | None:
        # 1. Subdomain: tenant.huginn.local
        host = request.headers.get('host', '')
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain not in ('www', 'api', 'admin', 'localhost'):
                return subdomain
        
        # 2. Header
        return request.headers.get('X-Tenant-ID')
```

### 6.4 API Endpoint Tenant Filter

```python
# web_app.py - örnek endpoint

@app.get("/api/companies")
def api_companies(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    _auth: str = Depends(require_api_key)
):
    """Tenant-aware company listesi."""
    from company_master.api.core.tenant import get_current_tenant, apply_tenant_filter
    
    tenant_id = get_current_tenant()
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant context yok")
    
    engine = get_engine()
    with engine.connect() as conn:
        # Tenant filter uygula
        base_query = """
            SELECT * FROM companies 
            WHERE is_ankara = TRUE AND is_osb_member = TRUE
            ORDER BY legal_name
            LIMIT :lim OFFSET :off
        """
        query, params = apply_tenant_filter(base_query, {"lim": limit, "off": offset})
        rows = conn.execute(text(query), params).mappings().all()
    
    return [dict(r) for r in rows]
```

---

## 7. Timeline

| Faz | Dönem | Milestone | Sorumlu |
|-----|-------|-----------|---------|
| Phase 0 | 2026 Q3 | Single tenant (mevcut) | - |
| Phase 1 | 2026 Q4 | Schema separation ready, env flag | Utku + Orkestratör |
| Phase 2 | 2027 Q1 | Tenant CRUD UI, admin panel | Utku |
| Phase 3 | 2027 Q2 | Per-tenant billing, usage tracking | Utku + Yasu |

---

## 8. İlgili Nodlar

- [[Huginn Data Insights/AGENTS.md]] — D-xxx (karar matris pattern)
- [[Huginn Data Insights/Huginn Data Insights/README.md]] — Sistem mimarisi
- [[Huginn Data Insights/src/company_master]] — Current single-tenant schema
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Multi-tenant admin control
- [[Huginn Data Insights/docs/MULTITENANT_ARCHITECTURE_DECISION.md]] — Bu belge

---

> **Not:** Bu belge `docs/MULTITENANT_ARCHITECTURE_DECISION.md` olarak kaydedilir. Güncellemeler SSOT (ADMIN-KİT) ile senkronize edilir.

> **Ponytail:** Şu an single-tenant. Multi-tenant geçişi 6-9 ay operasyonel efor. Recommendation: Phase 0→1 (schema ready) devam et, Phase 2+ opsiyonel; customer demand ve operational maturity'ye bağlı.

> **Uyarı:** Cross-tenant data leak kritik risk. Belgeye 10+ security test case'i eklenecek (prod'da penetration test gerekebilir).

> **Karar Referansı:** [[Huginn Data Insights/AGENTS.md#D-209]] — Architecture decision log (yeni D-xxx karar buraya eklenecek).