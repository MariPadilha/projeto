"""Entrada de terminal para fonte única e comparação opcional com A*."""

import argparse
import json
from functools import partial
from math import inf
from pathlib import Path

from algoritmos import a_estrela, dijkstra_com_caminho
from avaliacao import avaliar
from dados import GerenciadorDeDados
from dijkstra import dijkstra
from relatorios import exportar_relatorio


def criar_analisador() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(description="Caminhos mínimos de fonte única")
    analisador.add_argument("conjunto_dados", help="arquivo .json ou .csv")
    analisador.add_argument("origem", help="vértice de origem")
    analisador.add_argument(
        "destino", nargs="?", help="destino opcional para comparar com A*"
    )
    analisador.add_argument("--relatorio", "--report", default="relatorio.json")
    analisador.add_argument(
        "--grafico", "--plot", help="imagem do grafo, por exemplo grafo.png"
    )
    analisador.add_argument("--comparacao", help="imagem das métricas; exige destino")
    analisador.add_argument("--repeticoes", type=int, default=7)
    analisador.add_argument(
        "--heuristica", help="JSON com estimativas de cada vértice ao destino"
    )
    return analisador


def executar(argumentos: argparse.Namespace) -> None:
    grafo = GerenciadorDeDados().carregar(argumentos.conjunto_dados)
    if argumentos.destino is None and (argumentos.heuristica or argumentos.comparacao):
        raise ValueError("--heuristica e --comparacao exigem um destino")
    if argumentos.repeticoes < 1:
        raise ValueError("repetições deve ser um inteiro positivo")
    distancias = dijkstra(grafo, argumentos.origem)
    caminho = None
    if argumentos.destino is None:
        resultados = [
            {
                "algoritmo": "dijkstra",
                "origem": argumentos.origem,
                "destino": vertice,
                "distancia": distancia,
                "alcancavel": distancia != inf,
            }
            for vertice, distancia in distancias.items()
        ]
    else:
        algoritmo_a_estrela = a_estrela
        if argumentos.heuristica:
            estimativas = json.loads(
                Path(argumentos.heuristica).read_text(encoding="utf-8")
            )
            if not isinstance(estimativas, dict) or set(estimativas) != set(grafo):
                raise ValueError(
                    "a heurística deve informar exatamente os vértices do grafo"
                )
            algoritmo_a_estrela = partial(
                a_estrela, heuristica=lambda vertice, _destino: estimativas[vertice]
            )
        algoritmos = {
            "dijkstra": dijkstra_com_caminho,
            "a_estrela": algoritmo_a_estrela,
        }
        resultados = avaliar(
            grafo,
            argumentos.origem,
            argumentos.destino,
            algoritmos,
            argumentos.repeticoes,
        )
        for resultado in resultados:
            if resultado["distancia"] != distancias[argumentos.destino]:
                raise ValueError("a comparação divergiu do resultado de fonte única")
            resultado["heuristica"] = (
                (argumentos.heuristica or "zero")
                if resultado["algoritmo"] == "a_estrela"
                else "não se aplica"
            )
        caminho = resultados[0]["caminho"]
    for resultado in resultados:
        resultado["conjunto_dados"] = str(argumentos.conjunto_dados)
    exportar_relatorio(resultados, argumentos.relatorio)
    if argumentos.grafico:
        from visualizacao import desenhar_grafo

        desenhar_grafo(grafo, caminho, argumentos.grafico)
    if argumentos.comparacao:
        from visualizacao import desenhar_comparacao

        desenhar_comparacao(resultados, argumentos.comparacao)
    print(f"Distâncias mínimas a partir de {argumentos.origem}:")
    for vertice, distancia in distancias.items():
        print(
            f"{argumentos.origem} → {vertice}: {distancia if distancia != inf else 'inalcançável'}"
        )
    if argumentos.destino is not None:
        for resultado in resultados:
            print(
                f"{resultado['algoritmo']}: distância={resultado['distancia']}, "
                f"tempo mediano={resultado['tempo_execucao_ms']:.6f} ms, "
                f"vértices fixados={resultado['vertices_expandidos']}"
            )
    print(f"Relatório salvo em {argumentos.relatorio}")


def principal() -> None:
    analisador = criar_analisador()
    try:
        executar(analisador.parse_args())
    except (OSError, ValueError, KeyError, RuntimeError) as erro:
        analisador.exit(2, f"Erro: {erro}\n")


if __name__ == "__main__":
    principal()
