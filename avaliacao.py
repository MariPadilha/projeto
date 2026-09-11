"""Métricas de consultas origem-destino sob as mesmas condições de execução."""

from statistics import median, pstdev
from time import perf_counter
from typing import Any

from algoritmos import Algoritmo
from complexidade import resumo_complexidade
from grafo import Grafo


def avaliar(
    grafo: Grafo,
    origem: str,
    destino: str,
    algoritmos: dict[str, Algoritmo],
    repeticoes: int = 7,
) -> list[dict[str, Any]]:
    """Mede mediana/desvio dos tempos; inclui validação, exclui leitura e gráficos."""
    if (
        isinstance(repeticoes, bool)
        or not isinstance(repeticoes, int)
        or repeticoes < 1
    ):
        raise ValueError("repetições deve ser um inteiro positivo")
    vertices = len(grafo)
    arestas = sum(len(vizinhos) for vizinhos in grafo.values())
    complexidades = resumo_complexidade(vertices, arestas)
    tempos: dict[str, list[float]] = {nome: [] for nome in algoritmos}
    respostas = {}
    for nome, algoritmo in algoritmos.items():
        respostas[nome] = algoritmo(grafo, origem, destino)  # Aquecimento.
    for repeticao in range(repeticoes):
        ordem = list(algoritmos)
        if repeticao % 2:
            ordem.reverse()
        for nome in ordem:
            inicio = perf_counter()
            resposta = algoritmos[nome](grafo, origem, destino)
            tempos[nome].append((perf_counter() - inicio) * 1000)
            if resposta != respostas[nome]:
                raise ValueError(
                    f"o algoritmo {nome!r} produziu resultados inconsistentes"
                )
    resultados = []
    for nome, (distancia, caminho, expandidos) in respostas.items():
        resultados.append(
            {
                "algoritmo": nome,
                "origem": origem,
                "destino": destino,
                "distancia": distancia,
                "caminho": caminho,
                "alcancavel": bool(caminho),
                "arestas_caminho": max(0, len(caminho) - 1),
                "vertices_expandidos": expandidos,
                "tempo_execucao_ms": median(tempos[nome]),
                "desvio_tempo_ms": pstdev(tempos[nome]),
                "repeticoes": repeticoes,
                "vertices": vertices,
                "arestas": arestas,
                "complexidade": complexidades.get(nome, "não informada"),
            }
        )
    return resultados
