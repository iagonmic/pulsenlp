# main.py
import threading
import asyncio
from dashboard_module.dashboard import criar_dashboard
from simulation_module.async_runner import main as async_main
import os

json_path = "dashboard_module/data.json"
topico_path  = "dashboard_module/topico.json"

# Config do dashboard
app = criar_dashboard(
    json_path,
    col_linha_x="round",
    col_linha_y="rating",
    col_barra_x="rating",
    col_barra_y="nome",
    colunas_filtros_linha=["round"],
    colunas_filtro_barra=["nome"],
    col_wordcloud="texto"
)

app.gatilho = {"atualizar": 0}  # inicializa contador interno

# Função wrapper para rodar o async_runner
def rodar_async_runner():
    asyncio.run(async_main())   # main() do async_runner deve ser async

if __name__ == "__main__":
    if os.path.exists(json_path):
        os.remove(json_path)
    if os.path.exists(topico_path):
        os.remove(topico_path)
        
    # 1) Start async_runner em thread separada
    t = threading.Thread(target=rodar_async_runner, daemon=True)
    t.start()

    # 2) Start dashboard
    app.run_server(debug=True, use_reloader=False)  
