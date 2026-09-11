"""Dijkstra e A* com seleção linear e heurística consistente."""

from collections.abc import Callable
from dataclasses import dataclass
from math import inf

from grafo import Grafo, Peso, somar_custos, validar_grafo, validar_numero

Heuristica = Callable[[str, str], Peso]
Algoritmo = Callable[[Grafo, str, str], tuple[Peso, list[str], int]]


@dataclass
class ResultadoBusca:
    """Com destino, distâncias de outros vértices podem ser provisórias."""

    distancias: dict[str, Peso]
    anteriores: dict[str, str]
    vertices_expandidos: int


def reconstruir_caminho(
    anteriores: dict[str, str], origem: str, destino: str
) -> list[str]:
    """Reconstrói a sequência a partir dos predecessores produzidos pela busca."""
    if destino != origem and destino not in anteriores:
        return []
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anteriores[caminho[-1]])
    return list(reversed(caminho))


def _estimar_distancias(
    grafo: Grafo, destino: str | None, heuristica: Heuristica | None
) -> dict[str, Peso]:
    if heuristica is None:
        return dict.fromkeys(grafo, 0)
    if destino is None:
        raise ValueError("a heurística exige um destino")
    estimativas = {vertice: heuristica(vertice, destino) for vertice in grafo}
    for estimativa in estimativas.values():
        validar_numero(estimativa, "heurística")
    if estimativas[destino] != 0:
        raise ValueError("a heurística no destino deve ser zero")
    for origem, vizinhos in grafo.items():
        for vizinho, peso in vizinhos.items():
            if estimativas[origem] > somar_custos(peso, estimativas[vizinho]):
                raise ValueError(
                    "a heurística deve ser consistente em todas as arestas"
                )
    return estimativas


def buscar(
    grafo: Grafo,
    origem: str,
    destino: str | None = None,
    heuristica: Heuristica | None = None,
) -> ResultadoBusca:
    """Sem destino, resolve fonte única; com destino, interrompe ao fixá-lo.

    Tempo O(V² + E), espaço auxiliar O(V), com heurística O(1) por chamada.
    Empates seguem a ordem de inserção dos vértices no dicionário.
    """
    validar_grafo(grafo)
    if origem not in grafo:
        raise KeyError(f"vértice de origem inexistente: {origem!r}")
    if destino is not None and destino not in grafo:
        raise KeyError(f"vértice de destino inexistente: {destino!r}")
    estimativas = _estimar_distancias(grafo, destino, heuristica)
    distancias = dict.fromkeys(grafo, inf)
    prioridades = dict.fromkeys(grafo, inf)
    anteriores: dict[str, str] = {}
    visitados: set[str] = set()
    distancias[origem] = 0
    prioridades[origem] = estimativas[origem]

    while len(visitados) < len(grafo):
        candidatos = (vertice for vertice in grafo if vertice not in visitados)
        atual = min(candidatos, key=prioridades.__getitem__, default=None)
        if atual is None or prioridades[atual] == inf:
            break
        visitados.add(atual)
        if atual == destino:
            break
        for vizinho, peso in grafo[atual].items():
            if vizinho in visitados:
                continue
            nova_distancia = somar_custos(distancias[atual], peso)
            if nova_distancia < distancias[vizinho]:
                distancias[vizinho] = nova_distancia
                prioridades[vizinho] = somar_custos(
                    nova_distancia, estimativas[vizinho]
                )
                anteriores[vizinho] = atual
    return ResultadoBusca(distancias, anteriores, len(visitados))


def dijkstra_com_caminho(
    grafo: Grafo, origem: str, destino: str
) -> tuple[Peso, list[str], int]:
    """Retorna custo, caminho e quantidade de vértices fixados até o destino."""
    return a_estrela(grafo, origem, destino)


def a_estrela(
    grafo: Grafo,
    origem: str,
    destino: str,
    heuristica: Heuristica | None = None,
) -> tuple[Peso, list[str], int]:
    """A* sem reabertura: exige consistência; h=0 equivale a Dijkstra."""
    resultado = buscar(grafo, origem, destino, heuristica)
    caminho = reconstruir_caminho(resultado.anteriores, origem, destino)
    return resultado.distancias[destino], caminho, resultado.vertices_expandidos
