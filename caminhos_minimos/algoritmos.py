from caminhos_minimos._busca import _executar_busca, reconstruir_caminho
from caminhos_minimos.grafo import Grafo, Peso


def buscar(grafo: Grafo, origem: str) -> list[Peso]:
    resultado = _executar_busca(grafo, origem)
    return [resultado.distancias[vertice] for vertice in grafo]


def dijkstra(grafo: Grafo, origem: str) -> list[Peso]:
    return buscar(grafo, origem)


def dijkstra_com_caminho(
    grafo: Grafo, origem: str, destino: str
) -> tuple[Peso, list[str], int]:
    resultado = _executar_busca(grafo, origem, destino)
    caminho = reconstruir_caminho(resultado.anteriores, origem, destino)
    return resultado.distancias[destino], caminho, resultado.vertices_expandidos
