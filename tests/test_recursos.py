import json
import math
import subprocess
import sys
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import networkx as nx
import pytest

from caminhos_minimos.algoritmos import (
    a_estrela,
    a_estrela_distancias,
    dijkstra,
    dijkstra_com_caminho,
)
from caminhos_minimos.avaliacao import avaliar
from caminhos_minimos.gerar_dataset import gerar_grafo_aleatorio
from caminhos_minimos.ler_salvar_grafos import carregar_grafo, salvar_grafo
from caminhos_minimos.relatorios import exportar_relatorio
from caminhos_minimos.visualizacao import desenhar_comparacao, desenhar_grafo

GRAFO = {"A": {"B": 4, "C": 1}, "B": {"D": 1}, "C": {"B": 2, "D": 5}, "D": {}}
RAIZ = Path(__file__).resolve().parents[1]


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
    assert dijkstra({"A": {"B": inteiro_grande}, "B": {}}, "A")[1] == inteiro_grande


def test_nao_modifica_entrada_e_aceita_zero_lacos_ciclos():
    grafo = {"A": {"A": 0, "B": 0}, "B": {"A": 0, "C": 2.5}, "C": {}, "D": {}}
    copia = deepcopy(grafo)
    assert dijkstra(grafo, "A") == [0, 0, 2.5, math.inf]
    assert a_estrela(grafo, "A", "C")[:2] == (2.5, ["A", "B", "C"])
    assert grafo == copia


def test_heuristica_consistente_reduz_vertices_fixados():
    grafo = carregar_grafo(RAIZ / "exemplos/desvios.json")
    estimativas = json.loads((RAIZ / "exemplos/heuristica_desvios.json").read_text())
    resposta = a_estrela(grafo, "A", "D", lambda vertice, _: estimativas[vertice])
    assert resposta == (4, ["A", "C", "D"], 3)
    assert dijkstra_com_caminho(grafo, "A", "D")[2] == 4


def test_a_estrela_vetor_completo_continua_apos_destino():
    grafo = {
        "isolado": {},
        "A": {"B": 1, "C": 9},
        "B": {"C": 1},
        "C": {"D": 1},
        "D": {},
    }
    estimativas = {"isolado": 0, "A": 1, "B": 0, "C": 0, "D": 0}
    assert a_estrela_distancias(
        grafo, "A", "B", lambda vertice, _: estimativas[vertice]
    ) == [math.inf, 0, 1, 2, 3]
    assert a_estrela_distancias(grafo, "A", "A") == [math.inf, 0, 1, 2, 3]


@pytest.mark.parametrize(
    "estimativas",
    [
        pytest.param(
            {"A": 4, "B": 0, "C": 3, "D": 0}, id="admissivel_mas_inconsistente"
        ),
        pytest.param(
            {"A": 0, "B": 0, "C": 0, "D": 1}, id="destino_com_estimativa_nao_nula"
        ),
        pytest.param(
            {"A": math.nan, "B": 0, "C": 0, "D": 0}, id="estimativa_nao_finita"
        ),
    ],
)
def test_rejeita_heuristica_invalida(estimativas):
    with pytest.raises(ValueError):
        a_estrela(GRAFO, "A", "D", lambda vertice, _: estimativas[vertice])


@pytest.mark.parametrize("semente", range(12))
def test_resultados_conferem_com_bellman_ford_independente(semente):
    grafo = gerar_grafo_aleatorio(9, semente / 12, semente)
    rede = nx.DiGraph()
    rede.add_nodes_from(grafo)
    for origem, vizinhos in grafo.items():
        for destino, peso in vizinhos.items():
            rede.add_edge(origem, destino, weight=peso)
    for origem in grafo:
        referencia = nx.single_source_bellman_ford_path_length(rede, origem)
        esperado = {vertice: referencia.get(vertice, math.inf) for vertice in grafo}
        assert dijkstra(grafo, origem) == [esperado[vertice] for vertice in grafo]
        for destino in grafo:
            assert a_estrela_distancias(grafo, origem, destino) == list(
                esperado.values()
            )
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
    salvar_grafo(grafo, caminho)
    assert carregar_grafo(caminho) == grafo
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
        carregar_grafo(caminho)


def test_compatibilidade_e_destinos_implicitos(tmp_path):
    caminho = tmp_path / "grafo.json"
    for dados in (
        {"A": {"B": 1}},
        {"grafo": {"A": {"B": 1}}},
        {"graph": {"A": {"B": 1}}},
    ):
        caminho.write_text(json.dumps(dados), encoding="utf-8")
        assert carregar_grafo(caminho) == {"A": {"B": 1}, "B": {}}
    caminho = tmp_path / "grafo.csv"
    caminho.write_text("source,target,weight\nA,B,1\n", encoding="utf-8")
    assert carregar_grafo(caminho) == {"A": {"B": 1}, "B": {}}


def test_rejeita_chaves_duplicadas_json(tmp_path):
    caminho = tmp_path / "duplicado.json"
    caminho.write_text('{"A": {"B": 1, "B": 2}, "B": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicada"):
        carregar_grafo(caminho)


def test_geracao_reproduzivel_e_limites():
    assert gerar_grafo_aleatorio(10, 0.3, 42) == gerar_grafo_aleatorio(10, 0.3, 42)
    assert gerar_grafo_aleatorio(2, 0) == {"0": {}, "1": {}}
    assert sum(map(len, gerar_grafo_aleatorio(3, 1).values())) == 6
    for quantidade, probabilidade in [
        (0, 0.2),
        (1.5, 0.2),
        (True, 0.2),
        (2, math.nan),
        (2, 1.1),
    ]:
        with pytest.raises(ValueError):
            gerar_grafo_aleatorio(quantidade, probabilidade)


def test_metricas_e_repeticoes():
    resultados = avaliar(GRAFO, "A", {"dijkstra": dijkstra}, 3)
    resultado = resultados[0]
    assert resultado["ordem_vertices"] == ["A", "B", "C", "D"]
    assert resultado["distancias"] == [0, 3, 1, 4]
    assert resultado["vertices"] == 4 and resultado["arestas"] == 5
    assert resultado["repeticoes"] == 3
    assert resultado["tempo_execucao_ms"] >= 0 and resultado["desvio_tempo_ms"] >= 0
    with pytest.raises(ValueError):
        avaliar(GRAFO, "A", {}, 0)


def test_avaliacao_mede_vetor_completo_com_aquecimento_e_ordem_alternada(monkeypatch):
    chamadas = []

    def primeiro(grafo, origem):
        chamadas.append("primeiro")
        return dijkstra(grafo, origem)

    def segundo(grafo, origem):
        chamadas.append("segundo")
        return dijkstra(grafo, origem)

    instantes = iter([0, 0.001, 1, 1.002, 2, 2.004, 3, 3.003, 4, 4.005, 5, 5.006])
    monkeypatch.setattr(
        "caminhos_minimos.avaliacao.perf_counter", lambda: next(instantes)
    )
    resultados = avaliar(GRAFO, "A", {"primeiro": primeiro, "segundo": segundo}, 3)
    chamadas_aquecimento = ["primeiro", "segundo"]
    chamadas_medidas = [
        "primeiro",
        "segundo",
        "segundo",
        "primeiro",
        "primeiro",
        "segundo",
    ]
    assert chamadas == chamadas_aquecimento + chamadas_medidas
    assert [
        resultado["tempo_execucao_ms"] for resultado in resultados
    ] == pytest.approx([3, 4])
    assert [resultado["desvio_tempo_ms"] for resultado in resultados] == pytest.approx(
        [math.sqrt(8 / 3), math.sqrt(8 / 3)]
    )


@pytest.mark.parametrize("resposta", [[0], (0, ["A"], 1)])
def test_avaliacao_rejeita_resposta_que_nao_e_vetor_completo(resposta):
    with pytest.raises(ValueError, match="vetor com 4 distâncias"):
        avaliar(GRAFO, "A", {"invalido": lambda grafo, origem: resposta}, 1)


def test_avaliacao_detecta_vetor_mutavel_inconsistente():
    vetor = [0, 3, 1, 4]

    def inconsistente(grafo, origem):
        vetor[-1] += 1
        return vetor

    with pytest.raises(ValueError, match="inconsistentes"):
        avaliar(GRAFO, "A", {"inconsistente": inconsistente}, 2)


@pytest.mark.parametrize("extensao", ["json", "csv", "html"])
def test_relatorios_inalcancaveis_e_escape_html(tmp_path, extensao):
    resultados = avaliar(
        {"A": {}, "<script>": {}},
        "A",
        {"dijkstra": dijkstra},
        1,
    )
    saida = tmp_path / f"relatorio.{extensao}"
    exportar_relatorio(resultados, saida)
    texto = saida.read_text(encoding="utf-8")
    assert "Infinity" not in texto
    if extensao == "json":
        assert json.loads(texto)[0]["distancias"] == [0, None]
    elif extensao == "html":
        assert "<script>" not in texto and "&lt;script&gt;" in texto
    else:
        assert "inalcançável" in texto
    assert resultados[0]["distancias"] == [0, math.inf]


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
    resultados = avaliar(grafo, "A", {"dijkstra": dijkstra}, 1)
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
    resultado = executar(RAIZ / "exemplos/grafo.json", "0", "--relatorio", saida)
    assert resultado.returncode == 0, resultado.stderr
    assert "Vetor de distâncias: [0, 2, 5, 1, 4, 5, 5, 8, 10, 9]" in resultado.stdout
    relatorio = json.loads(saida.read_text())
    assert len(relatorio) == 1
    assert relatorio[0]["repeticoes"] == 7
    assert relatorio[0]["tempo_execucao_ms"] >= 0
    distancias = dict(zip(relatorio[0]["ordem_vertices"], relatorio[0]["distancias"]))
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
        "--repeticoes",
        "3",
        "--grafico",
        tmp_path / "caminho.png",
        "--comparacao",
        tmp_path / "comparacao.png",
    )
    assert resultado.returncode == 0, resultado.stderr
    relatorio = json.loads(saida.read_text())
    assert [linha["algoritmo"] for linha in relatorio] == ["dijkstra", "a_estrela"]
    assert relatorio[0]["distancias"] == relatorio[1]["distancias"]
    grafo = carregar_grafo(RAIZ / "exemplos/desvios.json")
    assert relatorio[0]["distancias"] == dijkstra(grafo, "A")
    assert relatorio[1]["destino_heuristica"] == "D"
    assert all(linha["repeticoes"] == 3 for linha in relatorio)
    assert (tmp_path / "caminho.png").read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "comparacao.png").read_bytes().startswith(b"\x89PNG")
    imagem = tmp_path / "metricas.png"
    resultado = executar(RAIZ / "exemplos/grafo.json", "0", "--comparacao", imagem)
    assert resultado.returncode == 0, resultado.stderr
    assert imagem.read_bytes().startswith(b"\x89PNG")
    resultado = executar(RAIZ / "exemplos/grafo.json", "ausente", "--relatorio", saida)
    assert resultado.returncode == 2 and "Erro:" in resultado.stderr
    assert "Traceback" not in resultado.stderr

    resultado = executar(RAIZ / "exemplos/grafo.json", "0")
    assert resultado.returncode == 0, resultado.stderr
    assert json.loads((tmp_path / "resultados/relatorio.json").read_text())
    assert not (tmp_path / "relatorio.json").exists()


def test_gerar_dataset_salva_apenas_seis_grafos_aleatorios(tmp_path):
    from caminhos_minimos.gerar_dataset import gerar_dataset

    pasta_saida = tmp_path / "datasets"
    arquivos = gerar_dataset(pasta_saida, semente=42)
    nomes_esperados = {
        "grafo_10_10.json",
        "grafo_10_50.json",
        "grafo_50_10.json",
        "grafo_50_50.json",
        "grafo_100_10.json",
        "grafo_100_50.json",
    }
    assert len(arquivos) == 6
    assert {arquivo.name for arquivo in pasta_saida.iterdir()} == nomes_esperados
    assert set(arquivos) == {pasta_saida / nome for nome in nomes_esperados}
    for arquivo in arquivos:
        grafo = carregar_grafo(arquivo)
        quantidade_vertices = int(arquivo.stem.split("_")[1])
        assert len(grafo) == quantidade_vertices
