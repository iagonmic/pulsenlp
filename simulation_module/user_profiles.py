from random import randint, choice, sample
# Definição de perfis de usuários (otimista, crítico, neutro, etc.)

NAMES = ["Ana", "Carlos", "João", "Mariana", "Lucas", "Fernanda", "Rafael", "Bianca", "Paulo", "Isabela"]
STYLES = ["emoji", "formal", "casual", "gírias", "detalhado"]
TONES = ["optimistic", "pessimistic", "neutral", "sarcastic", "analytical"]
TOPICS = ["política", "esportes", "tecnologia", "música", "filmes", "economia", "viagens"]

class UserProfile:
    def __init__(self, name:str, style:str, tone:str, topics:list):
        self.name = name
        self.style = style
        self.tone = tone
        self.topics = topics
        
    @classmethod
    def generate_random(cls):
        """Gera um perfil de usuário com atributos aleatórios."""
        return cls(
            name=choice(NAMES),
            style=choice(STYLES),
            tone=choice(TONES),
            topics=sample(TOPICS, k=randint(1, len(TOPICS)))
        )
    
    def __repr__(self):
        return f"UserProfile(name={self.name}, style={self.style}, tone={self.tone}, topics={self.topics})"