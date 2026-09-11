"""Exportação de tabelas em JSON interoperável, CSV e HTML."""

import csv
import json
from html import escape
from math import isfinite
from pathlib import Path
from typing import Any


def _normalizar(valor: Any) -> Any:
    if isinstance(valor, float) and not isfinite(valor):
        return None
    if isinstance(valor, dict):
        return {chave: _normalizar(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [_normalizar(item) for item in valor]
    return valor


def exportar_relatorio(resultados: list[dict[str, Any]], caminho: str | Path) -> None:
    """Representa distância infinita como null no JSON e inalcançável nas tabelas."""
    caminho = Path(caminho)
    if caminho.suffix.lower() == ".json":
        caminho.write_text(
            json.dumps(
                _normalizar(resultados), ensure_ascii=False, indent=2, allow_nan=False
            )
            + "\n",
            encoding="utf-8",
        )
        return
    campos = list(
        dict.fromkeys(chave for resultado in resultados for chave in resultado)
    )
    linhas = []
    for resultado in _normalizar(resultados):
        linha = dict(resultado)
        if "caminho" in linha:
            linha["caminho"] = " → ".join(map(str, linha["caminho"]))
        if "distancia" in linha and linha["distancia"] is None:
            linha["distancia"] = "inalcançável"
        linhas.append(linha)
    if caminho.suffix.lower() == ".csv":
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(linhas)
        return
    if caminho.suffix.lower() in {".html", ".htm"}:
        cabecalho = "".join(f"<th>{escape(campo)}</th>" for campo in campos)
        corpo = "".join(
            "<tr>"
            + "".join(
                f"<td>{escape(str(linha.get(campo, '')))}</td>" for campo in campos
            )
            + "</tr>"
            for linha in linhas
        )
        documento = (
            '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>Relatório de caminhos mínimos</title>"
            "<style>body{font-family:sans-serif;margin:2rem;overflow-x:auto}"
            "table{border-collapse:collapse}th,td{border:1px solid #bbb;padding:.5rem}"
            "th{background:#eee}</style><body><h1>Relatório de caminhos mínimos</h1>"
            "<p>Tempos em milissegundos; quando há repetições, o tempo é a mediana. "
            "Distância inalcançável indica ausência de caminho.</p>"
            f"<table><thead><tr>{cabecalho}</tr></thead><tbody>{corpo}</tbody></table>"
            "</body></html>\n"
        )
        caminho.write_text(documento, encoding="utf-8")
        return
    raise ValueError("formato de relatório suportado: .json, .csv ou .html")
