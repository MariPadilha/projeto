from caminhos_minimos._busca import _executar_busca, reconstruir_caminho
from caminhos_minimos.grafo import Grafo, Peso


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
