import plotly.graph_objs as go
import pandas as pd

def gerar_grafico_linha(df, coluna_x, coluna_y):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[coluna_x],
        y=df[coluna_y],
        mode='lines+markers',
        line=dict(color='#4dabf7'),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title='Análise de Sentimento x Rodada',
        template='plotly_dark',
        paper_bgcolor='#1A1B1E',
        plot_bgcolor='#1A1B1E',
        font=dict(color='white'),
        xaxis=dict(title=coluna_x, showgrid=False, dtick=1),
        yaxis=dict(title=coluna_y, showgrid=False),
    )
    return fig


def gerar_grafico_barra(df, coluna_x, coluna_y):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[coluna_x],
        y=df[coluna_y],
        orientation='h',
        marker=dict(color='#4dabf7')
    ))
    fig.update_layout(
        title='Rating x Pessoa',
        template='plotly_dark',
        paper_bgcolor='#1A1B1E',
        plot_bgcolor='#1A1B1E',
        font=dict(color='white'),
        xaxis=dict(title=coluna_x, showgrid=False),
        yaxis=dict(title=coluna_y, showgrid=False)
    )
    return fig