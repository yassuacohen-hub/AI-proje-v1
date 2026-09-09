# -*- coding: utf-8 -*-
"""Job Intelligence — Pydantic veri modelleri."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c-level"
    HEAD = "head"
    UNKNOWN = "unknown"


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERN = "intern"
    FREELANCE = "freelance"
    UNKNOWN = "unknown"


class RemoteType(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


class SignalType(str, Enum):
    GROWTH = "growth"
    RISK = "risk"
    TECH_TRANSFORMATION = "tech_transformation"
    INVESTMENT = "investment"
    GEO_EXPANSION = "geo_expansion"
    ORG_CHANGE = "org_change"


class HiringTrend(str, Enum):
    ACCELERATING = "accelerating"
    STABLE = "stable"
    DECELERATING = "decelerating"
    UNKNOWN = "unknown"


class JobPostingBase(BaseModel):
    """İş ilanı temel modeli."""
    source_name: str = Field(..., description="Kaynak adı: kariyer.net, iskur, company_career, linkedin")
    source_url: HttpUrl = Field(..., description="İlanın orijinal URL'si")
    external_id: str | None = Field(None, description="Kaynağın kendi ID'si")
    title: str = Field(..., description="Pozisyon başlığı")
    description: str | None = Field(None, description="İlan açıklaması")
    department: str | None = Field(None, description="Departman: Engineering, Sales, HR, vb.")
    seniority_level: SeniorityLevel = Field(default=SeniorityLevel.UNKNOWN, description="Kıdem seviyesi")
    location_city: str | None = Field(None, description="Şehir")
    location_country: str = Field(default="Türkiye", description="Ülke")
    employment_type: EmploymentType = Field(default=EmploymentType.UNKNOWN, description="Çalışma tipi")
    remote_type: RemoteType = Field(default=RemoteType.UNKNOWN, description="Uzaktan çalışma tipi")
    technologies: list[str] = Field(default_factory=list, description="Teknolojiler: ['Python', 'AWS', 'Kubernetes']")
    salary_min: int | None = Field(None, description="Minimum maaş (TL, yıllık)")
    salary_max: int | None = Field(None, description="Maksimum maaş (TL, yıllık)")
    salary_currency: str = Field(default="TRY", description="Para birimi")
    posted_at: datetime | None = Field(None, description="İlan yayın tarihi")
    expired_at: datetime | None = Field(None, description="İlan bitiş tarihi")
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Ham veri (kaynağa özgü ek alanlar)")


class JobPostingCreate(JobPostingBase):
    """İş ilanı oluşturma modeli."""
    pass


class JobPosting(JobPostingBase):
    """İş ilanı tam modeli (DB'den gelen)."""
    job_posting_id: UUID
    company_id: UUID | None = None
    collected_at: datetime
    content_hash: str | None = None

    class Config:
        from_attributes = True


class CompanySignalBase(BaseModel):
    """Şirket sinyali temel modeli."""
    company_id: UUID
    signal_type: SignalType
    signal_subtype: str | None = None
    score: float = Field(default=0.0, ge=0, le=100)
    confidence: float = Field(default=0.0, ge=0, le=100)
    evidence: dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=datetime.now)
    valid_until: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompanySignal(CompanySignalBase):
    """Şirket sinyali tam modeli."""
    signal_id: UUID

    class Config:
        from_attributes = True


class CompanyIntelligenceScoresBase(BaseModel):
    """Şirket istihbarat skorları temel modeli."""
    company_id: UUID
    growth_score: float = Field(default=0.0, ge=0, le=100)
    expansion_score: float = Field(default=0.0, ge=0, le=100)
    tech_transformation_score: float = Field(default=0.0, ge=0, le=100)
    investment_signal_score: float = Field(default=0.0, ge=0, le=100)
    org_change_score: float = Field(default=0.0, ge=0, le=100)
    risk_score: float = Field(default=0.0, ge=0, le=100)
    hiring_trend: HiringTrend = Field(default=HiringTrend.UNKNOWN)
    new_locations: list[str] = Field(default_factory=list)
    new_departments: list[str] = Field(default_factory=list)
    critical_hires: list[dict[str, Any]] = Field(default_factory=list)
    detected_signals: list[dict[str, Any]] = Field(default_factory=list)
    signal_count_30d: int = Field(default=0)
    signal_count_90d: int = Field(default=0)
    overall_confidence: float = Field(default=0.0, ge=0, le=100)


class CompanyIntelligenceScores(CompanyIntelligenceScoresBase):
    """Şirket istihbarat skorları tam modeli."""
    last_calculated_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyTechProfileBase(BaseModel):
    """Şirket teknoloji profili temel modeli."""
    company_id: UUID
    technologies: dict[str, int] = Field(default_factory=dict)  # {"Python": 15, "AWS": 8}
    tech_categories: dict[str, list[str]] = Field(default_factory=dict)  # {"languages": ["Python", "Java"]}
    modernization_signals: list[dict[str, Any]] = Field(default_factory=list)
    tech_stack_maturity: float = Field(default=0.0, ge=0, le=100)
    innovation_index: float = Field(default=0.0, ge=0, le=100)


class CompanyTechProfile(CompanyTechProfileBase):
    """Şirket teknoloji profili tam modeli."""
    last_updated: datetime

    class Config:
        from_attributes = True


class CompanyAliasBase(BaseModel):
    """Şirket alias modeli."""
    company_id: UUID
    alias_name: str
    alias_type: str = Field(default="fuzzy")  # exact, fuzzy, domain, mersis, manual
    confidence: float = Field(default=100.0, ge=0, le=100)
    source: str = Field(default="system")  # system, manual, mersis, gib


class CompanyAlias(CompanyAliasBase):
    """Şirket alias tam modeli."""
    alias_id: UUID
    created_at: datetime
    verified_at: datetime | None = None
    verified_by: str | None = None

    class Config:
        from_attributes = True


class SignalEvidence(BaseModel):
    """Sinyal kanıtı modeli."""
    job_posting_ids: list[UUID] = Field(default_factory=list)
    date_range: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    supporting_sources: list[str] = Field(default_factory=list)