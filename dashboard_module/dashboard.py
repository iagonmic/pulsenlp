import dash
from dash import html
import pandas as pd
import json

from wordcloud_gen import gerar_nuvem_palavras_base64  

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

app = dash.Dash(__name__)

app.layout = html.Div([                                                             # TODO usar ddk para organizar o layout
    html.H1("Dashboard com Word Cloud Dinâmica", style={'textAlign': 'center'}),    # TODO Criar graficos no Plotly e plotar no dash
    
    html.Div([
        html.Img(
            src=gerar_nuvem_palavras_base64(df, coluna='texto'),  
            style={'width': '80%', 'display': 'block', 'margin': '0 auto'}
        )
    ], style={'padding': '20px'})
])

if __name__ == "__main__":
    app.run(debug=True)
