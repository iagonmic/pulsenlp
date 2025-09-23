# Definição de perfis de usuários (otimista, crítico, neutro, etc.)
from random import randint, choice, sample

NAMES = ["Ana", "Carlos", "João", "Mariana", "Lucas", "Fernanda", "Rafael", "Bianca", "Paulo", "Isabela"]
STYLES = ["emoji", "formal", "casual", "gírias", "detalhado"]
TONES = ["optimistic", "pessimistic", "neutral", "sarcastic", "analytical"]

class UserProfile:
    def __init__(self, name:str, style:str, tone:str):
        self.name = name
        self.style = style
        self.tone = tone
        
    @classmethod
    def generate_random(cls):
        """Gera um perfil de usuário com atributos aleatórios."""
        return cls(
            name=choice(NAMES),
            style=choice(STYLES),
            tone=choice(TONES),
        )
    
    def __repr__(self):
        return f"UserProfile(name={self.name}, style={self.style}, tone={self.tone}"