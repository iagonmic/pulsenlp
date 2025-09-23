import reflex as rx
from rxconfig import config


class AppState(rx.State):
    simulation_started: bool = False
    topico: str = ""
    num_users: int = 3

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
        print(f"Simulação iniciada com tópico: {self.topico} e {self.num_users} agentes.")

    @rx.event
    def stop_simulation(self):
        self.simulation_started = False
        print("Simulação parada.")


def index() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.text(
                    "Bem-vindo ao PulseNLP!",
                    align="center",
                    size="5",
                ),
                rx.text(
                    "Digite os valores abaixo para iniciar a simulação:",
                    align="center",
                    size="2"
                ),
                rx.hstack(
                    rx.input(placeholder="Tópico da conversa", width="200px", on_change=AppState.set_topico, required=True),
                    rx.input(placeholder="Quantidade de agentes", width="200px", on_change=AppState.set_num_users),
                    spacing="4",
                    align="center",
                    justify="center"
                ),
                rx.button("Iniciar", color_scheme="blue", width="100%", on_click=AppState.start_simulation),
                spacing="5",
                align="center",
                width="100%",  # garante que o vstack ocupe toda largura do card
                ),
            size="3",
            padding="20px",    
            ),
        padding="40px"
        )


app = rx.App()
app.add_page(index)
