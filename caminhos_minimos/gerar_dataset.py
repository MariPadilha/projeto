import argparse
from pathlib import Path
from random import Random

from caminhos_minimos.grafo import Grafo
from caminhos_minimos.ler_salvar_grafos import salvar_grafo


def gerar_grafo_aleatorio(
    quantidade_vertices: int,
    probabilidade_aresta: float = 0.2,
    semente: int | None = 0,
) -> Grafo:
    if (
        isinstance(quantidade_vertices, bool)
        or not isinstance(quantidade_vertices, int)
        or quantidade_vertices < 1
    ):
        raise ValueError("quantidade deve ser um inteiro positivo")
    if (
        isinstance(probabilidade_aresta, bool)
        or not isinstance(probabilidade_aresta, (int, float))
        or not 0 <= probabilidade_aresta <= 1
    ):
        raise ValueError("a probabilidade deve estar entre 0 e 1")
    gerador = Random(semente)
    grafo: Grafo = {str(indice): {} for indice in range(quantidade_vertices)}
    for origem in grafo:
        for destino in grafo:
            if origem != destino and gerador.random() < probabilidade_aresta:
                grafo[origem][destino] = gerador.randint(1, 100)
    return grafo


def gerar_dataset(pasta_saida: Path, semente: int = 42) -> list[Path]:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivos_gerados = []
    for quantidade_vertices in (10, 50, 100):
        for probabilidade_aresta in (0.1, 0.5):
            nome_arquivo_grafo = (
                f"grafo_{quantidade_vertices}_{int(probabilidade_aresta * 100)}.json"
            )
            grafo_aleatorio = gerar_grafo_aleatorio(
                quantidade_vertices, probabilidade_aresta, semente
            )
            caminho_grafo = pasta_saida / nome_arquivo_grafo
            salvar_grafo(grafo_aleatorio, caminho_grafo)
            arquivos_gerados.append(caminho_grafo)
    return arquivos_gerados


if __name__ == "__main__":
    analisador_argumentos = argparse.ArgumentParser(
        description="Gera e salva datasets de grafos aleatórios em JSON"
    )
    analisador_argumentos.add_argument(
        "--saida", type=Path, default=Path("resultados/datasets")
    )
    analisador_argumentos.add_argument("--semente", type=int, default=42)
    argumentos = analisador_argumentos.parse_args()
    try:
        arquivos_gerados = gerar_dataset(argumentos.saida, argumentos.semente)
    except (OSError, ValueError) as erro:
        analisador_argumentos.exit(2, f"Erro: {erro}\n")
    print(f"{len(arquivos_gerados)} datasets salvos em {argumentos.saida}")
