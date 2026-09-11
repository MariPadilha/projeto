"""Limites da implementação com seleção linear, sem fila de prioridade."""


def resumo_complexidade(vertices: int, arestas: int) -> dict[str, str]:
    return {
        "dijkstra": "O(V² + E) em tempo; O(V) em espaço auxiliar",
        "a_estrela": "O(V² + E) em tempo; O(V) em espaço auxiliar; h consistente",
        "conjunto_dados": f"V={vertices}, E={arestas}",
    }
