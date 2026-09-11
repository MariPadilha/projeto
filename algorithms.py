from collections.abc import Callable
from math import inf
from typing import Any


Heuristica = Callable[[Any, Any], float]


def reconstruir_caminho(
    anteriores: dict[Any, Any], origem: Any, destino: Any
) -> list[Any]:
    if destino != origem and destino not in anteriores:
        return []
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anteriores[caminho[-1]])
    return list(reversed(caminho))


def selecionar_menor_prioridade(
    prioridades: dict[Any, float], visitados: set[Any]
) -> Any | None:
    candidatos = (vertice for vertice in prioridades if vertice not in visitados)
    return min(candidatos, key=prioridades.__getitem__, default=None)


def buscar_caminho(
    grafo: dict[Any, dict[Any, float]],
    origem: Any,
    destino: Any,
    heuristica: Heuristica | None = None,
) -> tuple[float, list[Any], int]:
    if origem not in grafo or destino not in grafo:
        raise KeyError("origem ou destino inexistente")

    estimar = heuristica or (lambda _origem, _destino: 0)
    distancias = {vertice: inf for vertice in grafo}
    prioridades = {vertice: inf for vertice in grafo}
    anteriores: dict[Any, Any] = {}
    visitados: set[Any] = set()
    distancias[origem] = 0
    prioridades[origem] = estimar(origem, destino)
    expandidos = 0

    while len(visitados) < len(prioridades):
        atual = selecionar_menor_prioridade(prioridades, visitados)
        if atual is None or prioridades[atual] == inf:
            break
        visitados.add(atual)
        expandidos += 1
        if atual == destino:
            break

        for vizinho, peso in grafo[atual].items():
            if peso < 0:
                raise ValueError("A estrela não aceita arestas com peso negativo")
            nova_distancia = distancias[atual] + peso
            if vizinho in visitados or nova_distancia >= distancias[vizinho]:
                continue
            distancias[vizinho] = nova_distancia
            prioridades[vizinho] = nova_distancia + estimar(vizinho, destino)
            anteriores[vizinho] = atual

    caminho = reconstruir_caminho(anteriores, origem, destino) if distancias[destino] != inf else []
    return distancias[destino], caminho, expandidos


def dijkstra_com_caminho(
    grafo: dict[Any, dict[Any, float]], origem: Any, destino: Any
) -> tuple[float, list[Any], int]:
    return buscar_caminho(grafo, origem, destino)


def a_estrela(
    grafo: dict[Any, dict[Any, float]],
    origem: Any,
    destino: Any,
    heuristica: Heuristica | None = None,
) -> tuple[float, list[Any], int]:
    return buscar_caminho(grafo, origem, destino, heuristica)
