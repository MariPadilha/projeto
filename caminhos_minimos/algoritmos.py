from dataclasses import dataclass
from math import inf

from caminhos_minimos.grafo import (
    Grafo,
    Peso,
    somar_custos,
    validar_grafo,
    validar_numero_nao_negativo,
)


@dataclass
class _ResultadoBusca:
    distancias: dict[str, Peso]
    anteriores: dict[str, str]
    vertices_expandidos: int


def reconstruir_caminho(
    anteriores: dict[str, str], origem: str, destino: str
) -> list[str]:
    if destino != origem and destino not in anteriores:
        return []
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anteriores[caminho[-1]])
    return list(reversed(caminho))


def _calcular_heuristica_consistente(
    grafo: Grafo, destino: str | None, heuristica
) -> dict[str, Peso]:
    if heuristica is None:
        return dict.fromkeys(grafo, 0)
    if destino is None:
        raise ValueError("a heurística exige um destino")
    estimativas = {vertice: heuristica(vertice, destino) for vertice in grafo}
    for estimativa in estimativas.values():
        validar_numero_nao_negativo(estimativa, "heurística")
    if estimativas[destino] != 0:
        raise ValueError("a heurística no destino deve ser zero")
    for origem, vizinhos in grafo.items():
        for vizinho, peso in vizinhos.items():
            if estimativas[origem] > somar_custos(peso, estimativas[vizinho]):
                raise ValueError(
                    "a heurística deve ser consistente em todas as arestas"
                )
    return estimativas


def _executar_busca(
    grafo: Grafo,
    origem: str,
    destino: str | None = None,
    heuristica=None,
    *,
    parar_no_destino: bool = True,
) -> _ResultadoBusca:
    validar_grafo(grafo)
    if origem not in grafo:
        raise KeyError(f"vértice de origem inexistente: {origem!r}")
    if destino is not None and destino not in grafo:
        raise KeyError(f"vértice de destino inexistente: {destino!r}")
    estimativas = _calcular_heuristica_consistente(grafo, destino, heuristica)
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
        if parar_no_destino and atual == destino:
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
    return _ResultadoBusca(distancias, anteriores, len(visitados))


def buscar(grafo: Grafo, origem: str) -> list[Peso]:
    resultado = _executar_busca(grafo, origem)
    return [resultado.distancias[vertice] for vertice in grafo]


def dijkstra(grafo: Grafo, origem: str) -> list[Peso]:
    return buscar(grafo, origem)


def dijkstra_com_caminho(
    grafo: Grafo, origem: str, destino: str
) -> tuple[Peso, list[str], int]:
    return a_estrela(grafo, origem, destino)


def a_estrela(
    grafo: Grafo,
    origem: str,
    destino: str,
    heuristica=None,
) -> tuple[Peso, list[str], int]:
    resultado = _executar_busca(grafo, origem, destino, heuristica)
    caminho = reconstruir_caminho(resultado.anteriores, origem, destino)
    return resultado.distancias[destino], caminho, resultado.vertices_expandidos


def a_estrela_distancias(
    grafo: Grafo,
    origem: str,
    destino: str,
    heuristica=None,
) -> list[Peso]:
    resultado = _executar_busca(
        grafo, origem, destino, heuristica, parar_no_destino=False
    )
    return [resultado.distancias[vertice] for vertice in grafo]
