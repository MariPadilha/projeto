"""Gera datasets e relatórios de seis cenários reproduzíveis."""

import argparse
import json
import platform
from pathlib import Path

from algoritmos import a_estrela, dijkstra_com_caminho
from avaliacao import avaliar
from dados import GerenciadorDeDados
from relatorios import exportar_relatorio


def executar_experimentos(
    pasta: Path, repeticoes: int = 7, semente: int = 42
) -> list[dict]:
    """Compara os mesmos pares de vértices; A* usa h=0 nestes grafos aleatórios."""
    if repeticoes < 1:
        raise ValueError("repetições deve ser um inteiro positivo")
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = []
    for quantidade in (10, 50, 100):
        for probabilidade in (0.1, 0.5):
            nome = f"grafo_{quantidade}_{int(probabilidade * 100)}.json"
            grafo = GerenciadorDeDados.aleatorio(quantidade, probabilidade, semente)
            GerenciadorDeDados.salvar(grafo, pasta / nome)
            medidas = avaliar(
                grafo,
                "0",
                str(quantidade - 1),
                {"dijkstra": dijkstra_com_caminho, "a_estrela": a_estrela},
                repeticoes,
            )
            for medida in medidas:
                medida.update(
                    {
                        "conjunto_dados": nome,
                        "semente": semente,
                        "probabilidade_aresta": probabilidade,
                        "heuristica": "zero",
                    }
                )
            resultados.extend(medidas)
    for extensao in ("json", "csv", "html"):
        exportar_relatorio(resultados, pasta / f"experimentos.{extensao}")
    ambiente = {
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "repeticoes": repeticoes,
        "semente": semente,
        "metodologia": "uma execução de aquecimento; mediana e desvio populacional; ordem alternada",
    }
    (pasta / "ambiente.json").write_text(
        json.dumps(ambiente, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return resultados


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(
        description="Experimentos com múltiplos datasets"
    )
    analisador.add_argument(
        "--saida", type=Path, default=Path("resultados/experimentos")
    )
    analisador.add_argument("--repeticoes", type=int, default=7)
    analisador.add_argument("--semente", type=int, default=42)
    argumentos = analisador.parse_args()
    try:
        medidas = executar_experimentos(
            argumentos.saida, argumentos.repeticoes, argumentos.semente
        )
    except (OSError, ValueError) as erro:
        analisador.exit(2, f"Erro: {erro}\n")
    print(f"{len(medidas)} avaliações salvas em {argumentos.saida}")
