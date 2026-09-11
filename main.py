import argparse

from algorithms import a_estrela, dijkstra_com_caminho
from datasets import GerenciadorDeDados
from evaluation import avaliar
from reports import exportar_relatorio


def criar_analisador() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(description="Experimentos de caminhos mínimos")
    analisador.add_argument("conjunto_dados", help="arquivo .json ou .csv")
    analisador.add_argument("origem")
    analisador.add_argument("destino")
    analisador.add_argument("--report", "--relatorio", dest="relatorio", default="report.json")
    analisador.add_argument("--plot", "--grafico", dest="grafico")
    return analisador


def executar(argumentos: argparse.Namespace) -> None:
    grafo = GerenciadorDeDados().carregar(argumentos.conjunto_dados)
    algoritmos = {"dijkstra": dijkstra_com_caminho, "a_estrela": a_estrela}
    resultados = avaliar(grafo, argumentos.origem, argumentos.destino, algoritmos)
    exportar_relatorio(resultados, argumentos.relatorio)
    if argumentos.grafico:
        from visualization import desenhar_grafo

        desenhar_grafo(grafo, resultados[0]["caminho"], argumentos.grafico)
    for resultado in resultados:
        print(
            f"{resultado['algoritmo']}: distância={resultado['distancia']}, "
            f"tempo={resultado['tempo_execucao_ms']} ms"
        )


def main() -> None:
    executar(criar_analisador().parse_args())


if __name__ == "__main__":
    main()
