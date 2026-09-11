from __future__ import annotations


def desenhar_grafo(grafo: dict, caminho: list | None = None, saida: str = "grafo.png") -> None:
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as exc:
        raise RuntimeError("instale as dependências com: pip install -r requirements.txt") from exc
    rede = nx.DiGraph()
    for origem, vizinhos in grafo.items():
        for destino, peso in vizinhos.items():
            rede.add_edge(origem, destino, weight=peso)
    posicoes = nx.spring_layout(rede, seed=42)
    arestas_caminho = set(zip(caminho or [], (caminho or [])[1:]))
    cores = ["crimson" if aresta in arestas_caminho else "#4c78a8" for aresta in rede.edges()]
    nx.draw(rede, posicoes, with_labels=True, node_color="#f2cf5b", edge_color=cores, arrows=True)
    nx.draw_networkx_edge_labels(rede, posicoes, edge_labels=nx.get_edge_attributes(rede, "weight"))
    plt.tight_layout()
    plt.savefig(saida, dpi=160)
    plt.close()
