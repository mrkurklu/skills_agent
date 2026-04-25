from core.database import init_db, add_skill

init_db()

# DÜNYACA KABUL EDİLEN STANDART FORMAT:
name = "read_file"
description = "Sistemden bir dosyanın içeriğini okur."
parameters = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string", "description": "Okunacak dosyanın yolu."}
    },
    "required": ["file_path"]
}

# Python kodu metin (string) olarak saklanıyor!
code = """
import os
from pydantic import BaseModel, Field
from core.base import BaseSkill

class ReadFileInput(BaseModel):
    file_path: str = Field(...)

class ReadFileSkill(BaseSkill):
    name = "read_file"
    description = "Sistemden bir dosyanın içeriğini okur."
    args_schema = ReadFileInput

    def execute(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError("Dosya bulunamadi.")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
"""

add_skill(name, description, parameters, code)
print("✅ Standart formattaki yetenek Veritabanına eklendi!")