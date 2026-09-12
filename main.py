import argparse
import json
from functools import partial
from math import inf
from pathlib import Path

from caminhos_minimos.algoritmos import (
    dijkstra,
    dijkstra_com_caminho,
)
from caminhos_minimos.ler_salvar_grafos import carregar_grafo
from complementos.avaliacao import avaliar
from complementos.relatorios import exportar_relatorio


def criar_analisador() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(description="Caminhos mínimos de fonte única")
    analisador.add_argument("conjunto_dados", help="arquivo .json ou .csv")
    analisador.add_argument("origem", help="vértice de origem")
    analisador.add_argument(
        "destino",
        nargs="?",
        help="destino da heurística para comparar vetores completos com A*",
    )
    analisador.add_argument(
        "--relatorio", "--report", default="resultados/relatorio.json"
    )
    analisador.add_argument(
        "--grafico", "--plot", help="imagem do grafo, por exemplo grafo.png"
    )
    analisador.add_argument(
        "--comparacao", help="imagem dos tempos de cálculo do vetor completo"
    )
    analisador.add_argument("--repeticoes", type=int, default=7)
    analisador.add_argument(
        "--heuristica", help="JSON com estimativas de cada vértice ao destino"
    )
    return analisador


def executar(argumentos: argparse.Namespace) -> None:
    grafo = carregar_grafo(argumentos.conjunto_dados)
    if argumentos.destino is None and argumentos.heuristica:
        raise ValueError("--heuristica exige um destino")
    if argumentos.repeticoes < 1:
        raise ValueError("repetições deve ser um inteiro positivo")
    caminho = None
    algoritmos = {"dijkstra": dijkstra}
    if argumentos.destino is not None:
        from complementos.a_estrela import a_estrela_distancias

        algoritmo_a_estrela = partial(a_estrela_distancias, destino=argumentos.destino)
        if argumentos.heuristica:
            estimativas = json.loads(
                Path(argumentos.heuristica).read_text(encoding="utf-8")
            )
            if not isinstance(estimativas, dict) or set(estimativas) != set(grafo):
                raise ValueError(
                    "a heurística deve informar exatamente os vértices do grafo"
                )
            algoritmo_a_estrela = partial(
                algoritmo_a_estrela,
                heuristica=lambda vertice, _destino: estimativas[vertice],
            )
        algoritmos["a_estrela"] = algoritmo_a_estrela
    resultados = avaliar(grafo, argumentos.origem, algoritmos, argumentos.repeticoes)
    vetor_distancias = resultados[0]["distancias"]
    distancias = dict(zip(grafo, vetor_distancias))
    for resultado in resultados:
        if resultado["distancias"] != vetor_distancias:
            raise ValueError(
                "a comparação divergiu do vetor de distâncias de fonte única"
            )
        if resultado["algoritmo"] == "a_estrela":
            resultado["destino_heuristica"] = argumentos.destino
            resultado["heuristica"] = argumentos.heuristica or "zero"
        resultado["conjunto_dados"] = str(argumentos.conjunto_dados)
    Path(argumentos.relatorio).parent.mkdir(parents=True, exist_ok=True)
    exportar_relatorio(resultados, argumentos.relatorio)
    if argumentos.grafico:
        from complementos.visualizacao import desenhar_grafo

        if argumentos.destino is not None:
            _, caminho, _ = dijkstra_com_caminho(
                grafo, argumentos.origem, argumentos.destino
            )
        desenhar_grafo(grafo, caminho, argumentos.grafico)
    if argumentos.comparacao:
        from complementos.visualizacao import desenhar_comparacao

        desenhar_comparacao(resultados, argumentos.comparacao)
    print(f"Distâncias mínimas a partir de {argumentos.origem}:")
    print(f"Vértices: {list(grafo)}")
    print(f"Vetor de distâncias: {vetor_distancias}")
    for vertice, distancia in distancias.items():
        print(
            f"{argumentos.origem} → {vertice}: {distancia if distancia != inf else 'inalcançável'}"
        )
    for resultado in resultados:
        print(
            f"{resultado['algoritmo']}: vetor completo, "
            f"tempo mediano={resultado['tempo_execucao_ms']:.6f} ms, "
            f"desvio={resultado['desvio_tempo_ms']:.6f} ms"
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
