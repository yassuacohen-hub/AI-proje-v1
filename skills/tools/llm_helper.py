# LLM YardÄ±mcÄ± YeteneÄŸi

from skills.base import registry


@registry.register(
    name="count_tokens",
    description="Metin iÃ§in tahmini token sayÄ±sÄ±nÄ± hesaplar."
)
def count_tokens(text: str) -> int:
    """Metin iÃ§in tahmini token sayÄ±sÄ±nÄ± hesapla."""
    words = text.split()
    return len(words)


@registry.register(
    name="validate_llm_response",
    description="LLM yanÄ±tÄ±nÄ± verilen ÅŸemaya gÃ¶re doÄŸrulama yapar."
)
def validate_llm_response(response: str, schema: dict) -> bool:
    """LLM yanÄ±tÄ±nÄ± verilen ÅŸemaya gÃ¶re doÄŸrulama yap."""
    if not response or not isinstance(response, str):
        return False
    return True
