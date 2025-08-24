import dash
from dash import dcc, html
import dash_mantine_components as dmc
import pandas as pd
import json
from typing import List
from charts import gerar_grafico_linha, gerar_grafico_barra
from wordcloud_gen import gerar_nuvem_palavras_base64

# Função para criar filtros
def criar_filtros(df: pd.DataFrame, colunas: List[str], id_prefix: str):
    filtros = []
    for i, col in enumerate(colunas):
        valores_unicos = df[col].dropna().unique()
        valores_unicos = sorted(valores_unicos)
        filtro = dmc.CheckboxGroup(
            id=f"{id_prefix}-{i}",
            value=[],  # Nenhuma opção selecionada por padrão
            size="sm",  # Filtros menores
            style={"marginBottom": "10px", "marginLeft": "5px", "marginRight": "5px"},
            children=[dmc.Checkbox(label=str(v), value=str(v)) for v in valores_unicos]
        )
        filtros.append(filtro)
    return filtros

# Função para criar o dashboard
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

    # Carregar o arquivo JSON e convertê-lo em DataFrame
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

    # Layout da aplicação
    app.layout = dmc.MantineProvider(
        theme={"colorScheme": "dark"},
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dmc.Container(
                [
                    dmc.Grid(
                        [
                            # Primeira coluna: Wordcloud e Último Comentário
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
                            # Segunda coluna: Gráficos de Linha e Barra
                            dmc.Col(
                                [
                                    dmc.Card(
                                        children=[
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
            # Intervalo de atualização do gráfico de linha
            dcc.Interval(
                id="intervalo-grafico-linha",
                interval=5 * 1000,  # Atualiza a cada 5 segundos (o valor é em milisegundos)
                n_intervals=0,
            ),
            # Intervalo de atualização do gráfico de barra
            dcc.Interval(
                id="intervalo-grafico-barra",
                interval=5 * 1000,  # Atualiza a cada 5 segundos (o valor é em milisegundos)
                n_intervals=0,
            ),
            # Intervalo para atualizar os cards (wordcloud e comentário)
            dcc.Interval(
                id="intervalo-cards",
                interval=10 * 1000,  # Atualiza a cada 5 segundos
                n_intervals=0,
            ),
        ],
    )

    # Callback para atualizar o gráfico de linha em tempo real
    @app.callback(
        dash.dependencies.Output("grafico-linha", "figure"),
        [dash.dependencies.Input("intervalo-grafico-linha", "n_intervals")]
    )
    def update_grafico_linha(n_intervals):
        # Lê o arquivo JSON sempre que o intervalo é disparado
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        return gerar_grafico_linha(df_atualizado, col_linha_x, col_linha_y)

    # Callback para atualizar o gráfico de barra conforme os filtros
    @app.callback(
        dash.dependencies.Output("grafico-barra", "figure"),
        [
            dash.dependencies.Input(f"filtro-barra-{i}", "value") for i in range(len(colunas_filtro_barra))
        ]
        + [dash.dependencies.Input("intervalo-grafico-barra", "n_intervals")]
    )
    def update_grafico_barra(*valores_filtros):
        valores_filtros = valores_filtros[:-1]  # Exclui o valor do intervalo
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        dff = df_atualizado.copy()
        for col, val in zip(colunas_filtro_barra, valores_filtros):
            if val:
                if isinstance(dff[col].iloc[0], (int, float)):
                    val = [int(v) for v in val]
                dff = dff[dff[col].isin(val)]
        return gerar_grafico_barra(dff, col_barra_x, col_barra_y)

    # Callback para atualizar os cards (wordcloud e comentário)
    @app.callback(
        [
            dash.dependencies.Output("imagem-wordcloud", "src"),
            dash.dependencies.Output("nome-comentario", "children"),
            dash.dependencies.Output("texto-comentario", "children"),
        ],
        [dash.dependencies.Input("intervalo-cards", "n_intervals")]
    )
    def update_cards(n_intervals):
        # Lê o arquivo JSON sempre que o intervalo é disparado
        data = ler_json()
        df_atualizado = pd.DataFrame(data)

        # Último comentário
        ultimo = df_atualizado.iloc[-1]
        nome = ultimo["nome"]
        texto = ultimo["texto"]

        # Gerar a imagem da wordcloud
        imagem_wordcloud = gerar_nuvem_palavras_base64(df_atualizado, coluna=col_wordcloud)

        # Retornar as atualizações para os cards
        return imagem_wordcloud, nome, texto

    return app

# ---------------------------------- TESTES ------------------------------------------------

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




































