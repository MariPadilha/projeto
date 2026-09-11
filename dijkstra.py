"""Interface obrigatória: distâncias de uma origem para todos os vértices."""

from algoritmos import buscar
from grafo import Grafo, Peso


def dijkstra(grafo: Grafo, origem: str) -> dict[str, Peso]:
    """Retorna todas as distâncias mínimas; infinito indica vértice inalcançável."""
    return buscar(grafo, origem).distancias
