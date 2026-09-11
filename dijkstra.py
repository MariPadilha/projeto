from math import inf

def dijkstra(grafo: dict[str, dict[str, float]], origem: str) -> dict[str, float]:
    if origem not in grafo:
        raise KeyError(f"vértice de origem inexistente: {origem!r}")

    distancias = {vertice: inf for vertice in grafo}
    visitados: set[str] = set()
    distancias[origem] = 0

    while len(visitados) < len(distancias):
        candidatos = (vertice for vertice in distancias if vertice not in visitados)
        atual = min(candidatos, key=distancias.__getitem__, default=None)

        if atual is None or distancias[atual] == inf:
            break

        visitados.add(atual)
        for vizinho, peso in grafo[atual].items():
            if peso < 0:
                raise ValueError("Dijkstra não aceita arestas com peso negativo")

            nova_distancia = distancias[atual] + peso
            if nova_distancia < distancias[vizinho]:
                distancias[vizinho] = nova_distancia

    return distancias
