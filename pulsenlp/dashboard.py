import os
import matplotlib
matplotlib.use('Agg') # evitar problemas de threading com o Dash
import dash
from dash import dcc, html
import dash_mantine_components as dmc
import pandas as pd
import json
from typing import List
from pulsenlp.charts import gerar_grafico_linha, gerar_grafico_barra
from pulsenlp.wordcloud_gen import gerar_nuvem_palavras_base64
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def ler_contador_json():
    if os.path.exists("pulsenlp/data.json"):
        return os.path.getmtime("pulsenlp/data.json")  
    return 0

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        if event.src_path.endswith("data.json"):
            self.app.gatilho["atualizar"] += 1
            print(f"⚡ data.json atualizado - gatilho agora {self.app.gatilho['atualizar']}")


def iniciar_observador(app, path="pulsenlp/data.json"):
    event_handler = FileChangeHandler(app)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(path), recursive=False)
    observer.start()
    return observer


# Agora os filtros começam vazios
def criar_filtros(colunas: List[str], id_prefix: str):
    filtros = []
    for i, col in enumerate(colunas):
        filtro = dmc.Select(
            id=f"{id_prefix}-{i}",
            data=[],  # começa vazio, será preenchido dinamicamente
            placeholder=f"Selecione {col}",
            clearable=True,
            searchable=True,
            nothingFound="Sem opções",
            size="sm",
            radius="lg",  
            style={
                "marginTop": "10px",
                "marginBottom": "15px",
                "marginLeft": "10px",
                "marginRight": "10px",
                "borderRadius": "12px"  
            }
        )
        filtros.append(filtro)
    return filtros

def criar_dashboard(
    json_path: str,
    col_linha_x: str,
    col_linha_y: str,
    col_barra_x: str,
    col_barra_y: str,
    colunas_filtros_linha: List[str],
    colunas_filtro_barra: List[str],
    col_wordcloud: str,
):
    app = dash.Dash(__name__)

    # Função para ler o JSON
    def ler_json():
        if os.path.exists(json_path):
            with open(json_path, encoding="utf-8") as f:
                return json.load(f)
        return {"nome": ["Arnaldo"], "texto": ["arroba"], "style": ["Formal"], "tone": ["Amigável"], "rating": [0.0], "topic": ["esporte"], "round": [0]}

    # Carregar o arquivo JSON inicial
    data = ler_json()
    df = pd.DataFrame(data)

    print(df)

    # Último comentário
    ultimo = df.iloc[-1]
    nome = ultimo["nome"]
    texto = ultimo["texto"]

    # Gerar wordcloud em base64
    imagem_wordcloud = gerar_nuvem_palavras_base64(df, coluna=col_wordcloud)

    # Criar filtros (vazios no início)
    filtros_linha = criar_filtros(colunas_filtros_linha, id_prefix="filtro-linha")
    filtros_barra = criar_filtros(colunas_filtro_barra, id_prefix="filtro-barra")

    # Layout
    app.layout = dmc.MantineProvider(
        theme={"colorScheme": "dark"},
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dcc.Store(id="gatilho-update", data={"atualizar": 0}),
            dmc.Container(
                [
                    dmc.Card(
                        [
                            dmc.Text("Defina o tópico e número de agentes", weight=700, size="lg", mb=10),
                            dmc.Group(
                                [
                                    dmc.TextInput(
                                        label="Digite o tópico da conversa abaixo:",
                                        id="input-topico",
                                        placeholder="Digite aqui o tema para comentários...",
                                        style={"flex": 2},
                                    ),
                                    dmc.NumberInput(
                                        id="input-agentes",
                                        value=3,
                                        min=1,
                                        max=10,
                                        step=1,
                                        label="Quantas pessoas vai querer na conversa?",
                                        size="sm",
                                        style={"width": "120px"},
                                    ),
                                ],
                                grow=True,
                            ),
                            dmc.Button("Iniciar",id="botao-topico", color="blue", radius="md", fullWidth=True, style={"marginTop": "15px"}),
                        ],
                        withBorder=True,
                        shadow="md",
                        radius="lg",
                        p="md",
                        style={
                            "backgroundColor": "#1A1B1E",
                            "marginBottom": "20px",
                        },
                    ),
                    dmc.Grid(
                        [
                            # Coluna esquerda
                            dmc.Col(
                                html.Div(
                                    [
                                        dmc.Card(
                                            dmc.CardSection(
                                                [
                                                    html.Img(
                                                        id="imagem-wordcloud",
                                                        src=imagem_wordcloud,
                                                        style={
                                                            "width": "100%",
                                                            "maxHeight": "600px",
                                                            "objectFit": "contain",
                                                            "borderRadius": "12px",
                                                            "display": "block",
                                                            "margin": "0 auto",
                                                        },
                                                    ),
                                                ]
                                            ),
                                            withBorder=True,
                                            shadow="md",
                                            radius="lg",
                                            p="md",
                                            style={
                                                "backgroundColor": "#1A1B1E",
                                                "marginBottom": "20px",
                                                "height": "60%",
                                                "display": "flex",
                                                "flexDirection": "column",
                                            },
                                        ),
                                        dmc.Card(
                                            [
                                                dmc.Text("Último Comentário", weight=700, size="30px", mb=10),
                                                dmc.Text(id="nome-comentario", weight=700, size="30px", mb=8),
                                                dmc.Text(id="texto-comentario", weight=500, size="25px"),
                                            ],
                                            withBorder=True,
                                            shadow="md",
                                            radius="lg",
                                            p="md",
                                            style={
                                                "backgroundColor": "#1A1B1E",
                                                "flex": "1 1 30%",
                                                "display": "flex",
                                                "flexDirection": "column",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "flexDirection": "column", "height": "100vh"},
                                ),
                                span=6,
                                style={"display": "flex", "flexDirection": "column", "height": "100vh"},
                            ),
                            # Coluna direita: gráficos
                            dmc.Col(
                                [
                                    dmc.Card(
                                        children=[
                                            dmc.CardSection(id='filtros-linha', children=filtros_linha + [html.Div(style={"height": "15px"})]),
                                            dcc.Graph(
                                                id="grafico-linha",
                                                figure=gerar_grafico_linha(df, col_linha_x, col_linha_y),
                                                style={"flex": "1 1 auto"},
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="md",
                                        radius="lg",
                                        p="md",
                                        style={
                                            "backgroundColor": "#1A1B1E",
                                            "flex": "2 1 50%",
                                            "marginBottom": "20px",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "height": "100%",
                                        },
                                    ),
                                    dmc.Card(
                                        children=[
                                            dmc.CardSection(id='filtros-barra', children=filtros_barra + [html.Div(style={"height": "15px"})]),
                                            dcc.Graph(
                                                id="grafico-barra",
                                                figure=gerar_grafico_barra(df, col_barra_x, col_barra_y),
                                                style={"flex": "1 1 auto"},
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="md",
                                        radius="lg",
                                        p="md",
                                        style={
                                            "backgroundColor": "#1A1B1E",
                                            "flex": "2 1 50%",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "height": "100%",
                                        },
                                    ),
                                ],
                                span=6,
                                style={"display": "flex", "flexDirection": "column", "height": "100vh"},
                            ),
                        ],
                        gutter="xl",
                    ),
                ],
                fluid=True,
                style={"backgroundColor": "#121212", "minHeight": "100vh", "paddingTop": "25px", "paddingBottom": "25px"},
            ),
            # Intervalos
            dcc.Interval(id="intervalo-arquivo", interval=10000, n_intervals=0),
        ],
    )

    # ------------------------ CALLBACKS -----------------------------

    @app.callback(
        dash.Output("gatilho-update", "data"),
        dash.Input("intervalo-arquivo", "n_intervals")
    )
    def atualizar_gatilho(_):
        return ler_contador_json()

    @app.callback(
        dash.Output("input-topico", "value"),
        dash.Input("botao-topico", "n_clicks"),
        dash.State("input-topico", "value"),
        dash.State("input-agentes", "value"),
        prevent_initial_call=True
    )
    def definir_topico_e_agentes(n_clicks, topico, num_users):
        if not topico or topico.strip() == "":
            print("Tópico não pode ser vazio.")
            return topico
        try:
            num_users_int = int(num_users)
        except (ValueError, TypeError):
            print("Número de agentes inválido.")
            return topico

        dados_para_salvar = {
            "topico": topico,
            "num_users": num_users
        }

        try:
            with open("pulsenlp/topico.json", "w", encoding="utf-8") as f:
                json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)
            print(f"Dados salvos com sucesso: {dados_para_salvar}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")

        return topico
    
    # Atualizar gráfico de linha (com filtros funcionando)
    @app.callback(
        dash.Output("grafico-linha", "figure"),
        [dash.Input("gatilho-update", "data")] +
        [dash.Input(f"filtro-linha-{i}", "value") for i in range(len(colunas_filtros_linha))]
    )
    def update_grafico_linha(gatilho, *filtros):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtros_linha, filtros):
            if val:
                dff = dff[dff[col] == val]

        return gerar_grafico_linha(dff, col_linha_x, col_linha_y)

    # Atualizar gráfico de barra (com filtros funcionando)
    @app.callback(
        dash.Output("grafico-barra", "figure"),
        [dash.Input("gatilho-update", "data")] +
        [dash.Input(f"filtro-barra-{i}", "value") for i in range(len(colunas_filtro_barra))]
    )
    def update_grafico_barra(gatilho, *filtros):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtro_barra, filtros):
            if val:
                dff = dff[dff[col] == val]

        df_media = dff.groupby("nome", as_index=False)["rating"].mean()
        return gerar_grafico_barra(df_media, col_barra_x, col_barra_y)

    # Atualizar cards (wordcloud e último comentário)
    @app.callback(
        [dash.Output("imagem-wordcloud", "src"),
         dash.Output("nome-comentario", "children"),
         dash.Output("texto-comentario", "children")],
        [dash.Input("gatilho-update", "data")]
    )
    def update_cards(gatilho):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        ultimo = df_atualizado.iloc[-1]
        nome = ultimo["nome"]
        texto = ultimo["texto"]
        imagem_wordcloud = gerar_nuvem_palavras_base64(df_atualizado, coluna=col_wordcloud)
        return imagem_wordcloud, nome, texto

    # Atualizar opções dos filtros de linha dinamicamente
    for i, col in enumerate(colunas_filtros_linha):
        @app.callback(
            dash.Output(f"filtro-linha-{i}", "data"),
            dash.Input("gatilho-update", "data"),
            prevent_initial_call=False
        )
        def update_filtro_linha(gatilho, col=col):
            data = ler_json()
            df_atualizado = pd.DataFrame(data)
            valores_unicos = df_atualizado[col].dropna().unique()
            valores_unicos = sorted(valores_unicos)
            return [{"label": str(v), "value": str(v)} for v in valores_unicos]

    # Atualizar opções dos filtros de barra dinamicamente
    for i, col in enumerate(colunas_filtro_barra):
        @app.callback(
            dash.Output(f"filtro-barra-{i}", "data"),
            dash.Input("gatilho-update", "data"),
            prevent_initial_call=False
        )
        def update_filtro_barra(gatilho, col=col):
            data = ler_json()
            df_atualizado = pd.DataFrame(data)
            valores_unicos = df_atualizado[col].dropna().unique()
            valores_unicos = sorted(valores_unicos)
            return [{"label": str(v), "value": str(v)} for v in valores_unicos]

    return app

# ------------------------------- TESTE LOCAL -----------------------------------

json_path = "pulsenlp/data.json"

app = criar_dashboard(
    json_path,
    col_linha_x="nome",
    col_linha_y="rating",
    col_barra_x="rating",
    col_barra_y="nome",
    colunas_filtros_linha=["nome"],
    colunas_filtro_barra=["nome"],
    col_wordcloud="texto"
)

app.gatilho = {"atualizar": 0}

def trigger_update():
    app.gatilho["atualizar"] += 1
    app._cached_gatilho = {"atualizar": app.gatilho["atualizar"]}
    app._callback_map["gatilho-update.data"]["callback"](
        app._cached_gatilho
    )

app._trigger_update = trigger_update

if __name__ == "__main__":
    observer = iniciar_observador(app, path=json_path)
    try:
        app.run(debug=True)
    finally:
        observer.stop()
        observer.join()