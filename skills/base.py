# Ortak Temel Sınıf — Tüm yeteneklerin temel yapısı

import inspect
from typing import Callable, Dict, Any, List


class SkillRegistry:
    """Tüm ajan yeteneklerini merkezi olarak kaydeden ve yöneten sınıf."""

    def __init__(self):
        self._skills: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str):
        """Fonksiyonları ajan yeteneği olarak kaydeden decorator."""
        def decorator(func: Callable):
            sig = inspect.signature(func)
            parameters = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                param_type = "string"
                if param.annotation == int:
                    param_type = "number"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

                parameters[param_name] = {
                    "type": param_type,
                    "description": f"{param_name} parametresi."
                }

            self._skills[name] = {
                "name": name,
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": parameters,
                    "required": [
                        p for p, param in sig.parameters.items()
                        if param.default == inspect.Parameter.empty and p != "self"
                    ]
                },
                "func": func
            }
            return func
        return decorator

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """LLM'e gönderilecek tool şemalarını döner."""
        return [
            {k: v for k, v in skill.items() if k != "func"}
            for skill in self._skills.values()
        ]

    def execute_skill(self, name: str, **kwargs) -> Any:
        """İsmi verilen skill'i argümanlarıyla tetikler."""
        if name not in self._skills:
            raise ValueError(f"Skill '{name}' bulunamadı!")
        return self._skills[name]["func"](**kwargs)


# Global registry örneği
registry = SkillRegistry()