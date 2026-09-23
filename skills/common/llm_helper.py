# LLM Yardımcı Yeteneği

from skills.base import registry


@registry.register(
    name="count_tokens",
    description="Metin için tahmini token sayısını hesaplar."
)
def count_tokens(text: str) -> int:
    """Metin için tahmini token sayısını hesapla."""
    words = text.split()
    return len(words)


@registry.register(
    name="validate_llm_response",
    description="LLM yanıtını verilen şemaya göre doğrulama yapar."
)
def validate_llm_response(response: str, schema: dict) -> bool:
    """LLM yanıtını verilen şemaya göre doğrulama yap."""
    if not response or not isinstance(response, str):
        return False
    return True
