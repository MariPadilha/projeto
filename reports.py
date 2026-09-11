from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def exportar_relatorio(resultados: list[dict[str, Any]], caminho: str | Path) -> None:
    caminho = Path(caminho)
    if caminho.suffix.lower() == ".json":
        caminho.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if caminho.suffix.lower() == ".csv":
        campos = ["algoritmo", "distancia", "alcancavel", "vertices_expandidos", "tempo_execucao_ms", "vertices", "arestas", "complexidade", "caminho"]
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=campos)
            writer.writeheader()
            for resultado in resultados:
                linha = dict(resultado)
                linha["caminho"] = " -> ".join(map(str, linha["caminho"]))
                writer.writerow({campo: linha.get(campo) for campo in campos})
        return
    if caminho.suffix.lower() in {".html", ".htm"}:
        cabecalhos = list(resultados[0]) if resultados else []
        linhas = "".join("<tr>" + "".join(f"<td>{resultado.get(cabecalho, '')}</td>" for cabecalho in cabecalhos) + "</tr>" for resultado in resultados)
        tabela = "<table><tr>" + "".join(f"<th>{cabecalho}</th>" for cabecalho in cabecalhos) + "</tr>" + linhas + "</table>"
        caminho.write_text(f"<html><body><h1>Relatório de caminhos mínimos</h1>{tabela}</body></html>", encoding="utf-8")
        return
    raise ValueError("formato de relatório suportado: .json, .csv ou .html")
