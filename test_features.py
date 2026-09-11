import json

from algorithms import a_estrela, dijkstra_com_caminho
from datasets import GerenciadorDeDados
from evaluation import avaliar
from reports import exportar_relatorio


GRAPH = {"A": {"B": 4, "C": 1}, "B": {"D": 1}, "C": {"B": 2, "D": 5}, "D": {}}


def test_algoritmos_retornam_mesmo_caminho():
    assert dijkstra_com_caminho(GRAPH, "A", "D")[:2] == (4, ["A", "C", "B", "D"])
    assert a_estrela(GRAPH, "A", "D")[:2] == (4, ["A", "C", "B", "D"])


def test_dataset_e_relatorio(tmp_path):
    conjunto_dados = tmp_path / "grafo.json"
    conjunto_dados.write_text(json.dumps(GRAPH), encoding="utf-8")
    carregado = GerenciadorDeDados().carregar(conjunto_dados)
    resultados = avaliar(carregado, "A", "D", {"a_estrela": a_estrela})
    saida = tmp_path / "relatorio.csv"
    exportar_relatorio(resultados, saida)
    assert "a_estrela" in saida.read_text(encoding="utf-8")
