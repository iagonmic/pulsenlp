import reflex as rx
from rxconfig import config


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.text(
                    "Defina o tópico e número de agentes",
                    align="center",
                    size="5"
                ),
                rx.hstack(
                    rx.input(placeholder="Tópico", width="200px"),
                    rx.input(placeholder="Número de agentes", width="200px"),
                    spacing="4",
                    align="center",
                    justify="center"
                ),
                rx.button("Iniciar", color_scheme="blue", width="100%"),
                spacing="5",
                align="center",
                width="100%",  # garante que o vstack ocupe toda largura do card
            ),
            size="3",
            padding="20px",
        ),
        padding="40px",
    )



app = rx.App()
app.add_page(index)
