import os
import matplotlib
matplotlib.use('Agg') # evitar problemas de threading com o Dash
import dash
from dash import dcc, html
# Importação correta das dependências
from dash.dependencies import Input, Output, State 
import dash_mantine_components as dmc
import pandas as pd
import json
from typing import List
# Importações mockadas (presumindo que funcionam)
from pulsenlp.charts import gerar_grafico_linha, gerar_grafico_barra
from pulsenlp.wordcloud_gen import gerar_nuvem_palavras_base64
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pulsenlp.nlp_module.preprocessing import pos_tagging, sentence_segmentation, noun_chunks


# Constantes de Estilo (Mantidas do ajuste de estilo)
COR_FUNDO_PRINCIPAL = "#0f172a" 
COR_FUNDO_CARD = "#1e293b"      
COR_TEXTO_PADRAO = "#e2e8f0"    
COR_PRIMARIA = "cyan"           

def ler_contador_json():
    """Retorna o timestamp da última modificação do arquivo."""
    if os.path.exists("pulsenlp/data.json"):
        return os.path.getmtime("pulsenlp/data.json") 
    return 0

class FileChangeHandler(FileSystemEventHandler):
    """
    Manipulador de eventos do watchdog. 
    """
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        if event.src_path.endswith("data.json"):
            print(f"⚡ data.json atualizado - evento watchdog capturado.")


def iniciar_observador(app, path="pulsenlp/data.json"):
    event_handler = FileChangeHandler(app)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(path), recursive=False)
    observer.start()
    return observer


def criar_filtros(colunas: List[str], id_prefix: str):
    filtros = []
    for i, col in enumerate(colunas):
        filtro = dmc.Select(
            id=f"{id_prefix}-{i}",
            data=[], 
            placeholder=f"Filtrar por {col.capitalize()}",
            clearable=True,
            searchable=True,
            nothingFound="Sem opções",
            size="sm",
            radius="md",
            style={
                "flexGrow": 1,
                "marginTop": "0px",
                "marginBottom": "0px",
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

    def ler_json():
        if os.path.exists(json_path):
            try:
                with open(json_path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Erro ao decodificar JSON. Retornando dados de exemplo.")
                return {"nome": ["Exemplo"], "texto": ["pulsenlp dash"], "style": ["Formal"], "tone": ["Amigável"], "rating": [5.0], "topic": ["dash"], "round": [0]}
        
        return {"nome": ["Arnaldo"], "texto": ["arroba"], "style": ["Formal"], "tone": ["Amigável"], "rating": [0.0], "topic": ["esporte"], "round": [0]}

    data = ler_json()
    df = pd.DataFrame(data)

    if not df.empty:
        ultimo = df.iloc[-1]
        nome = ultimo["nome"]
        texto = ultimo["texto"]
    else:
        nome = "N/A"
        texto = "Nenhum dado ainda."
        
    imagem_wordcloud = gerar_nuvem_palavras_base64(df, coluna=col_wordcloud)

    filtros_linha = criar_filtros(colunas_filtros_linha, id_prefix="filtro-linha")
    filtros_barra = criar_filtros(colunas_filtro_barra, id_prefix="filtro-barra")

    # Layout
    app.layout = dmc.MantineProvider(
        theme={"colorScheme": "dark", "primaryColor": COR_PRIMARIA},
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dcc.Store(id="gatilho-update", data={"timestamp": ler_contador_json()}),
            dmc.Container(
                [
                    # Seção de Controle
                    dmc.Card(
                        [
                            dmc.Text("Configurações da Simulação", fw=700, size="xl", color=COR_TEXTO_PADRAO, mb=15),
                            dmc.Group(
                                [
                                    dmc.TextInput(
                                        label="Digite o tópico da conversa:",
                                        id="input-topico",
                                        placeholder="Ex: Últimos lançamentos da NASA...",
                                        style={"flex": 2},
                                        size="md",
                                        radius="md"
                                    ),
                                    dmc.NumberInput(
                                        id="input-agentes",
                                        value=3,
                                        min=1,
                                        max=10,
                                        step=1,
                                        label="Número de Agentes:",
                                        size="md",
                                        radius="md",
                                        style={"width": "150px"},
                                    ),
                                ],
                                grow=True,
                                align="flex-end"
                            ),
                            dmc.Button("Iniciar Simulação",id="botao-topico", color=COR_PRIMARIA, radius="md", fullWidth=True, size="lg", style={"marginTop": "20px"}),
                        ],
                        withBorder=True,
                        shadow="xl",
                        radius="lg",
                        p="xl",
                        style={
                            "backgroundColor": COR_FUNDO_CARD,
                            "marginBottom": "30px",
                            "border": f"1px solid #334155",
                        },
                    ),
                    
                    # Layout Principal
                    dmc.Grid(
                        [
                            # Coluna esquerda
                            dmc.Col(
                                html.Div(
                                    [
                                        # Card da Wordcloud
                                        dmc.Card(
                                            children=[
                                                dmc.Text("Nuvem de Palavras Mais Frequentes", fw=700, size="lg", color=COR_TEXTO_PADRAO, mb=10),
                                                dmc.CardSection(
                                                    children=[
                                                        html.Img(
                                                            id="imagem-wordcloud",
                                                            src=imagem_wordcloud,
                                                            style={
                                                                "width": "100%",
                                                                "maxHeight": "55vh",
                                                                "objectFit": "contain",
                                                                "borderRadius": "8px",
                                                                "display": "block",
                                                                "margin": "0 auto",
                                                            },
                                                        ),
                                                    ],
                                                    p="md"
                                                ),
                                            ],
                                            withBorder=True,
                                            shadow="md",
                                            radius="lg",
                                            p="lg",
                                            style={
                                                "backgroundColor": COR_FUNDO_CARD,
                                                "marginBottom": "20px",
                                                "flexGrow": 1,
                                                "border": f"1px solid #334155",
                                            },
                                        ),
                                        
                                        # Card do Último Comentário e Análise NLP (Scroll Adicionado Aqui)
                                        dmc.Card(
                                            [
                                                dmc.Text("Último Comentário e Análise NLP", fw=700, size="xl", color=COR_TEXTO_PADRAO, mb=15),
                                                dmc.Group([
                                                    dmc.ThemeIcon(
                                                        variant="light", radius="xl", size="lg", color=COR_PRIMARIA,
                                                        children=[dmc.Text("🗣️")]
                                                    ),
                                                    dmc.Text(id="nome-comentario", children=nome, fw=700, size="lg", color=COR_PRIMARIA),
                                                ], mb=10),
                                                dmc.Text(id="texto-comentario", children=f'"{texto}"', fw=500, size="md", mb=20, style={"fontStyle": "italic"}),
                                                
                                                dmc.Divider(my="xs", style={"opacity": 0.3}),

                                                dmc.Text("Frases Nominais (Noun Chunks):", fw=600, size="sm", mt=10, color="#cbd5e1"),
                                                dmc.Text(id="noun-chunks", fw=400, size="sm", children="Análise de Noun Chunks...", style={"whiteSpace": "pre-line", "color": "#94a3b8"}),
                                                
                                                dmc.Text("POS Tagging (Token|Tag):", fw=600, size="sm", mt=15, color="#cbd5e1"),
                                                dmc.Text(id="pos-tagging", fw=400, size="xs", children="Análise de POS Tagging...", style={"whiteSpace": "pre-line", "color": "#94a3b8", "wordBreak": "break-word"}),
                                                
                                                dmc.Text("Sentenças Segmentadas:", fw=600, size="sm", mt=15, color="#cbd5e1"),
                                                dmc.Text(id="sentencas", fw=400, size="sm", children="Análise de Sentenças...", style={"whiteSpace": "pre-line", "color": "#94a3b8"}),
                                            ],
                                            withBorder=True,
                                            shadow="md",
                                            radius="lg",
                                            p="lg",
                                            style={
                                                "backgroundColor": COR_FUNDO_CARD,
                                                "flexGrow": 1,
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "border": f"1px solid #334155",
                                                # IMPLEMENTAÇÃO DO SCROLL
                                                "maxHeight": "calc(45vh - 20px)",
                                                "overflowY": "auto",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "flexDirection": "column", "height": "100%"},
                                ),
                                span=6,
                                style={"display": "flex", "flexDirection": "column", "height": "100%"},
                            ),
                            
                            # Coluna direita: Gráficos
                            dmc.Col(
                                [
                                    # Card Gráfico de Linha
                                    dmc.Card(
                                        children=[
                                            dmc.Text("Evolução da Métrica ao longo do Tempo", fw=700, size="lg", color=COR_TEXTO_PADRAO, mb=10, p="md", style={"paddingBottom": "0"}),
                                            dmc.CardSection(
                                                id='filtros-linha', 
                                                children=dmc.Group(filtros_linha, spacing="lg", p="md", style={"paddingTop": "0"}), 
                                                withBorder=True, 
                                                inheritPadding=True, 
                                                style={"borderBottom": "1px solid #334155"}
                                            ),
                                            dcc.Graph(
                                                id="grafico-linha",
                                                figure=gerar_grafico_linha(df, col_linha_x, col_linha_y),
                                                config={'displayModeBar': False}, 
                                                style={"flex": "1 1 auto", "padding": "10px"},
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="md",
                                        radius="lg",
                                        style={
                                            "backgroundColor": COR_FUNDO_CARD,
                                            "flex": "1 1 50%",
                                            "marginBottom": "20px",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "height": "calc(50% - 10px)",
                                            "border": f"1px solid #334155",
                                        },
                                    ),
                                    
                                    # Card Gráfico de Barra
                                    dmc.Card(
                                        children=[
                                            dmc.Text("Ranking de Média por Agente", fw=700, size="lg", color=COR_TEXTO_PADRAO, mb=10, p="md", style={"paddingBottom": "0"}),
                                            dmc.CardSection(
                                                id='filtros-barra', 
                                                children=dmc.Group(filtros_barra, spacing="lg", p="md", style={"paddingTop": "0"}), 
                                                withBorder=True, 
                                                inheritPadding=True,
                                                style={"borderBottom": "1px solid #334155"}
                                            ),
                                            dcc.Graph(
                                                id="grafico-barra",
                                                figure=gerar_grafico_barra(df, col_barra_x, col_barra_y),
                                                config={'displayModeBar': False},
                                                style={"flex": "1 1 auto", "padding": "10px"},
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="md",
                                        radius="lg",
                                        style={
                                            "backgroundColor": COR_FUNDO_CARD,
                                            "flex": "1 1 50%",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "height": "calc(50% - 10px)",
                                            "border": f"1px solid #334155",
                                        },
                                    ),
                                ],
                                span=6,
                                style={"display": "flex", "flexDirection": "column", "height": "100%"},
                            ),
                        ],
                        gutter="xl",
                        style={"height": "calc(100vh - 120px)"}
                    ),
                ],
                fluid=True,
                style={"backgroundColor": COR_FUNDO_PRINCIPAL, "minHeight": "100vh", "padding": "25px"},
            ),
            # Intervalos
            dcc.Interval(id="intervalo-arquivo", interval=10000, n_intervals=0), 
        ],
    )

    # ------------------------ CALLBACKS -----------------------------

    @app.callback(
        Output("gatilho-update", "data"),
        [Input("intervalo-arquivo", "n_intervals")]
    )
    def atualizar_gatilho(_):
        return {"timestamp": ler_contador_json()} 

    @app.callback(
        Output("input-topico", "value"),
        [Input("botao-topico", "n_clicks")],
        [State("input-topico", "value"),
         State("input-agentes", "value")],
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
            "num_users": num_users_int
        }

        try:
            with open("pulsenlp/topico.json", "w", encoding="utf-8") as f:
                json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)
            print(f"Dados salvos com sucesso: {dados_para_salvar}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")

        return topico
    
    @app.callback(
        Output("grafico-linha", "figure"),
        [Input("gatilho-update", "data")] +
        [Input(f"filtro-linha-{i}", "value") for i in range(len(colunas_filtros_linha))]
    )
    def update_grafico_linha(gatilho, *filtros):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        
        if df_atualizado.empty:
            return gerar_grafico_linha(pd.DataFrame(), col_linha_x, col_linha_y)

        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtros_linha, filtros):
            if val is not None and val != "":
                dff = dff[dff[col].astype(str) == str(val)]

        return gerar_grafico_linha(dff, col_linha_x, col_linha_y)

    @app.callback(
        Output("grafico-barra", "figure"),
        [Input("gatilho-update", "data")] +
        [Input(f"filtro-barra-{i}", "value") for i in range(len(colunas_filtro_barra))]
    )
    def update_grafico_barra(gatilho, *filtros):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)
        
        if df_atualizado.empty or "rating" not in df_atualizado.columns:
            return gerar_grafico_barra(pd.DataFrame(), col_barra_x, col_barra_y)

        dff = df_atualizado.copy()

        for col, val in zip(colunas_filtro_barra, filtros):
            if val is not None and val != "":
                dff = dff[dff[col].astype(str) == str(val)]

        if dff.empty or "rating" not in dff.columns:
             return gerar_grafico_barra(pd.DataFrame(), col_barra_x, col_barra_y)

        try:
             dff['rating'] = pd.to_numeric(dff['rating'], errors='coerce')
        except:
             pass 

        df_media = dff.groupby("nome", as_index=False)["rating"].mean().sort_values(by="rating", ascending=False)
        return gerar_grafico_barra(df_media, col_barra_x, col_barra_y)

    @app.callback(
        [Output("imagem-wordcloud", "src"),
         Output("nome-comentario", "children"),
         Output("texto-comentario", "children"),
         Output("noun-chunks", "children"),
         Output("pos-tagging", "children"),
         Output("sentencas", "children")],
        [Input("gatilho-update", "data")]
    )
    def update_cards(gatilho):
        data = ler_json()
        df_atualizado = pd.DataFrame(data)

        if df_atualizado.empty:
            vazio_wc = gerar_nuvem_palavras_base64(pd.DataFrame({"texto": ["vazio"]}), coluna="texto") 
            return vazio_wc, "N/A", "Nenhum dado para exibir.", "Nenhum dado.", "Nenhum dado.", "Nenhum dado."

        ultimo = df_atualizado.iloc[-1]
        nome = ultimo["nome"]
        texto = ultimo["texto"]
        
        imagem_wordcloud = gerar_nuvem_palavras_base64(df_atualizado, coluna=col_wordcloud)

        texto_str = str(texto)
        
        noun_chunks_texto = noun_chunks(texto_str)
        pos_tagging_texto = pos_tagging(texto_str)
        sentencas_texto = sentence_segmentation(texto_str)

        noun_chunks_str = " | ".join(noun_chunks_texto) if noun_chunks_texto else "Nenhuma frase nominal encontrada."
        pos_tagging_str = " | ".join([f"{token[0]}|{token[3]}" for token in pos_tagging_texto]) if pos_tagging_texto else "Nenhuma marcação de POS encontrada."
        sentencas_str = "\n".join([f"• {s}" for s in sentencas_texto]) if sentencas_texto else "Nenhuma sentença encontrada."

        return imagem_wordcloud, nome, f'"{texto}"', noun_chunks_str, pos_tagging_str, sentencas_str

    for i, col in enumerate(colunas_filtros_linha):
        @app.callback(
            Output(f"filtro-linha-{i}", "data"),
            [Input("gatilho-update", "data")],
            prevent_initial_call=False
        )
        def update_filtro_linha(gatilho, col=col):
            data = ler_json()
            df_atualizado = pd.DataFrame(data)
            if df_atualizado.empty or col not in df_atualizado.columns:
                 return []
            
            valores_unicos = df_atualizado[col].astype(str).dropna().unique()
            valores_unicos = sorted(valores_unicos)
            return [{"label": str(v), "value": str(v)} for v in valores_unicos]

    for i, col in enumerate(colunas_filtro_barra):
        @app.callback(
            Output(f"filtro-barra-{i}", "data"),
            [Input("gatilho-update", "data")],
            prevent_initial_call=False
        )
        def update_filtro_barra(gatilho, col=col):
            data = ler_json()
            df_atualizado = pd.DataFrame(data)
            if df_atualizado.empty or col not in df_atualizado.columns:
                 return []
                 
            valores_unicos = df_atualizado[col].astype(str).dropna().unique()
            valores_unicos = sorted(valores_unicos)
            return [{"label": str(v), "value": str(v)} for v in valores_unicos]

    return app

# ------------------------------- TESTE LOCAL -----------------------------------

json_path = "pulsenlp/data.json"

app = criar_dashboard(
    json_path,
    col_linha_x="round", 
    col_linha_y="rating",
    col_barra_x="rating",
    col_barra_y="nome",
    colunas_filtros_linha=["nome", "style", "tone"], 
    colunas_filtro_barra=["topic"],
    col_wordcloud="texto"
)

if __name__ == "__main__":
    observer = iniciar_observador(app, path=json_path)
    try:
        app.run(debug=True)
    finally:
        observer.stop()
        observer.join()
