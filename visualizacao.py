"""Figuras de grafos e métricas; funcionam também sem interface gráfica."""

from itertools import pairwise
from math import isfinite
from pathlib import Path
from typing import Any

from grafo import Grafo, validar_grafo


def _carregar_bibliotecas():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as erro:
        raise RuntimeError(
            "instale as dependências: pip install -r requirements.txt"
        ) from erro
    return plt, nx


def desenhar_grafo(
    grafo: Grafo, caminho: list[str] | None = None, saida: str | Path = "grafo.png"
) -> None:
    """Preserva vértices isolados e destaca em vermelho o caminho informado."""
    validar_grafo(grafo)
    plt, nx = _carregar_bibliotecas()
    rede = nx.DiGraph()
    rede.add_nodes_from(grafo)
    for origem, vizinhos in grafo.items():
        for destino, peso in vizinhos.items():
            rede.add_edge(origem, destino, weight=peso)
    posicoes = nx.spring_layout(rede, seed=42)
    arestas_caminho = set(pairwise(caminho or []))
    cores = [
        "crimson" if aresta in arestas_caminho else "#4c78a8" for aresta in rede.edges()
    ]
    figura, eixo = plt.subplots(figsize=(9, 6))
    try:
        nx.draw(
            rede,
            posicoes,
            ax=eixo,
            with_labels=True,
            node_color="#f2cf5b",
            edge_color=cores,
            arrows=True,
            node_size=650,
            connectionstyle="arc3,rad=0.08",
        )
        nx.draw_networkx_edge_labels(
            rede,
            posicoes,
            ax=eixo,
            edge_labels=nx.get_edge_attributes(rede, "weight"),
            connectionstyle="arc3,rad=0.08",
        )
        eixo.set_title("Caminho mínimo em vermelho" if caminho else "Grafo direcionado")
        figura.tight_layout()
        figura.savefig(saida, dpi=160)
    finally:
        plt.close(figura)


def desenhar_comparacao(resultados: list[dict[str, Any]], saida: str | Path) -> None:
    """Compara custo, mediana do tempo e vértices fixados em uma consulta."""
    plt, _ = _carregar_bibliotecas()
    nomes = [resultado["algoritmo"] for resultado in resultados]
    metricas = [
        ("distancia", "Distância", "Custo"),
        ("tempo_execucao_ms", "Tempo mediano", "Milissegundos"),
        ("vertices_expandidos", "Vértices fixados", "Quantidade"),
    ]
    figura, eixos = plt.subplots(1, 3, figsize=(13, 4))
    try:
        for eixo, (campo, titulo, unidade) in zip(eixos, metricas, strict=True):
            valores = [resultado[campo] for resultado in resultados]
            valores_finitos = [
                valor if valor is not None and isfinite(valor) else 0
                for valor in valores
            ]
            barras = eixo.bar(nomes, valores_finitos, color=["#4c78a8", "#e08d3c"])
            for barra, valor in zip(barras, valores, strict=True):
                if valor is None or not isfinite(valor):
                    eixo.annotate("inalcançável", (barra.get_x(), 0), rotation=90)
            eixo.set_title(titulo)
            eixo.set_ylabel(unidade)
            eixo.grid(axis="y", alpha=0.3)
        figura.tight_layout()
        figura.savefig(saida, dpi=160)
    finally:
        plt.close(figura)
