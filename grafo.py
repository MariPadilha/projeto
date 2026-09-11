"""Representação e restrições compartilhadas pelos algoritmos e datasets."""

from math import isfinite
from typing import TypeAlias

Peso: TypeAlias = int | float
Grafo: TypeAlias = dict[str, dict[str, Peso]]


def validar_numero(valor: Peso, nome: str) -> None:
    """Aceita números finitos e não negativos; booleanos são inválidos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser um número não negativo")
    if valor < 0:
        raise ValueError(f"{nome}: peso negativo não é permitido")
    if isinstance(valor, float) and not isfinite(valor):
        raise ValueError(f"{nome} deve ser finito")


def validar_grafo(grafo: Grafo) -> None:
    """Valida todo o grafo sem modificá-lo, inclusive partes desconexas."""
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
            validar_numero(peso, f"aresta {origem!r} → {destino!r}")


def somar_custos(primeiro: Peso, segundo: Peso) -> Peso:
    """Não confunde estouro de ponto flutuante com vértice inalcançável."""
    try:
        total = primeiro + segundo
    except OverflowError as erro:
        raise ValueError("custo excede a capacidade de ponto flutuante") from erro
    if isinstance(total, float) and not isfinite(total):
        raise ValueError("custo excede a capacidade de ponto flutuante")
    return total
