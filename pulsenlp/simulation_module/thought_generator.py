import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.memory.manager import UserMemory
from agno.models.groq.groq import Groq  # <- provedor Groq no Agno
from pulsenlp.simulation_module.user_profiles import UserProfile

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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

class UserAgent(Agent):
    def __init__(self, user_profile: UserProfile, **kwargs):
        self.user_profile = user_profile
        self.models = modelos_disponiveis
        self.current = 0

        super().__init__(
            role=f"Usuário {user_profile.name} ({user_profile.style}, {user_profile.tone}) comentando sobre um tópico fornecido",
            instructions="Você é um usuário com um perfil específico." \
            "Gere pensamentos baseados no tópico que foi fornecido, mantendo congruência com o estilo e tom que lhe foram dados.",
            model=Groq(id=self.models[self.current], api_key=GROQ_API_KEY),
            #memory=UserMemory(),
            **kwargs
        )

    def _switch_model(self):
        """Troca para o próximo modelo da lista."""
        self.current = (self.current + 1) % len(self.models)
        print(f"[INFO] Trocando para modelo: {self.models[self.current]}")
        self.model = Groq(id=self.models[self.current], api_key=GROQ_API_KEY)

    def generate_thought(self, topico) -> str:
        """Gera um pensamento do usuário, trocando de modelo se falhar."""
        try:
            response = self.run(f"Diga uma opinião curta sobre o seguinte tópico: {topico}")
            return str(response.content)
        except Exception as e:
            print(f"[ERRO] {e} -> tentando próximo modelo...")
            self._switch_model()
            return self.generate_thought(topico)


# ====================== TESTE ======================
if __name__ == "__main__":

    user = UserProfile.generate_random()
    print(f"[Perfil gerado] {user}")

    agent = UserAgent(user)

    for _ in range(3):
        print(f"{user.name} disse: {agent.generate_thought()}")
