import inspect
from abc import ABC, abstractmethod
from typing import Type, Any, Dict
from pydantic import BaseModel

class BaseSkill(ABC):
    """
    Tüm yeteneklerin (skills) türeyeceği ana sınıf.
    Hem LLM function calling (JSON) şeması üretir, hem de parametreleri doğrular.
    """
    name: str = "base_skill"
    description: str = "Yetenek açıklaması."
    
    # Pydantic ile parametre şeması (Zorunlu)
    args_schema: Type[BaseModel]

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Asıl işlemin yapıldığı metod. Alt sınıflar bunu ezmeli (override etmeli)."""
        pass

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Dışarıdan (LLM veya n8n Node'u tarafından) çağrılan güvenli metod.
        Parametreleri Pydantic ile doğrular, hatasız çalışmayı garanti eder.
        """
        try:
            # Gelen argümanları şemaya göre doğrula
            validated_args = self.args_schema(**kwargs)
            # Yeteneği çalıştır
            result = self.execute(**validated_args.model_dump())
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_tool_schema(self) -> dict:
        """
        LLM'ler (OpenAI, Claude, Gemini vb.) için ortak Tool Calling / Function Calling şeması üretir.
        """
        schema = self.args_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema
            }
        }