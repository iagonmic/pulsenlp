# Loop assíncrono para simular comentários em tempo real
import asyncio
import random
from thought_generator import UserAgent
from user_profiles import UserProfile
from state_manager import save_state, load_state

async def simulate_user(agent: UserAgent, delay_range=(5, 20)):
    """Loop assíncrono: gera pensamentos em tempo real para um usuário."""
    while True:
        await asyncio.sleep(random.uniform(*delay_range))  # espera aleatória
        thought = agent.generate_thought()
        print(f"[{agent.user_profile.name}] 💬 {thought}")


async def main(num_users=3, resume=False):
    if resume:
        agents = load_state()
        print(f"[INFO] Estado carregado com {len(agents)} usuários.")
        if not agents:
            print("[INFO] Nenhum estado salvo, criando novos usuários...")
            users = [UserProfile.generate_random() for _ in range(num_users)]
            agents = [UserAgent(user) for user in users]
    else:
        users = [UserProfile.generate_random() for _ in range(num_users)]
        agents = [UserAgent(user) for user in users]

    # Mostra os perfis
    for agent in agents:
        print(agent.user_profile)

    # Roda os loops
    tasks = [asyncio.create_task(simulate_user(agent)) for agent in agents]

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
