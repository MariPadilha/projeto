"""Leitura, escrita e geração reproduzível de conjuntos de dados."""

import csv
import json
from pathlib import Path
from random import Random

from grafo import Grafo, validar_grafo


def _objeto_sem_duplicatas(pares: list[tuple]) -> dict:
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"chave duplicada no JSON: {chave!r}")
        objeto[chave] = valor
    return objeto


class GerenciadorDeDados:
    """Converte formatos externos para o dicionário usado pelos algoritmos."""

    def carregar(self, caminho: str | Path) -> Grafo:
        caminho = Path(caminho)
        if caminho.suffix.lower() == ".csv":
            grafo = self._carregar_csv(caminho)
        elif caminho.suffix.lower() == ".json":
            with caminho.open(encoding="utf-8") as arquivo:
                grafo = json.load(arquivo, object_pairs_hook=_objeto_sem_duplicatas)
            if isinstance(grafo, dict) and len(grafo) == 1:
                for chave in ("grafo", "graph"):
                    conteudo = grafo.get(chave)
                    if isinstance(conteudo, dict) and any(
                        isinstance(valor, dict) for valor in conteudo.values()
                    ):
                        grafo = conteudo
                        break
        else:
            raise ValueError("formato de dados suportado: .json ou .csv")
        if not isinstance(grafo, dict):
            raise ValueError("o conjunto de dados deve ser um objeto de adjacência")
        # Completa destinos implícitos somente durante a importação.
        for vizinhos in list(grafo.values()):
            if isinstance(vizinhos, dict):
                for destino in vizinhos:
                    grafo.setdefault(destino, {})
        validar_grafo(grafo)
        return grafo

    @staticmethod
    def _carregar_csv(caminho: Path) -> Grafo:
        grafo: Grafo = {}
        with caminho.open(newline="", encoding="utf-8-sig") as arquivo:
            linhas = csv.DictReader(arquivo)
            campos = linhas.fieldnames
            if campos in (
                ["origem", "destino", "peso"],
                ["source", "target", "weight"],
            ):
                origem_coluna, destino_coluna, peso_coluna = campos
            else:
                raise ValueError("o CSV deve ter o cabeçalho origem,destino,peso")
            for numero, linha in enumerate(linhas, start=2):
                if None in linha or any(valor is None for valor in linha.values()):
                    raise ValueError(f"linha {numero}: quantidade de colunas inválida")
                origem = linha[origem_coluna].strip()
                destino = linha[destino_coluna].strip()
                peso_texto = linha[peso_coluna].strip()
                if not origem or (not destino and peso_texto):
                    raise ValueError(f"linha {numero}: vértice ausente")
                grafo.setdefault(origem, {})
                if not destino and not peso_texto:
                    continue  # 'X,,' representa um vértice isolado.
                if destino in grafo[origem]:
                    raise ValueError(f"linha {numero}: aresta duplicada")
                try:
                    peso = int(peso_texto)
                except ValueError:
                    try:
                        peso = float(peso_texto)
                    except ValueError as erro:
                        raise ValueError(f"linha {numero}: peso inválido") from erro
                grafo[origem][destino] = peso
                grafo.setdefault(destino, {})
        return grafo

    validar = staticmethod(validar_grafo)

    @staticmethod
    def salvar(grafo: Grafo, caminho: str | Path) -> None:
        """Salva JSON ou CSV, preservando inclusive vértices isolados."""
        validar_grafo(grafo)
        caminho = Path(caminho)
        if caminho.suffix.lower() == ".json":
            caminho.write_text(
                json.dumps(grafo, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
        elif caminho.suffix.lower() == ".csv":
            with caminho.open("w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(["origem", "destino", "peso"])
                for origem, vizinhos in grafo.items():
                    if not vizinhos:
                        escritor.writerow([origem, "", ""])
                    for destino, peso in vizinhos.items():
                        escritor.writerow([origem, destino, peso])
        else:
            raise ValueError("formato de dados suportado: .json ou .csv")

    @staticmethod
    def aleatorio(
        quantidade: int, probabilidade_aresta: float = 0.2, semente: int | None = 0
    ) -> Grafo:
        """Gera grafo direcionado sem laços, com pesos inteiros de 1 a 100."""
        if (
            isinstance(quantidade, bool)
            or not isinstance(quantidade, int)
            or quantidade < 1
        ):
            raise ValueError("quantidade deve ser um inteiro positivo")
        if (
            isinstance(probabilidade_aresta, bool)
            or not isinstance(probabilidade_aresta, (int, float))
            or not 0 <= probabilidade_aresta <= 1
        ):
            raise ValueError("a probabilidade deve estar entre 0 e 1")
        gerador = Random(semente)
        grafo: Grafo = {str(indice): {} for indice in range(quantidade)}
        for origem in grafo:
            for destino in grafo:
                if origem != destino and gerador.random() < probabilidade_aresta:
                    grafo[origem][destino] = gerador.randint(1, 100)
        return grafo
