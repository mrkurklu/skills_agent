import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from core.base import BaseSkill

class ApiRequestInput(BaseModel):
    url: str = Field(..., description="İstek atılacak tam URL adresi. Örn: https://api.exchangerate-api.com/v4/latest/USD")
    method: str = Field(default="GET", description="HTTP metodu: 'GET', 'POST', 'PUT' vb.")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Gerekliyse HTTP başlıkları (Headers).")
    body: Optional[Dict[str, Any]] = Field(default=None, description="POST/PUT istekleri için gönderilecek JSON verisi.")

class ApiRequestSkill(BaseSkill):
    name = "api_request"
    description = "Herhangi bir web API'sine HTTP isteği (REST) atarak dış dünyadan güncel veri (JSON veya metin) çeker."
    args_schema = ApiRequestInput

    def execute(self, url: str, method: str = "GET", headers: dict = None, body: dict = None) -> Any:
        print(f"   🌐 Web İsteği Atılıyor: [{method}] {url}")
        
        response = requests.request(
            method=method, 
            url=url, 
            headers=headers, 
            json=body,
            timeout=15 # Sonsuza kadar beklemesini engellemek için
        )
        
        # Eğer HTTP hatası varsa fırlat (Örn: 404, 500)
        response.raise_for_status()
        
        # Gelen yanıt JSON ise otomatik Python sözlüğüne (dict) çevir, değilse düz metin dön
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text