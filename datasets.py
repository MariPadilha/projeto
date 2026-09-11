from __future__ import annotations

import csv
import json
from pathlib import Path
from random import Random
from typing import Any


class GerenciadorDeDados:
    def carregar(self, caminho: str | Path) -> dict[str, dict[str, float]]:
        caminho = Path(caminho)
        if caminho.suffix.lower() == ".csv":
            with caminho.open(newline="", encoding="utf-8") as arquivo:
                linhas = csv.DictReader(arquivo)
                grafo: dict[str, dict[str, float]] = {}
                for linha in linhas:
                    origem, destino = linha["source"], linha["target"]
                    grafo.setdefault(origem, {})[destino] = float(linha["weight"])
                    grafo.setdefault(destino, {})
        elif caminho.suffix.lower() == ".json":
            with caminho.open(encoding="utf-8") as arquivo:
                dados: Any = json.load(arquivo)
            grafo = dados.get("graph", dados) if isinstance(dados, dict) else dados
        else:
            raise ValueError("formato suportado: .json ou .csv")
        self.validar(grafo)
        return grafo

    @staticmethod
    def validar(grafo: dict[str, dict[str, float]]) -> None:
        if not isinstance(grafo, dict):
            raise ValueError("o conjunto de dados deve ser um objeto de adjacência")
        vertices_faltantes = []
        for origem, vizinhos in list(grafo.items()):
            if not isinstance(vizinhos, dict):
                raise ValueError(f"vizinhos inválidos para {origem!r}")
            for destino, peso in vizinhos.items():
                if not isinstance(peso, (int, float)) or peso < 0:
                    raise ValueError("pesos devem ser números não negativos")
                if destino not in grafo:
                    vertices_faltantes.append(destino)
        for vertice in vertices_faltantes:
            grafo.setdefault(vertice, {})

    @staticmethod
    def salvar(grafo: dict[str, dict[str, float]], caminho: str | Path) -> None:
        GerenciadorDeDados.validar(grafo)
        with Path(caminho).open("w", encoding="utf-8") as arquivo:
            json.dump(grafo, arquivo, ensure_ascii=False, indent=2)

    @staticmethod
    def aleatorio(quantidade: int, probabilidade_aresta: float = 0.2, semente: int | None = 0) -> dict[str, dict[str, int]]:
        if quantidade < 1 or not 0 <= probabilidade_aresta <= 1:
            raise ValueError("quantidade deve ser positiva e a probabilidade deve estar entre 0 e 1")
        gerador = Random(semente)
        grafo = {str(i): {} for i in range(quantidade)}
        for origem in grafo:
            for destino in grafo:
                if origem != destino and gerador.random() < probabilidade_aresta:
                    grafo[origem][destino] = gerador.randint(1, 100)
        return grafo
