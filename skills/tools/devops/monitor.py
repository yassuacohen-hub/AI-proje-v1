# Monitor DevOps YeteneÄŸi

from skills.base import registry


@registry.register(
    name="analyze_oom_killer",
    description="OOM-killer loglarini analiz eder ve bellek kullanimini raporlar."
)
def analyze_oom_killer(dmesg_log: str) -> str:
    if "Out of memory" in dmesg_log or "oom-kill" in dmesg_log:
        return "\u26a0\ufe0f OOM-killer tespit edildi: Container bellek limitini artir veya application memory tuning yap."
    return "OOM-killer sorunu tespit edilmedi."


@registry.register(
    name="check_resource_usage",
    description="RAM/CPU kullanim oranlarini kontrol eder."
)
def check_resource_usage(metrics: dict) -> str:
    cpu = metrics.get("cpu_percent", 0)
    mem = metrics.get("memory_percent", 0)
    if cpu > 90:
        return "\u26a0\ufe0f CPU kullanimi yuksek: %{cpu}"
    if mem > 90:
        return "\u26a0\ufe0f RAM kullanimi yuksek: %{mem}"
    return "Kaynaklar normal: CPU %{cpu}, RAM %{mem}"
