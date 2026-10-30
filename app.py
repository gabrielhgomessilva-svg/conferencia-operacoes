"""Conferência XML x TXT - ponto de entrada.

Uso:
    python app.py                       # usa config.json
    python app.py --raiz "C:\\operacoes\\xml"
    python app.py --demo                # roda com a pasta exemplos_pasta (dados de teste)
"""
import argparse
import json
import logging
import os
import socket
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from core.auth import Auth  # noqa: E402
from core.indicantes import Indicantes  # noqa: E402
from core.scanner import Scanner  # noqa: E402
from core.server import criar_servidor  # noqa: E402
from core.store import Store  # noqa: E402


def main():
    for f in (sys.stdout, sys.stderr):          # evita erro de acento no console do Windows
        try:
            f.reconfigure(errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", help="Pasta raiz com as pastas dos dias (ex.: C:\\operacoes\\xml)")
    ap.add_argument("--porta", type=int)
    ap.add_argument("--demo", action="store_true", help="usa a pasta de exemplo para testar")
    a = ap.parse_args()

    cfg_path = os.path.join(BASE, "config.json")
    if not os.path.exists(cfg_path):          # primeira execução: usa o modelo
        cfg_path = os.path.join(BASE, "config.example.json")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    if a.demo:
        cfg["PastaRaiz"] = os.path.join(BASE, "exemplos_pasta")
        cfg["BancoDados"] = os.path.join(BASE, "demo.db")
        cfg["FontesZip"] = []  # no teste, só a pasta de exemplo
        cfg["PastaPdfs"] = os.path.join(BASE, "exemplos_pasta", "_pdfs")
        cfg["Indicantes"] = {"Ativo": False}
        sys.path.insert(0, os.path.join(BASE, "demo"))
        import gerar_exemplos                      # dados fictícios (precisa do reportlab)
        if not os.path.isdir(cfg["PastaRaiz"]):
            gerar_exemplos.gerar(cfg["PastaRaiz"])
    if a.raiz:
        cfg["PastaRaiz"] = a.raiz
    if a.porta:
        cfg["Porta"] = a.porta

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    for nome in ("pypdf", "pypdf._cmap", "pypdf._font", "fontTools"):   # avisos de fonte dos PDFs: irrelevantes para a conferência
        logging.getLogger(nome).setLevel(logging.ERROR)
    db = cfg.get("BancoDados", "conferencia.db")
    store = Store(db if os.path.isabs(db) else os.path.join(BASE, db))
    auth = Auth(store)
    if a.demo:                                     # gerentes fictícios, só para a demonstração
        store.indicantes_gravar(gerar_exemplos.GERENTES)
    scanner = Scanner(cfg)
    scanner.iniciar()
    indicantes = Indicantes(cfg, store)
    indicantes.iniciar()
    srv = criar_servidor(cfg, scanner, store, auth, indicantes)

    porta = srv.server_address[1]
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        ip = "IP-DO-SERVIDOR"
    print(f"Monitorando: {cfg['PastaRaiz']}")
    print(f"Abra no navegador:  http://localhost:{porta}   |   outras máquinas: http://{ip}:{porta}")
    if not auth.tem_usuarios():
        print(f"PRIMEIRO ACESSO: abra o endereço acima e crie a senha do administrador ({cfg.get('AdminInicial', 'ADMIN')}).")
    print("Para encerrar: Ctrl+C")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scanner.parar()
        indicantes.parar()


if __name__ == "__main__":
    main()
