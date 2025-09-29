import reflex as rx
from rxconfig import config
from collections import defaultdict
import json
from pulsenlp.simulation_module.async_runner import main
import asyncio

DATA_PATH = "pulsenlp/data.json"


class AppState(rx.State):
    simulation_started: bool = False
    topico: str = ""
    num_users: int = 3
    agents: dict = {}

    def _save_state(self):
        """Salva topico e num_users em um arquivo JSON."""
        data = {
            "topico": self.topico,
            "num_users": self.num_users
        }
        with open("pulsenlp/topico.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    @rx.event
    def recreate_cards(self):
        json_data = load_json(DATA_PATH)
        self.agents = prepare_agent_data(json_data)

    @rx.event
    def return_last_comment(self):
        pass

    @rx.event
    def set_topico(self, topico):
        self.topico = topico
    
    @rx.event
    def set_num_users(self, num_users):
        if num_users.isdigit():
            num_users = int(num_users)
        self.num_users = num_users

    @rx.event
    def start_simulation(self):
        self.simulation_started = True
        self._save_state()
        asyncio.create_task(main())
        print(f"Simulação iniciada com tópico: {self.topico} e {self.num_users} agentes.")

    @rx.event
    def stop_simulation(self):
        self.simulation_started = False
        print("Simulação parada.")

    @rx.event
    def set_agent_data(self, agent_data):
        self.agent_data = agent_data

        # Calcula a média de cada agente ao mesmo tempo
        avg_dict = {}
        for nome, data in agent_data.items():
            if data:
                avg_dict[nome] = sum(d["sentiment"] for d in data) / len(data)
            else:
                avg_dict[nome] = 0
        self.agent_avg = avg_dict

def load_json(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def prepare_agent_data(json_data):
    agents = defaultdict(list)
    for entry in json_data:
        agents[entry["nome"]].append({
            "index": len(agents[entry["nome"]]) + 1,  # só um contador
            "sentiment": entry["rating"]["score"],
            "texto": entry["texto"],
            "style": entry["style"],
            "tone": entry["tone"],
            "topic": entry["topic"],
        })
    return agents

def agent_graph(data: list[dict]) -> rx.Component:
    # calcula média do sentimento
    # avg_sentiment = sum(d["sentiment"] for d in data) / len(data) if data else 0

    return rx.recharts.line_chart(
        # Linha principal dos sentimentos
        rx.recharts.line(
            data_key="sentiment",
            stroke="#3b82f6",
            dot=True,
            is_animation_active=True,
        ),
        # Linha tracejada no zero
        rx.recharts.reference_line(
            y=0,
            stroke="gray",
            stroke_dasharray="5 5",
        ),
        
        # Linha de média
        #rx.recharts.reference_line(
        #    y=avg_sentiment,
        #    stroke="red",
        #    stroke_dasharray="3 3",
        #    label=f"Média ({avg_sentiment:.2f})",
        #),
        
        # Eixo X = índice (ordem dos comentários)
        rx.recharts.x_axis(data_key="index"),
        # Eixo Y fixo entre -1 e 1
        rx.recharts.y_axis(domain=[-1, 1]),
        # Tooltip para mostrar os valores
        rx.recharts.tooltip(),
        # Dados do agente
        data=data,
        width="100%",
        height=250,
    )

def agent_card(nome: str, data: list[dict]) -> rx.Component:
    last = data[-1]
    return rx.card(
        rx.vstack(
            rx.text(f"Agente: {nome}", size="6", weight="bold"),
            rx.text(f"Estilo: {last.get('style', '-')}" if last else "-"),
            rx.text(f"Tom: {last.get('tone', '-')}" if last else "-"),
            rx.spacer(),
            agent_graph(data),
        ),
        padding="20px",
        margin="10px",
        width="100%",
    )

def sentimental_analysis_view() -> rx.Component:
    return rx.grid(
        rx.foreach(
            AppState.agents,
            lambda nome, data: agent_card(nome, data)
        ),
        columns="3",
        spacing="6",
        width="100%",
        padding="20px"
    )


def index() -> rx.Component:
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
                border_radius="2xl",   # cantos bem arredondados
                shadow="lg",           # sombra suave
                border="1px solid #e2e8f0",  # borda leve (cinza claro)
            ),
            width="100%",
            padding="20px",
            
        ),

        # Grid com os agentes
        sentimental_analysis_view(),
        spacing="4",
        width="100%",
        padding="20px",
    )

app = rx.App()
app.add_page(index)
