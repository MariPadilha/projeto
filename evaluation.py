from __future__ import annotations

from time import perf_counter
from typing import Any, Callable

from complexity import resumo_complexidade


def avaliar(grafo: dict, origem: Any, destino: Any, algoritmos: dict[str, Callable]) -> list[dict[str, Any]]:
    resultados = []
    vertices = len(grafo)
    arestas = sum(len(vizinhos) for vizinhos in grafo.values())
    complexidades = resumo_complexidade(vertices, arestas)
    for nome, algoritmo in algoritmos.items():
        inicio = perf_counter()
        distancia, caminho, expandidos = algoritmo(grafo, origem, destino)
        tempo_decorrido = (perf_counter() - inicio) * 1000
        resultados.append({
            "algoritmo": nome,
            "distancia": distancia,
            "caminho": caminho,
            "alcancavel": bool(caminho),
            "vertices_expandidos": expandidos,
            "tempo_execucao_ms": round(tempo_decorrido, 4),
            "vertices": vertices,
            "arestas": arestas,
            "complexidade": complexidades.get(nome, "não informada"),
        })
    return resultados
