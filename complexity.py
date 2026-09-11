def resumo_complexidade(vertices: int, arestas: int) -> dict[str, str]:
    return {
        "dijkstra": "O(V² + E) (seleção linear do próximo vértice)",
        "a_estrela": "O(V² + E) (seleção linear do próximo vértice)",
        "visualizacao_grafo": "O(V + E) para construir o grafo",
        "conjunto_dados": f"V={vertices}, E={arestas}",
    }
