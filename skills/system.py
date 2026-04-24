import os
import subprocess
from pydantic import BaseModel, Field
from core.base import BaseSkill

# --- 1. DOSYA OKUMA YETENEĞİ ---

class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Okunacak dosyanın tam veya göreceli yolu.")

class ReadFileSkill(BaseSkill):
    name = "read_file"
    description = "Sistemden bir dosyanın içeriğini okur. Kod veya metin analizleri için kullanılır."
    args_schema = ReadFileInput

    def execute(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


# --- 2. KOMUT ÇALIŞTIRMA YETENEĞİ ---

class RunCommandInput(BaseModel):
    command: str = Field(..., description="Terminalde/Shell'de çalıştırılacak bash komutu.")

class RunCommandSkill(BaseSkill):
    name = "run_command"
    description = "Sistem terminalinde bir bash komutu çalıştırır ve çıktısını döndürür. Örn: ls, dir, npm install vb."
    args_schema = RunCommandInput

    def execute(self, command: str) -> str:
        # errors="replace" parametresi Windows'taki encoding (TR karakter vs.) çökmelerini engeller.
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            errors="replace" 
        )
        
        if result.returncode != 0:
            return f"Hata ({result.returncode}):\n{result.stderr}"
            
        # Eğer stdout None dönerse (olası bir çökme durumunda), hata vermemesi için boş string dön
        if result.stdout is None:
            return ""
            
        return result.stdout