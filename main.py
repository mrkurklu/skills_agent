import dotenv
import os
# DİKKAT: Diğer importlardan ÖNCE yüklemeliyiz
dotenv.load_dotenv() 

from agent import SkillsAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli():
    console.print(Panel("[bold green]Skills Agent CLI v1.0[/bold green]\n[dim]Model bağımsız kodlama asistanı hazır.[/dim]"))
    
    # Burada modeli istediğin gibi değiştir: "ollama/llama3", "gemini/gemini-1.5-pro" vb.
    agent = SkillsAgent(model="gemini/gemini-2.5-flash") 
    
    while True:
        try:
            query = console.input("[bold cyan]>>> [/bold cyan]")
            if query.lower() in ["exit", "quit"]: break

            with console.status("[bold yellow]Agent çalışıyor...[/bold yellow]"):
                response = agent.execute(query)
            
            console.print(f"\n[bold blue]Agent:[/bold blue]\n{response}\n")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_cli()