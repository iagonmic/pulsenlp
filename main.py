# main.py
import threading
import asyncio
from pulsenlp.simulation_module.async_runner import main as async_main
import os

json_path = "dashboard_module/data.json"
topico_path  = "dashboard_module/topico.json"

# Config do dashboard

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
