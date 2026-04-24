import json
import re
from typing import List, Dict, Any
from litellm import completion
from core.base import BaseSkill

class SkillAgent:
    def __init__(self, skills: List[BaseSkill], model_name: str = "gpt-4o-mini"):
        """
        model_name örnekleri: 
        - "gpt-4o-mini" (OpenAI)
        - "claude-3-haiku-20240307" (Anthropic)
        - "gemini/gemini-1.5-flash" (Google)
        """
        self.skills = {skill.name: skill for skill in skills}
        self.model_name = model_name

    def _get_system_prompt(self) -> str:
        # LLM'e yeteneklerimizi (Tools) tanıtıyoruz
        tools_info =[]
        for name, skill in self.skills.items():
            schema = skill.get_tool_schema()["function"]
            tools_info.append(json.dumps(schema, ensure_ascii=False, indent=2))

        tools_str = "\n".join(tools_info)

        return f"""Sen usta bir otomasyon planlayıcısısın (n8n uzmanı gibi).
Kullanıcının isteğini yerine getirmek için aşağıdaki araçları (yetenekleri) kullanarak bir iş akışı (workflow) tasarlamalısın.

MEVCUT ARAÇLAR (TOOLS):
{tools_str}

KURALLAR:
1. Sadece sana verilen araçları kullan.
2. Birden fazla adım gerekiyorsa, bir adımın çıktısını sonraki adımda kullanabilirsin. Bunun için {{step_id.result}} formatını kullan. 
   Örnek: Birinci adımın id'si "step_1" ise ve dosya okuduysa, ikinci adımda metin içinde "{{step_1.result}}" diyerek o veriyi enjekte edebilirsin.
3. Çıktın KESİNLİKLE VE SADECE aşağıdaki formatta BİR JSON dizisi (array) olmalıdır. Başka hiçbir açıklama yazma.

ÖRNEK ÇIKTI FORMATI:[
  {{
    "step_id": "adim_1",
    "skill_name": "run_command",
    "inputs": {{"command": "dir"}}
  }},
  {{
    "step_id": "adim_2",
    "skill_name": "run_command",
    "inputs": {{"command": "echo {{adim_1.result}} > liste.txt"}}
  }}
]
"""

    def plan_workflow(self, user_prompt: str) -> List[Dict[str, Any]]:
        print(f"🤖 Ajan Düşünüyor... (Model: {self.model_name})")
        
        messages =[
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_prompt}
        ]

        # LLM'e İsteği Gönder (LiteLLM sayesinde her modelle çalışır)
        response = completion(
            model=self.model_name,
            messages=messages,
            temperature=0.1 # Daha mantıksal sonuçlar için düşük tutuyoruz
        )

        raw_content = response.choices[0].message.content.strip()

        # Markdown ```json ... ``` kısımlarını temizleyelim
        clean_content = re.sub(r"```json|```", "", raw_content).strip()

        try:
            workflow_plan = json.loads(clean_content)
            return workflow_plan
        except json.JSONDecodeError:
            print("❌ Ajan geçersiz bir JSON üretti!")
            print("Raw Çıktı:", raw_content)
            return[]