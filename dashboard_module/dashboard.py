import dash
from dash import dcc, html
import dash_mantine_components as dmc
import pandas as pd
import json
from typing import List
from charts import gerar_grafico_linha, gerar_grafico_barra
from wordcloud_gen import gerar_nuvem_palavras_base64

def criar_filtros(df: pd.DataFrame, colunas: List[str], id_prefix: str):
    filtros = []
    for i, col in enumerate(colunas):
        valores_unicos = df[col].dropna().unique()
        valores_unicos = sorted(valores_unicos)

        filtro = dmc.Select(
            id=f"{id_prefix}-{i}",
            data=[{"label": str(v), "value": str(v)} for v in valores_unicos],
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
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)

    # Carregar o arquivo JSON inicial
    data = ler_json()
    df = pd.DataFrame(data)

    # Último comentário
    ultimo = df.iloc[-1]
    nome = ultimo["nome"]
    texto = ultimo["texto"]

    # Gerar wordcloud em base64
    imagem_wordcloud = gerar_nuvem_palavras_base64(df, coluna=col_wordcloud)

    # Criar filtros
    filtros_linha = criar_filtros(df, colunas_filtros_linha, id_prefix="filtro-linha")
    filtros_barra = criar_filtros(df, colunas_filtro_barra, id_prefix="filtro-barra")

    # Layout
    app.layout = dmc.MantineProvider(
        theme={"colorScheme": "dark"},
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dmc.Container(
                [
                    dmc.Grid(
                        [
                            # Coluna esquerda: Wordcloud e Último Comentário
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
                            # Coluna direita: Gráficos
                            dmc.Col(
                                [
                                    dmc.Card(
                                        children=[
                                            dmc.CardSection(children=filtros_linha + [html.Div(style={"height": "15px"})]),
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
                                            dmc.CardSection(children=filtros_barra + [html.Div(style={"height": "15px"})]),
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
            dcc.Interval(id="intervalo-grafico-linha", interval=5 * 1000, n_intervals=0),
            dcc.Interval(id="intervalo-grafico-barra", interval=5 * 1000, n_intervals=0),
            dcc.Interval(id="intervalo-cards", interval=10 * 1000, n_intervals=0),
        ],
    )

    # ------------------------ CALLBACKS -----------------------------

    # Atualizar gráfico de linha
    @app.callback(
        dash.dependencies.Output("grafico-linha", "figure"),
        [
            dash.dependencies.Input(f"filtro-linha-{i}", "value") for i in range(len(colunas_filtros_linha))
        ] + [dash.dependencies.Input("intervalo-grafico-linha", "n_intervals")]
    )
    def update_grafico_linha(*valores_filtros):
        valores_filtros = valores_filtros[:-1]  # exclui n_intervals
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtros_linha, valores_filtros):
            if val is not None and val != "":
                dff = dff[dff[col] == val]

        return gerar_grafico_linha(dff, col_linha_x, col_linha_y)

    # Atualizar gráfico de barra
    @app.callback(
        dash.dependencies.Output("grafico-barra", "figure"),
        [
            dash.dependencies.Input(f"filtro-barra-{i}", "value") for i in range(len(colunas_filtro_barra))
        ] + [dash.dependencies.Input("intervalo-grafico-barra", "n_intervals")]
    )
    def update_grafico_barra(*valores_filtros):
        valores_filtros = valores_filtros[:-1]
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtro_barra, valores_filtros):
            if val is not None and val != "":
                dff = dff[dff[col] == val]

        return gerar_grafico_barra(dff, col_barra_x, col_barra_y)

    # Atualizar cards (wordcloud e último comentário)
    @app.callback(
        [
            dash.dependencies.Output("imagem-wordcloud", "src"),
            dash.dependencies.Output("nome-comentario", "children"),
            dash.dependencies.Output("texto-comentario", "children"),
        ],
        [dash.dependencies.Input("intervalo-cards", "n_intervals")]
    )
    def update_cards(n_intervals):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)

        ultimo = df_atualizado.iloc[-1]
        nome = ultimo["nome"]
        texto = ultimo["texto"]

        imagem_wordcloud = gerar_nuvem_palavras_base64(df_atualizado, coluna=col_wordcloud)

        return imagem_wordcloud, nome, texto

    return app

# ------------------------------- TESTE LOCAL -----------------------------------

json_path = "dashboard_module/data.json"

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

if __name__ == "__main__":
    app.run_server(debug=True)






































