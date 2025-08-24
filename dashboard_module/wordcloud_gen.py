from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io
import base64
import re
import pandas as pd

def gerar_nuvem_palavras_base64(df: pd.DataFrame, coluna: str) -> str:
    """
    Gera uma Word Cloud a partir da coluna do DataFrame e retorna
    uma imagem em base64 para ser usada no Dash.

    :param df: DataFrame contendo os dados
    :param coluna: nome da coluna com textos
    :return: string base64 da imagem PNG
    """
    texto_completo = ' '.join(df[coluna].dropna())
    texto_completo = re.sub(r'[^\w\s]', '', texto_completo)

    wordcloud = WordCloud(
        width=1920,
        height=1080,
        background_color='white',
        max_words=200,
        colormap='viridis',
        stopwords=STOPWORDS
    ).generate(texto_completo)

    plt.figure(figsize=(16, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Nuvem de Palavras", fontsize=18)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=400, bbox_inches='tight')
    plt.close()
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"
