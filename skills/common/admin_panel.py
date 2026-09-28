# PRD Admin Panel Yetenekleri
# Kaynak: PRD Admin Panel skill.txt (SUPER ADMIN PANEL PRD Versiyon: 1.0)

from skills.base import registry


@registry.register(
    name="generate_admin_dashboard_kpis",
    description="Admin dashboard KPI kartlarını üretir: toplam tenant, aktif/trial/pasif, DAU/MAU, MRR/ARR."
)
def generate_admin_dashboard_kpis(tenant_data: dict) -> dict:
    """KPI kartları hesaplar."""
    return {
        "toplam_tenant": tenant_data.get("total", 0),
        "aktif_tenant": tenant_data.get("active", 0),
        "trial_tenant": tenant_data.get("trial", 0),
        "pasif_tenant": tenant_data.get("inactive", 0),
        "toplam_kullanici": tenant_data.get("total_users", 0),
        "gunluk_aktif_kullanici": tenant_data.get("dau", 0),
        "aylik_aktif_kullanici": tenant_data.get("mau", 0),
        "toplam_arama": tenant_data.get("total_searches", 0),
        "toplam_ai_sorgu": tenant_data.get("total_ai_queries", 0),
        "api_cagrilari": tenant_data.get("api_calls", 0),
        "mrr": tenant_data.get("mrr", 0.0),
        "arr": tenant_data.get("arr", 0.0)
    }
@registry.register(
    name="analyze_tenant_health",
    description="Tenant sağlık skorunu hesaplar: plan, kullanım, aktivite, ödeme durumu."
)
def analyze_tenant_health(tenant_id: str, usage_data: dict, plan_data: dict) -> dict:
    """Tenant sağlık skorunu 0-100 aralığında hesaplar."""
    score = 50
    if usage_data.get("dau", 0) > 0:
        score += 20
    if plan_data.get("status") == "active":
        score += 20
    if usage_data.get("ai_usage", 0) > 0:
        score += 10
    
    return {
        "tenant_id": tenant_id,
        "health_score": min(score, 100),
        "risk_level": "Düşük" if score >= 70 else ("Orta" if score >= 40 else "Yüksek"),
        "last_activity": usage_data.get("last_activity"),
        "plan_status": plan_data.get("status")
    }


@registry.register(
    name="analyze_churn_risk",
    description="Churn riskini analiz eder: 14 gün giriş yok, arama yok, AI kullanımı yok kuralları."
)
def analyze_churn_risk(tenant_id: str, activity_data: dict) -> dict:
    """Churn risk seviyesini belirler."""
    days_since_login = activity_data.get("days_since_login", 999)
    days_since_search = activity_data.get("days_since_search", 999)
    days_since_ai = activity_data.get("days_since_ai", 999)
    
    risk_factors = []
    if days_since_login > 14:
        risk_factors.append("14ünden uzun süredir giriş yok")
    if days_since_search > 14:
        risk_factors.append("14ünden uzun süredir arama yok")
    if days_since_ai > 14:
        risk_factors.append("14ünden uzun süredir AI kullanımı yok")
    
    if len(risk_factors) >= 2:
        level = "Yüksek"
    elif len(risk_factors) == 1:
        level = "Orta"
    else:
        level = "Düşük"
    
    return {
        "tenant_id": tenant_id,
        "churn_risk": level,
        "risk_factors": risk_factors,
        "days_inactive": max(days_since_login, days_since_search, days_since_ai)
    }


@registry.register(
    name="track_ai_costs",
    description="AI maliyetlerini takip eder: günlük/haftalık/aylık maliyet, tenant bazlı, token kullanımı."
)
def track_ai_costs(cost_data: dict) -> dict:
    """AI maliyetlerini hesaplar ve özetler."""
    daily = cost_data.get("daily", 0.0)
    weekly = cost_data.get("weekly", 0.0)
    monthly = cost_data.get("monthly", 0.0)
    tenant_costs = cost_data.get("tenant_breakdown", {})
    
    return {
        "daily_cost": daily,
        "weekly_cost": weekly,
        "monthly_cost": monthly,
        "tenant_breakdown": tenant_costs,
        "total_tokens": cost_data.get("total_tokens", 0),
        "input_tokens": cost_data.get("input_tokens", 0),
        "output_tokens": cost_data.get("output_tokens", 0),
        "avg_cost_per_query": monthly / max(cost_data.get("total_queries", 1), 1) if monthly > 0 else 0
    }


@registry.register(
    name="analyze_data_quality",
    description=(
        "İletişim bilgisi doluluğu: eksik telefon, email, website, sektör, "
        "LinkedIn, NACE sayısı ve 0-100 doluluk yüzdesi. "
        "Kimlik dosyası tamlığı (0-10) DEĞİLDİR."
    )
)
def analyze_data_quality(company_data: list) -> dict:
    """Şirket verileri üzerinden iletişim bilgisi doluluk yüzdesi hesaplar.

    D-250: "kalite skoru" adi yanltiiciydi. Bu metrik `identity_completeness`
    (0-10, tek kapi `etl/quality_recalc.py`) DEGILDIR; burada verilen listedeki
    alanlarin doluluk yuzdesidir ve 100'u gercekten ulasilabilir. Bu yuzden
    `sunum.puan_metni` ile sunulmaz --- tavan kisitli degil. Karismasin diye
    donen anahtarlar olcegini adinda tasir.
    """
    total = len(company_data)
    if total == 0:
        return {"error": "Veri yok"}
    
    missing = {"telefon": 0, "email": 0, "website": 0, "sektor": 0, "linkedin": 0, "nace": 0}
    quality_scores = []
    
    for company in company_data:
        score = 100
        if not company.get("telefon"):
            missing["telefon"] += 1
            score -= 15
        if not company.get("email"):
            missing["email"] += 1
            score -= 15
        if not company.get("website"):
            missing["website"] += 1
            score -= 10
        if not company.get("sektor"):
            missing["sektor"] += 1
            score -= 20
        if not company.get("linkedin"):
            missing["linkedin"] += 1
            score -= 10
        if not company.get("nace"):
            missing["nace"] += 1
            score -= 10
        quality_scores.append(max(score, 0))
    
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    return {
        "total_companies": total,
        "missing_fields": missing,
        "completion_rate": {
            k: round((total - v) / total * 100, 1) for k, v in missing.items()
        },
        "ort_iletisim_dolulugu_yuzde": round(avg_quality, 1),
        "iletisim_dolulugu_dagilimi_yuzde": {
            "0-20": sum(1 for s in quality_scores if s <= 20),
            "21-40": sum(1 for s in quality_scores if 21 <= s <= 40),
            "41-60": sum(1 for s in quality_scores if 41 <= s <= 60),
            "61-80": sum(1 for s in quality_scores if 61 <= s <= 80),
            "81-100": sum(1 for s in quality_scores if 81 <= s <= 100)
        }
    }


@registry.register(
    name="generate_security_alerts",
    description="Güvenlik dashboardu: başarılı/başarısız girişler, şüpheli aktiviteler, kilitli hesaplar."
)
def generate_security_alerts(auth_logs: list) -> dict:
    """Güvenlik loglarından alert üretir."""
    failed = [l for l in auth_logs if l.get("status") == "failed"]
    suspicious = [l for l in auth_logs if l.get("suspicious", False)]
    locked = [l for l in auth_logs if l.get("locked", False)]
    
    alerts = []
    if len(failed) > 10:
        alerts.append(f"Yüksek başarısız giriş: {len(failed)} deneme")
    if len(suspicious) > 0:
        alerts.append(f"Şüpheli aktivite: {len(suspicious)} olay")
    if len(locked) > 0:
        alerts.append(f"Kilitli hesap: {len(locked)} hesap")
    
    return {
        "total_logins": len(auth_logs),
        "failed_logins": len(failed),
        "suspicious_activities": len(suspicious),
        "locked_accounts": len(locked),
        "alerts": alerts,
        "severity": "Yüksek" if len(alerts) >= 2 else ("Orta" if len(alerts) == 1 else "Düşük")
    }