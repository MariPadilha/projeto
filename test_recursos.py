"""Testes de integração, formatos externos e regressões da revisão."""

import json
import math
import subprocess
import sys
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import networkx as nx
import pytest

from algoritmos import a_estrela, dijkstra_com_caminho
from avaliacao import avaliar
from dados import GerenciadorDeDados
from dijkstra import dijkstra
from relatorios import exportar_relatorio
from visualizacao import desenhar_comparacao, desenhar_grafo

GRAFO = {"A": {"B": 4, "C": 1}, "B": {"D": 1}, "C": {"B": 2, "D": 5}, "D": {}}
RAIZ = Path(__file__).parent


@pytest.mark.parametrize("algoritmo", [dijkstra_com_caminho, a_estrela])
def test_algoritmos_retornam_caminho_minimo(algoritmo):
    assert algoritmo(GRAFO, "A", "D")[:2] == (4, ["A", "C", "B", "D"])
    assert algoritmo({"A": {}, "B": {}}, "A", "B") == (math.inf, [], 1)
    assert algoritmo(GRAFO, "A", "A") == (0, ["A"], 1)


@pytest.mark.parametrize("peso", [-1, math.nan, math.inf, -math.inf, True, "2", None])
@pytest.mark.parametrize("consulta", ["completa", "mesma_origem", "destino"])
def test_rejeita_pesos_invalidos_inclusive_fora_da_busca(peso, consulta):
    grafo = {"A": {"B": 1}, "B": {}, "C": {"D": peso}, "D": {}}
    with pytest.raises(ValueError):
        if consulta == "completa":
            dijkstra(grafo, "A")
        else:
            a_estrela(grafo, "A", "A" if consulta == "mesma_origem" else "B")


def test_restricoes_estrutura_e_estouro():
    for grafo in [[], {"A": []}, {"A": {"B": 1}}, {1: {}}, {"": {}}]:
        with pytest.raises(ValueError):
            dijkstra(grafo, "A")
    with pytest.raises(KeyError):
        a_estrela(GRAFO, "A", "Z")
    with pytest.raises(ValueError, match="ponto flutuante"):
        dijkstra({"A": {"B": 1e308}, "B": {"C": 1e308}, "C": {}}, "A")
    inteiro_grande = 10**400
    assert dijkstra({"A": {"B": inteiro_grande}, "B": {}}, "A")["B"] == inteiro_grande


def test_nao_modifica_entrada_e_aceita_zero_lacos_ciclos():
    grafo = {"A": {"A": 0, "B": 0}, "B": {"A": 0, "C": 2.5}, "C": {}, "D": {}}
    copia = deepcopy(grafo)
    assert dijkstra(grafo, "A") == {"A": 0, "B": 0, "C": 2.5, "D": math.inf}
    assert a_estrela(grafo, "A", "C")[:2] == (2.5, ["A", "B", "C"])
    assert grafo == copia


def test_heuristica_consistente_reduz_vertices_fixados():
    grafo = GerenciadorDeDados().carregar(RAIZ / "exemplos/desvios.json")
    estimativas = json.loads((RAIZ / "exemplos/heuristica_desvios.json").read_text())
    resposta = a_estrela(grafo, "A", "D", lambda vertice, _: estimativas[vertice])
    assert resposta == (4, ["A", "C", "D"], 3)
    assert dijkstra_com_caminho(grafo, "A", "D")[2] == 4


@pytest.mark.parametrize(
    "estimativas",
    [
        {"A": 4, "B": 0, "C": 3, "D": 0},  # Admissível, mas inconsistente.
        {"A": 0, "B": 0, "C": 0, "D": 1},
        {"A": math.nan, "B": 0, "C": 0, "D": 0},
    ],
)
def test_rejeita_heuristica_invalida(estimativas):
    with pytest.raises(ValueError):
        a_estrela(GRAFO, "A", "D", lambda vertice, _: estimativas[vertice])


@pytest.mark.parametrize("semente", range(12))
def test_resultados_conferem_com_bellman_ford_independente(semente):
    grafo = GerenciadorDeDados.aleatorio(9, semente / 12, semente)
    rede = nx.DiGraph()
    rede.add_nodes_from(grafo)
    for origem, vizinhos in grafo.items():
        for destino, peso in vizinhos.items():
            rede.add_edge(origem, destino, weight=peso)
    for origem in grafo:
        referencia = nx.single_source_bellman_ford_path_length(rede, origem)
        esperado = {vertice: referencia.get(vertice, math.inf) for vertice in grafo}
        assert dijkstra(grafo, origem) == esperado
        for destino in grafo:
            for algoritmo in (a_estrela, dijkstra_com_caminho):
                distancia, caminho, expandidos = algoritmo(grafo, origem, destino)
                assert distancia == esperado[destino]
                assert 1 <= expandidos <= len(grafo)
                if caminho:
                    assert caminho[0] == origem and caminho[-1] == destino
                    assert sum(grafo[a][b] for a, b in pairwise(caminho)) == distancia
                else:
                    assert distancia == math.inf


@pytest.mark.parametrize("extensao", ["json", "csv"])
def test_dataset_ida_e_volta_preserva_isolados(tmp_path, extensao):
    grafo = {**GRAFO, "isolado": {}}
    copia = deepcopy(grafo)
    caminho = tmp_path / f"grafo.{extensao}"
    GerenciadorDeDados.salvar(grafo, caminho)
    assert GerenciadorDeDados().carregar(caminho) == grafo
    assert grafo == copia


@pytest.mark.parametrize(
    "conteudo",
    [
        "origem,destino,peso\nA,B,-1\n",
        "origem,destino,peso\nA,B,nan\n",
        "origem,destino,peso\nA,B,1\nA,B,2\n",
        "origem,destino,peso\nA,B\n",
        "origem,destino,peso\nA,B,1,extra\n",
        "origem,destino,peso\n,B,1\n",
        "origem,destino,peso\nA,B,\n",
        "coluna_errada\nA\n",
    ],
)
def test_rejeita_csv_invalido(tmp_path, conteudo):
    caminho = tmp_path / "invalido.csv"
    caminho.write_text(conteudo, encoding="utf-8")
    with pytest.raises(ValueError):
        GerenciadorDeDados().carregar(caminho)


def test_compatibilidade_e_destinos_implicitos(tmp_path):
    caminho = tmp_path / "grafo.json"
    for dados in (
        {"A": {"B": 1}},
        {"grafo": {"A": {"B": 1}}},
        {"graph": {"A": {"B": 1}}},
    ):
        caminho.write_text(json.dumps(dados), encoding="utf-8")
        assert GerenciadorDeDados().carregar(caminho) == {"A": {"B": 1}, "B": {}}
    caminho = tmp_path / "grafo.csv"
    caminho.write_text("source,target,weight\nA,B,1\n", encoding="utf-8")
    assert GerenciadorDeDados().carregar(caminho) == {"A": {"B": 1}, "B": {}}


def test_rejeita_chaves_duplicadas_json(tmp_path):
    caminho = tmp_path / "duplicado.json"
    caminho.write_text('{"A": {"B": 1, "B": 2}, "B": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicada"):
        GerenciadorDeDados().carregar(caminho)


def test_geracao_reproduzivel_e_limites():
    assert GerenciadorDeDados.aleatorio(10, 0.3, 42) == GerenciadorDeDados.aleatorio(
        10, 0.3, 42
    )
    assert GerenciadorDeDados.aleatorio(2, 0) == {"0": {}, "1": {}}
    assert sum(map(len, GerenciadorDeDados.aleatorio(3, 1).values())) == 6
    for quantidade, probabilidade in [
        (0, 0.2),
        (1.5, 0.2),
        (True, 0.2),
        (2, math.nan),
        (2, 1.1),
    ]:
        with pytest.raises(ValueError):
            GerenciadorDeDados.aleatorio(quantidade, probabilidade)


def test_metricas_e_repeticoes():
    resultados = avaliar(GRAFO, "A", "D", {"dijkstra": dijkstra_com_caminho}, 3)
    resultado = resultados[0]
    assert resultado["distancia"] == 4
    assert resultado["vertices"] == 4 and resultado["arestas"] == 5
    assert resultado["repeticoes"] == 3 and resultado["arestas_caminho"] == 3
    assert resultado["tempo_execucao_ms"] >= 0 and resultado["desvio_tempo_ms"] >= 0
    with pytest.raises(ValueError):
        avaliar(GRAFO, "A", "D", {}, 0)


@pytest.mark.parametrize("extensao", ["json", "csv", "html"])
def test_relatorios_inalcancaveis_e_escape_html(tmp_path, extensao):
    resultados = avaliar(
        {"A": {}, "<script>": {}},
        "A",
        "<script>",
        {"dijkstra": dijkstra_com_caminho},
        1,
    )
    saida = tmp_path / f"relatorio.{extensao}"
    exportar_relatorio(resultados, saida)
    texto = saida.read_text(encoding="utf-8")
    assert "Infinity" not in texto
    if extensao == "json":
        assert json.loads(texto)[0]["distancia"] is None
    elif extensao == "html":
        assert "<script>" not in texto and "&lt;script&gt;" in texto
    else:
        assert "inalcançável" in texto
    assert resultados[0]["distancia"] == math.inf


def test_visualizacao_preserva_isolados_e_fecha_figuras(tmp_path, monkeypatch):
    import matplotlib.pyplot as plt

    redes = []
    desenhar_original = nx.draw

    def registrar_rede(rede, *argumentos, **opcoes):
        redes.append(set(rede.nodes))
        return desenhar_original(rede, *argumentos, **opcoes)

    monkeypatch.setattr(nx, "draw", registrar_rede)
    grafo = {**GRAFO, "isolado": {}}
    saida = tmp_path / "grafo.png"
    desenhar_grafo(grafo, ["A", "C", "B", "D"], saida)
    assert redes == [set(grafo)]
    assert saida.read_bytes().startswith(b"\x89PNG")
    resultados = avaliar(grafo, "A", "isolado", {"dijkstra": dijkstra_com_caminho}, 1)
    desenhar_comparacao(resultados, tmp_path / "comparacao.png")
    assert not plt.get_fignums()


def test_terminal_fonte_unica_comparacao_e_erro(tmp_path):
    def executar(*argumentos):
        return subprocess.run(
            [sys.executable, str(RAIZ / "main.py"), *map(str, argumentos)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            check=False,
        )

    saida = tmp_path / "distancias.json"
    resultado = executar(RAIZ / "grafo.json", "0", "--relatorio", saida)
    assert resultado.returncode == 0, resultado.stderr
    distancias = {
        linha["destino"]: linha["distancia"] for linha in json.loads(saida.read_text())
    }
    assert distancias == {
        "0": 0,
        "1": 2,
        "2": 5,
        "3": 1,
        "4": 4,
        "5": 5,
        "6": 5,
        "7": 8,
        "8": 10,
        "9": 9,
    }
    resultado = executar(
        RAIZ / "exemplos/desvios.json",
        "A",
        "D",
        "--heuristica",
        RAIZ / "exemplos/heuristica_desvios.json",
        "--relatorio",
        saida,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert [
        linha["vertices_expandidos"] for linha in json.loads(saida.read_text())
    ] == [4, 3]
    resultado = executar(RAIZ / "grafo.json", "ausente", "--relatorio", saida)
    assert resultado.returncode == 2 and "Erro:" in resultado.stderr
    assert "Traceback" not in resultado.stderr


def test_experimentos_geram_seis_datasets_e_tres_relatorios(tmp_path):
    from experimentos import executar_experimentos

    resultados = executar_experimentos(tmp_path, repeticoes=1)
    assert len(resultados) == 12
    assert len(list(tmp_path.glob("grafo_*.json"))) == 6
    for indice in range(0, 12, 2):
        assert resultados[indice]["distancia"] == resultados[indice + 1]["distancia"]
    for extensao in ("json", "csv", "html"):
        assert (tmp_path / f"experimentos.{extensao}").stat().st_size > 0
