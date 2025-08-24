import pandas as pd
from dashboard_module.dashboard import criar_dashboard
from nlp_module.preprocessing import process
from nlp_module.sentiment import analysis_sentiment
#from simulation_module.async_runner import 

def main():

    json_path = "data.json"

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

    app.run_server(debug=True)

    # Gerar JSON agentes de ia

    while True:

        # Aplicar NLTK
        # Aplicar Analise de sentimento
        # Salvar JSON novo
        
        pass

    

if __name__ == "__main__":
    main()