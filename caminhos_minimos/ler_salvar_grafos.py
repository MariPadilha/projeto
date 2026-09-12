import csv
import json
from pathlib import Path

from caminhos_minimos.grafo import Grafo, Peso, validar_grafo


def _objeto_json_sem_chaves_duplicadas(pares_chave_valor: list[tuple]) -> dict:
    objeto_json = {}
    for chave, valor in pares_chave_valor:
        if chave in objeto_json:
            raise ValueError(f"chave duplicada no JSON: {chave!r}")
        objeto_json[chave] = valor
    return objeto_json


def _converter_peso_csv(peso_texto: str, numero_linha: int) -> Peso:
    try:
        return int(peso_texto)
    except ValueError:
        try:
            return float(peso_texto)
        except ValueError as erro:
            raise ValueError(f"linha {numero_linha}: peso inválido") from erro


def carregar_grafo(caminho: str | Path) -> Grafo:
    caminho = Path(caminho)
    if caminho.suffix.lower() == ".csv":
        grafo = _carregar_csv(caminho)
    elif caminho.suffix.lower() == ".json":
        grafo = _carregar_json(caminho)
    else:
        raise ValueError("formato de dados suportado: .json ou .csv")
    if not isinstance(grafo, dict):
        raise ValueError("o conjunto de dados deve ser um objeto de adjacência")
    _completar_vertices_de_destino(grafo)
    validar_grafo(grafo)
    return grafo


def _completar_vertices_de_destino(grafo: Grafo) -> None:
    for vizinhos in list(grafo.values()):
        if isinstance(vizinhos, dict):
            for destino in vizinhos:
                grafo.setdefault(destino, {})


def _carregar_json(caminho: Path) -> Grafo:
    with caminho.open(encoding="utf-8") as arquivo:
        grafo = json.load(arquivo, object_pairs_hook=_objeto_json_sem_chaves_duplicadas)
    if isinstance(grafo, dict) and len(grafo) == 1:
        for chave_grafo in ("grafo", "graph"):
            grafo_interno = grafo.get(chave_grafo)
            if isinstance(grafo_interno, dict) and any(
                isinstance(vizinhos, dict) for vizinhos in grafo_interno.values()
            ):
                return grafo_interno
    return grafo


def _carregar_csv(caminho: Path) -> Grafo:
    grafo: Grafo = {}
    with caminho.open(newline="", encoding="utf-8-sig") as arquivo:
        leitor_csv = csv.DictReader(arquivo)
        cabecalho = leitor_csv.fieldnames
        if cabecalho in (
            ["origem", "destino", "peso"],
            ["source", "target", "weight"],
        ):
            coluna_origem, coluna_destino, coluna_peso = cabecalho
        else:
            raise ValueError("o CSV deve ter o cabeçalho origem,destino,peso")
        for numero_linha, linha in enumerate(leitor_csv, start=2):
            if None in linha or any(valor is None for valor in linha.values()):
                raise ValueError(
                    f"linha {numero_linha}: quantidade de colunas inválida"
                )
            origem = linha[coluna_origem].strip()
            destino = linha[coluna_destino].strip()
            peso_texto = linha[coluna_peso].strip()
            if not origem or (not destino and peso_texto):
                raise ValueError(f"linha {numero_linha}: vértice ausente")
            grafo.setdefault(origem, {})
            declara_vertice_isolado = not destino and not peso_texto
            if declara_vertice_isolado:
                continue
            if destino in grafo[origem]:
                raise ValueError(f"linha {numero_linha}: aresta duplicada")
            grafo[origem][destino] = _converter_peso_csv(peso_texto, numero_linha)
            grafo.setdefault(destino, {})
    return grafo


def salvar_grafo(grafo: Grafo, caminho: str | Path) -> None:
    validar_grafo(grafo)
    caminho = Path(caminho)
    if caminho.suffix.lower() == ".json":
        caminho.write_text(
            json.dumps(grafo, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    elif caminho.suffix.lower() == ".csv":
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            escritor_csv = csv.writer(arquivo)
            escritor_csv.writerow(["origem", "destino", "peso"])
            for origem, vizinhos in grafo.items():
                if not vizinhos:
                    escritor_csv.writerow([origem, "", ""])
                for destino, peso in vizinhos.items():
                    escritor_csv.writerow([origem, destino, peso])
    else:
        raise ValueError("formato de dados suportado: .json ou .csv")
