import matplotlib
matplotlib.use('Agg') # evitar problemas de threading com o Dash
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
                                    value=3,  # valor padrão
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

    @app.callback(
    # A saída agora pode ser ajustada para o que você precisar.
    # Por exemplo, uma mensagem de sucesso em vez de limpar o input.
    dash.Output("input-topico", "value"),
    dash.Input("botao-topico", "n_clicks"),
    dash.State("input-topico", "value"),
    # O ID do State foi atualizado para "input-agentes" de acordo com o seu layout.
    dash.State("input-agentes", "value"),
    prevent_initial_call=True
)
    def definir_topico_e_agentes(n_clicks, topico, num_agentes):
        """
        Define e salva o tópico e o número de agentes em um arquivo JSON.

        Args:
            n_clicks (int): Número de cliques no botão.
            topico (str): O tópico inserido pelo usuário.
            num_agentes (str): O número de agentes inserido pelo usuário.

        Returns:
            str: Uma string vazia para limpar o campo de entrada do tópico.
        """
        if not topico or topico.strip() == "":
            # Se o tópico estiver vazio, retorna sem fazer nada.
            print("Tópico não pode ser vazio.")
            return topico

        # Verifica se o número de agentes é válido antes de salvar.
        try:
            # A entrada de número do Dash já retorna um tipo numérico,
            # mas é bom ter a validação.
            num_agentes_int = int(num_agentes)
        except (ValueError, TypeError):
            print("Número de agentes inválido.")
            # Retorne o valor original para o usuário corrigir.
            return topico

        # Cria um dicionário para armazenar os dados.
        dados_para_salvar = {
            "topico": topico,
            "num_agentes": num_agentes_int
        }

        try:
            # Salva o dicionário como JSON.
            # 'w' para sobrescrever, 'a' para adicionar ao final.
            # 'indent=4' para formatar o JSON de forma legível.
            with open("dashboard_module/topico.json", "w", encoding="utf-8") as f:
                json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)
            
            print(f"Dados salvos com sucesso: {dados_para_salvar}")  # Mensagem de debug
            
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")
            # Em caso de erro, você pode retornar algo para notificar o usuário.

        # Retorna uma string vazia para limpar o campo de entrada 'input-topico'.
        return topico
    
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
    app.run(debug=True)