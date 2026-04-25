from pydantic import BaseModel, Field
from core.base import BaseSkill

class PirateTranslatorInput(BaseModel):
    text: str = Field(..., description="Çevrilecek metin.")

class PirateTranslatorSkill(BaseSkill):
    name = "pirate_translator"
    description = "Metni korsan (pirate) ağzına çevirir."
    args_schema = PirateTranslatorInput

    def execute(self, text: str) -> str:
        korsan_sozlugu = {
            "merhaba": "Yarrr!",
            "dostum": "miço",
            "nasılsın": "denizler nasıl",
            "benim adım": "bana derler ki",
            "çok": "kocaman",
            "skillflow": "Kaptan SkillFlow"
        }
        
        yeni_metin = text.lower()
        for kelime, korsanca in korsan_sozlugu.items():
            yeni_metin = yeni_metin.replace(kelime, korsanca)
            
        return yeni_metin.upper() + " AHOY!"