from itertools import pairwise
from math import isfinite
from pathlib import Path
from typing import Any

import matplotlib
import networkx as nx

from caminhos_minimos.grafo import Grafo, validar_grafo

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def desenhar_grafo(
    grafo: Grafo, caminho: list[str] | None = None, saida: str | Path = "grafo.png"
) -> None:
    validar_grafo(grafo)
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
    nomes = [resultado["algoritmo"] for resultado in resultados]
    metricas = [
        ("tempo_execucao_ms", "Tempo mediano", "Milissegundos"),
        ("desvio_tempo_ms", "Desvio padrão do tempo", "Milissegundos"),
    ]
    figura, eixos = plt.subplots(1, 2, figsize=(10, 4))
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
