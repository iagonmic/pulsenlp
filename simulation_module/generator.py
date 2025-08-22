import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.groq.groq import Groq  # <- provedor Groq no Agno
from user_profiles import UserProfile

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class UserAgent(Agent):
    def __init__(self, user_profile: UserProfile, models: list, **kwargs):
        self.user_profile = user_profile
        self.models = models
        self.current = 0

        super().__init__(
            role=f"Usuário {user_profile.name} ({user_profile.style}, {user_profile.tone}) comentando sobre {', '.join(user_profile.topics)}",
            instructions="Você é um usuário com um perfil específico." \
            "Gere pensamentos baseados em um dos tópicos de interesse, mantendo congruência com o estilo e tom que lhe foram dados.",
            model=Groq(id=self.models[self.current], api_key=GROQ_API_KEY),
            memory=Memory(),
            **kwargs
        )

    def _switch_model(self):
        """Troca para o próximo modelo da lista."""
        self.current = (self.current + 1) % len(self.models)
        print(f"[INFO] Trocando para modelo: {self.models[self.current]}")
        self.model = Groq(id=self.models[self.current], api_key=GROQ_API_KEY)

    def generate_thought(self) -> str:
        """Gera um pensamento do usuário, trocando de modelo se falhar."""
        try:
            response = self.run("Diga uma opinião curta sobre um dos tópicos que você entende.")
            return str(response.content)
        except Exception as e:
            print(f"[ERRO] {e} -> tentando próximo modelo...")
            self._switch_model()
            return self.generate_thought()


# ====================== TESTE ======================
if __name__ == "__main__":
    modelos_disponiveis = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
        "deepseek-r1-distill-llama-70b",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-guard-4-12b",
        "meta-llama/llama-prompt-guard-2-22m",
        "meta-llama/llama-prompt-guard-2-86m"
    ]

    user = UserProfile.generate_random()
    print(f"[Perfil gerado] {user}")

    agent = UserAgent(user, modelos_disponiveis)

    for _ in range(3):
        print(f"{user.name} disse: {agent.generate_thought()}")
