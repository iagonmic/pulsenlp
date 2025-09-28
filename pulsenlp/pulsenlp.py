import reflex as rx
from rxconfig import config
from collections import defaultdict
import json
from pulsenlp.simulation_module.async_runner import main
from asyncio import create_task, sleep
import os

DATA_PATH = "pulsenlp/data.json"


class AppState(rx.State):
    simulation_started: bool = False
    topico: str = ""
    num_users: int = 3
    agent_data: dict = {}
    agent_avg: dict = {}
    _last_modified: float = 0

    # ===========================
    # Funções de manipulação de dados
    # ===========================
    def load_json(self, data_path=DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def prepare_agent_data(self, json_data):
        agents = defaultdict(list)
        for entry in json_data:
            agents[entry["nome"]].append({
                "index": len(agents[entry["nome"]]) + 1,
                "sentiment": entry["rating"],
                "texto": entry["texto"],
                "style": entry["style"],
                "tone": entry["tone"],
                "topic": entry["topic"],
            })
        return agents

    def agent_graph(self, data: list[dict]) -> rx.Component:
        return rx.recharts.line_chart(
            rx.recharts.line(
                data_key="sentiment",
                stroke="#3b82f6",
                dot=True,
                is_animation_active=True,
            ),
            rx.recharts.reference_line(
                y=0,
                stroke="gray",
                stroke_dasharray="5 5",
            ),
            rx.recharts.x_axis(data_key="index"),
            rx.recharts.y_axis(domain=[-1, 1]),
            rx.recharts.tooltip(),
            data=data,
            width="100%",
            height=250,
        )

    def agent_card(self, nome: str, data: list[dict]) -> rx.Component:
        last = data[-1]  # último comentário para exibir metadados
        return rx.card(
            rx.vstack(
                rx.text(f"Agente: {nome}", size="6", weight="bold"),
                rx.text(f"Estilo: {last['style']}"),
                rx.text(f"Tom: {last['tone']}"),
                rx.spacer(),
                self.agent_graph(data),
            ),
            padding="20px",
            margin="10px",
            width="100%",
        )

    def sentimental_analysis_view(self) -> rx.Component:
        agents = self.prepare_agent_data(self.agent_data)

        return rx.grid(
            rx.foreach(
                list(agents.items()),
                lambda item: self.agent_card(item[0], item[1]),
            ),
            columns="3",
            spacing="6",
            width="100%",
            padding="20px"
        )

    # ===========================
    # Funções de controle do estado
    # ===========================
    def _save_state(self):
        """Salva topico e num_users em um arquivo JSON."""
        data = {
            "topico": self.topico,
            "num_users": self.num_users
        }
        with open("pulsenlp/topico.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)

    @rx.event
    def set_topico(self, topico):
        self.topico = topico
    
    @rx.event
    def set_num_users(self, num_users):
        if num_users.isdigit():
            num_users = int(num_users)
        self.num_users = num_users

    @rx.event
    def set_agent_data(self, agent_data):
        self.agent_data = agent_data

        # Calcula a média de cada agente
        avg_dict = {}
        for nome, data in agent_data.items():
            if data:
                avg_dict[nome] = sum(d["sentiment"] for d in data) / len(data)
            else:
                avg_dict[nome] = 0
        self.agent_avg = avg_dict

    async def watch_data_file(self):
        """Monitora DATA_PATH e atualiza agent_data quando o arquivo mudar."""
        while True:
            if os.path.exists(DATA_PATH):
                modified = os.path.getmtime(DATA_PATH)
                if modified != self._last_modified:
                    self._last_modified = modified
                    data = self.load_json(DATA_PATH)
                    self.set_agent_data(data)
                    print("Agent data atualizado!")
            await sleep(1)

    @rx.event
    def start_simulation(self):
        self.simulation_started = True
        self._save_state()
        create_task(main())
        create_task(self.watch_data_file())
        print(f"Simulação iniciada com tópico: {self.topico} e {self.num_users} agentes.")

    @rx.event
    def stop_simulation(self):
        self.simulation_started = False
        print("Simulação parada.")


# ===========================
# Função de renderização da página
# ===========================
def index() -> rx.Component:
    # Reflex passa o estado automaticamente para eventos e métodos
    state = AppState

    return rx.vstack(
        # Card inicial (centralizado horizontalmente)
        rx.center(
            rx.card(
                rx.vstack(
                    rx.heading(
                        "Bem-vindo ao PulseNLP!",
                        align="center",
                        size="7",
                        color="blue.600"
                    ),
                    rx.text(
                        "Digite os valores abaixo para iniciar a simulação:",
                        align="center",
                        size="4",
                        color="gray.600"
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Tópico da conversa",
                            width="100%",
                            on_change=AppState.set_topico,
                            required=True
                        ),
                        rx.input(
                            placeholder="Quantidade de agentes",
                            width="100%",
                            on_change=AppState.set_num_users
                        ),
                        spacing="4",
                        align="center",
                        justify="center"
                    ),
                    rx.button(
                        "Iniciar",
                        color_scheme="blue",
                        width="100%",
                        on_click=AppState.start_simulation
                    ),
                    spacing="5",
                    align="center",
                    width="100%",
                ),
                padding="35px",
                width="100%",
                max_width="500px",
                border_radius="2xl",
                shadow="lg",
                border="1px solid #e2e8f0",
            ),
            width="100%",
            padding="20px",
        ),

        # Grid com os agentes
        AppState.sentimental_analysis_view(AppState),
        spacing="4",
        width="100%",
        padding="20px",
    )


# ===========================
# Inicialização do app Reflex
# ===========================
app = rx.App()
app.add_page(index)
