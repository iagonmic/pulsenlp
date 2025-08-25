import os
import json
import random
import asyncio
from simulation_module.thought_generator import UserAgent
from simulation_module.user_profiles import UserProfile
from simulation_module.state_manager import save_state, load_state

from nlp_module.sentiment import sentiment_analysis

### TESTE
# Análise de sentimentos

### TESTE

DATA_PATH = os.path.join("dashboard_module", "data.json")
TOPICO_CONFIG_PATH = os.path.join("dashboard_module", "topico.json")

def append_comment_to_json(agent_name: str, agent_style: str, agent_tone: str, text: str, topic: str):
    """Adiciona um comentário ao arquivo JSON com análise de sentimento."""
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        # Calcula o rating usando NLP
        rating = sentiment_analysis(text)

        new_entry = {
            "nome": agent_name,
            "style": agent_style,
            "tone": agent_tone,
            "texto": text,
            "rating": rating,
            "topic": topic,
            "round": len(data) + 1
        }
        data.append(new_entry)

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[ERRO] Falha ao salvar comentário no JSON: {e}")


async def simulate_user(agent: UserAgent, topico: str, delay_range=(5, 20)):
    """Loop assíncrono: gera pensamentos em tempo real para um usuário."""
    while True:
        await asyncio.sleep(random.uniform(*delay_range))  # espera aleatória
        thought = agent.generate_thought(topico)
        print(f"[{agent.user_profile.name}] 💬 {thought}")

        # Salvar no JSON com rating de sentimento
        append_comment_to_json(agent.user_profile.name, agent.user_profile.style, agent.user_profile.tone, thought, topico)


def load_topic():
    if os.path.exists(TOPICO_CONFIG_PATH):
        with open(TOPICO_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"topico": "Discussão livre", "num_agentes": 3}


async def main(num_users=3, resume=False):
    print("async_runner aguardando tópico...")
    last_topico = None

    while True:
        # Se não existir ainda, espera
        if not os.path.exists("dashboard_module/topico.json"):
            await asyncio.sleep(1)
            continue

        try:
            with open("dashboard_module/topico.json", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            print("Erro lendo topico.json:", e)
            await asyncio.sleep(1)
            continue

        topico = dados.get("topico")
        num_agentes = dados.get("num_agentes", 1)

        # Se não tem tópico ainda
        if not topico or topico.strip() == "":
            await asyncio.sleep(1)
            continue

        # Detecta mudança de tópico
        if topico != last_topico:
            print(f"Novo tópico detectado: {topico} com {num_agentes} agentes")
            last_topico = topico
            break

    config = load_topic()
    topico = config["topico"]
    num_users = config["num_agentes"]

    print(f"[INFO] Iniciando conversa sobre: {topico} ({num_users} agentes)")

    if resume:
        agents = load_state()
        if not agents:
            users = [UserProfile.generate_random() for _ in range(num_users)]
            agents = [UserAgent(users) for user in users]
    else:
        users = [UserProfile.generate_random() for _ in range(num_users)]
        agents = [UserAgent(user) for user in users]

    for agent in agents:
        print(agent.user_profile)

    tasks = [asyncio.create_task(simulate_user(agent, topico)) for agent in agents]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("[INFO] Tasks canceladas.")
        save_state(agents)

if __name__ == "__main__":
    try:
        asyncio.run(main(num_users=5, resume=True))
    except KeyboardInterrupt:
        print("\n[INFO] Simulação encerrada pelo usuário.")
