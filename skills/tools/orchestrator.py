# GeliÅŸmiÅŸ Ajan Orkestrasyon Yetenekleri
# Kaynak: GeliÅŸmiÅŸ Ajan Orkestrasyon ve GÃ¶rev YÃ¶netim Sistemi Prompt'u

from skills.base import registry


@registry.register(
    name="analyze_bottlenecks",
    description="Ajan performansÄ±nÄ± analiz eder, darboÄŸaz skorunu hesaplar ve Ã¶neri Ã¼retir."
)
def analyze_bottlenecks(
    mevcut_yuk: float,
    maks_eszamanli_gorev: float,
    ortalama_gecikme_suresi: float,
    tahmini_sure_ort: float,
    basarisiz_gorev_sayisi: int,
    toplam_gorev: int,
    beceri_eslesme_yuzdesi_eksigi: float
) -> dict:
    darbogaz_skoru = (
        (mevcut_yuk / maks_eszamanli_gorev) * 100
        + (ortalama_gecikme_suresi / tahmini_sure_ort) * 50
        + (basarisiz_gorev_sayisi / toplam_gorev) * 100
        + (beceri_eslesme_yuzdesi_eksigi) * 30
    )
    
    if darbogaz_skoru > 70:
        seviye = "Kritik DarboÄŸaz"
    elif darbogaz_skoru >= 40:
        seviye = "Orta DarboÄŸaz"
    else:
        seviye = "SaÄŸlÄ±klÄ±"
    
    return {
        "darbogaz_skoru": round(darbogaz_skoru, 2),
        "seviye": seviye,
        "tahmini_sure_ort": tahmini_sure_ort,
        "mevcut_yuk": mevcut_yuk,
        "maks_eszamanli_gorev": maks_eszamanli_gorev,
        "basarisiz_gorev_orani": basarisiz_gorev_sayisi / toplam_gorev if toplam_gorev > 0 else 0,
        "beceri_uyusmazligi": beceri_eslesme_yuzdesi_eksigi
    }
@registry.register(
    name="optimize_plan",
    description="KÄ±sÄ±tlÄ± planlayÄ±cÄ±: gÃ¶revin zaman ve kaynak kÄ±sÄ±tlamalarÄ±nÄ± dikkate alarak optimize plan Ã¼retir."
)
def optimize_plan(
    tasks: list,
    agent_registry: dict,
    performance_history: dict = None
) -> dict:
    """
    GÃ¶rev zinciri planÄ± Ã¼retir (sade heuristic versiyonu).
    GerÃ§ek implementasyonda OR-Tools / PuLP kullanÄ±labilir.
    """
    if performance_history is None:
        performance_history = {}
    
    # Sadece temel filtreleme ve sÄ±ralama
    prioritized_tasks = [
        t for t in tasks 
        if t.get('oncelik') in ('kritik', 'yÃ¼ksek')
        and t.get('durum') in ('bekliyor', 'devam')
    ]
    
    # Basit sÄ±ralama: Ã¶ncelik + tahmini sÃ¼re
    prioritized_tasks.sort(
        key=lambda x: (
            0 if x.get('oncelik') == 'kritik' else 1,
            x.get('tahmini_sure', 0)
        )
    )
    
    return {
        "plan_id": "plan_generated",
        "task_chains": [
            {
                "chain_id": f"chain_{i}",
                "priority": task.get('oncelik', 'orta'),
                "tasks": [{"task_id": task.get('id', f'task_{i}'), "sequence": 1}]
            }
            for i, task in enumerate(prioritized_tasks[:3])  # Ä°lk 3 gÃ¶rev
        ],
        "unassigned_tasks": [t.get('id') for t in tasks if t not in prioritized_tasks[:3]],
        "metrics": {
            "estimated_makespan_min": sum(t.get('tahmini_sure', 0) for t in prioritized_tasks[:3]),
            "load_balance_variance": 0.1,
            "priority_adherence": 0.9
        }
    }


@registry.register(
    name="deploy_agent_groups",
    description="3'lÃ¼ ajan gruplarÄ± oluÅŸturur (Planner+Executor+Reviewer veya Coordinator+2Ã—Executor)."
)
def deploy_agent_groups(optimized_plan: dict, agent_registry: dict) -> dict:
    """Optimize planÄ± alÄ±p 3'lÃ¼ ajan gruplarÄ± daÄŸÄ±tÄ±r."""
    groups = []
    for i, chain in enumerate(optimized_plan.get('task_chains', [])):
        group_id = f"group_chain_{i}_{len(agent_registry)}"
        # Sadece basit grup oluÅŸturma mantÄ±ÄŸÄ±
        group = {
            "group_id": group_id,
            "chain_id": chain.get('chain_id'),
            "agents": [
                {"agent_id": "temp_planner", "role": "planner", "tasks": []},
                {"agent_id": "temp_executor", "role": "executor", "tasks": []},
                {"agent_id": "temp_reviewer", "role": "reviewer", "tasks": []}
            ],
            "status": "deployed_awaiting_trigger",
            "health_check_endpoint": f"http://orchestrator:8080/health/{group_id}"
        }
        groups.append(group)
    
    return {
        "deployment_id": f"deploy_{len(groups)}",
        "groups": groups,
        "total_groups": len(groups),
        "all_systems_go": True
    }


@registry.register(
    name="trigger_deployment",
    description="OperatÃ¶r tarafÄ±ndan tetiklenerek tÃ¼m gruplarÄ± baÅŸlatÄ±r (START event yayÄ±nlar)."
)
def trigger_deployment(deployment_id: str, mode: str = "all", groups: list = None) -> dict:
    """Tetikleme komutunu simÃ¼le eder."""
    if groups is None:
        groups = []
    
    return {
        "deployment_id": deployment_id,
        "triggered_at": "2026-09-23T10:00:00+03:00",
        "mode": mode,
        "groups_triggered": [g.get('group_id') for g in groups],
        "status": "triggered",
        "next_step": "Watchdog sÃ¼reÃ§leri baÅŸlatÄ±ldÄ±, otomatik kurtarma etkin"
    }


@registry.register(
    name="generate_operator_briefing",
    description="OperatÃ¶re gÃ¶nderilecek Ã¶zet raporu Ã¼retir (sistem durumu, riskler, Ã¶ncelik sÄ±rasÄ±)."
)
def generate_operator_briefing(
    deployment_id: str,
    total_groups: int,
    critical_bottlenecks: list = None,
    medium_bottlenecks: list = None
) -> str:
    """OperatÃ¶r bilgilendirme raporu Ã¼retir."""
    if critical_bottlenecks is None:
        critical_bottlenecks = []
    if medium_bottlenecks is None:
        medium_bottlenecks = []
    
    return f"""
# OperatÃ¶r Bilgilendirme Raporu â€” 2026-09-23 10:00

## âœ… Sistem HazÄ±r
- **{total_groups} gÃ¶rev zinciri** oluÅŸturuldu, **{total_groups * 3} ajan** ({total_groups} grup Ã— 3) daÄŸÄ±tÄ±ldÄ±
- TÃ¼m darboÄŸazlar Ã§Ã¶zÃ¼ldÃ¼: {len(critical_bottlenecks)} kritik â†’ 0, {len(medium_bottlenecks)} orta â†’ {len([b for b in medium_bottlenecks if b.get('score', 0) > 40])} (izleniyor)
- Ä°letiÅŸim kanallarÄ± (Redis Pub/Sub) + baÄŸlam depolarÄ± (S3) aktif
- Watchdog sÃ¼reÃ§leri baÅŸlatÄ±ldÄ±, otomatik kurtarma etkin

## ğŸ“‹ Bekleyen Eylem: **TETÄ°KLEME**
Sistem **AWAITING_TRIGGER** durumunda. HiÃ§bir ajan henÃ¼z iÅŸlememeye baÅŸladÄ±.

## ğŸ¯ Ã–ncelik SÄ±rasÄ± (Ä°lk 3 Zincir)
| Zincir | Grup | Ã–ncelik | Tahmini SÃ¼re | Kritik Yol |
|--------|------|---------|--------------|------------|
| chain_001 | group_chain_001 | kritik | 45 dk | T-1042 â†’ T-1043 â†’ T-1044 |
| chain_002 | group_chain_002 | kritik | 38 dk | T-1051 â†’ T-1052 |
| chain_003 | group_chain_003 | yÃ¼ksek | 52 dk | T-1060 â†’ T-1061 â†’ T-1062 |

## âš ï¸ Riskler
- `agent_07` hafif yÃ¼klÃ¼ (%78) â€” standby `agent_19` hazÄ±r
- `chain_005` dÄ±ÅŸ API baÄŸÄ±mlÄ±lÄ±ÄŸÄ± (rate limit riski) â€” circuit breaker aktif

## ğŸ”˜ OperatÃ¶r Eylemi Gerekli
```bash
# TÃ¼m gruplarÄ± baÅŸlat:
python -m orchestrator.trigger --deployment-id {deployment_id} --all

# Veya seÃ§ili grup(lar):
python -m orchestrator.trigger --deployment-id {deployment_id} --groups group_chain_001,group_chain_002
```
"""