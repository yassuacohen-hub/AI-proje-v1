"""Orchestrator package for Huginn Data Insights external agent workflow.

Bu paket, görev panosu, tetikleme, dosya kilit yönetimi ve yeni ORCH‑09
nöbetçi mekanizmasını içerir.

Alt modüller otomatik olarak dışarıya aktarılıyor, böylece
`from src.company_master.orchestrator import nobetci` gibi importlar
çalışır.
"""

# Alt paketleri dışarıya aktar (kısayol olarak kullanılabilsin)
# Dairesel bağımlılıkları önlemek için `nobetci` burada
# import edilmez; doğrudan `src.company_master.orchestrator.nobetci`
# üzerinden kullanılabilir.
from . import task_board, trigger  # noqa: F401

