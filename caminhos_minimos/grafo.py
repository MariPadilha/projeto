from math import isfinite
from typing import TypeAlias

Peso: TypeAlias = int | float
Grafo: TypeAlias = dict[str, dict[str, Peso]]


def validar_numero_nao_negativo(valor: Peso, nome_campo: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome_campo} deve ser um número não negativo")
    if valor < 0:
        raise ValueError(f"{nome_campo}: peso negativo não é permitido")
    if isinstance(valor, float) and not isfinite(valor):
        raise ValueError(f"{nome_campo} deve ser finito")


def validar_grafo(grafo: Grafo) -> None:
    if not isinstance(grafo, dict):
        raise ValueError("o grafo deve ser um dicionário de adjacência")
    for origem, vizinhos in grafo.items():
        if not isinstance(origem, str) or not origem.strip():
            raise ValueError("os vértices devem ser textos não vazios")
        if not isinstance(vizinhos, dict):
            raise ValueError(f"vizinhos inválidos para {origem!r}")
        for destino, peso in vizinhos.items():
            if not isinstance(destino, str) or destino not in grafo:
                raise ValueError(f"vértice de destino ausente no grafo: {destino!r}")
            validar_numero_nao_negativo(peso, f"aresta {origem!r} → {destino!r}")


def somar_custos(primeiro_custo: Peso, segundo_custo: Peso) -> Peso:
    try:
        custo_total = primeiro_custo + segundo_custo
    except OverflowError as erro:
        raise ValueError("custo excede a capacidade de ponto flutuante") from erro
    if isinstance(custo_total, float) and not isfinite(custo_total):
        raise ValueError("custo excede a capacidade de ponto flutuante")
    return custo_total
