# Services Paketi - ucuncu parti API ve dis servis entegrasyonlari
#
# ALTYAPI-SKILL-YAPISI-01 Faz D: `skills/common/ninerouter.py` buraya tasindi.
# Kural: yapilacak is mantigi degil, SADECE dis servise cagri burada durur.

from skills.services.ninerouter import (
    ninerouter_chat,
    ninerouter_chat_anthropic,
    ninerouter_discover_models,
    ninerouter_embeddings,
    ninerouter_image_gen,
    ninerouter_setup,
    ninerouter_stt,
    ninerouter_tts,
    ninerouter_video_gen,
    ninerouter_video_poll,
    ninerouter_web_fetch,
    ninerouter_web_search,
)

__all__ = [
    "ninerouter_setup",
    "ninerouter_chat",
    "ninerouter_chat_anthropic",
    "ninerouter_image_gen",
    "ninerouter_video_gen",
    "ninerouter_video_poll",
    "ninerouter_tts",
    "ninerouter_stt",
    "ninerouter_embeddings",
    "ninerouter_web_search",
    "ninerouter_web_fetch",
    "ninerouter_discover_models",
]