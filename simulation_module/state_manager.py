# salva o estado atual das conversas e perfis em disco
import json
from user_profiles import UserProfile
from thought_generator import UserAgent

STATE_FILE = "simulation_state.json"

def save_state(agents: list):
    """Salva perfis, modelo atual e memória em disco."""
    state = []
    for agent in agents:
        state.append({
            "profile": {
                "name": agent.user_profile.name,
                "style": agent.user_profile.style,
                "tone": agent.user_profile.tone,
            },
            "current_model": agent.current,
            "memory": agent.memory.to_dict() if hasattr(agent.memory, "to_dict") else {}
        })

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state():
    """Carrega perfis, modelo atual e memória em disco."""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        agents = []
        for agent_data in state:
            profile = UserProfile(
                name=agent_data["profile"]["name"],
                style=agent_data["profile"]["style"],
                tone=agent_data["profile"]["tone"],
            )
            agent = UserAgent(profile)
            agent.current = agent_data["current_model"]

            # Reconstruindo memória manualmente
            if agent_data.get("memory"):
                mem_dict = agent_data["memory"]
                if "messages" in mem_dict:
                    for msg in mem_dict["messages"]:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        agent.memory.add(role=role, content=content)

            agents.append(agent)

        return agents

    except FileNotFoundError:
        return []
