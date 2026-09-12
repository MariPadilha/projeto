import math
import unittest

from caminhos_minimos.algoritmos import buscar, dijkstra


class TestesDijkstra(unittest.TestCase):
    def test_encontra_menores_distancias(self):
        grafo = {
            "A": {"B": 4, "C": 1},
            "B": {"D": 1},
            "C": {"B": 2, "D": 5},
            "D": {},
        }

        self.assertEqual(dijkstra(grafo, "A"), [0, 3, 1, 4])

    def test_marca_vertices_inalcancaveis_com_infinito(self):
        self.assertEqual(
            dijkstra({"A": {"B": 2}, "B": {}, "C": {}}, "A"),
            [0, 2, math.inf],
        )

    def test_buscar_retorna_vetor_completo_na_ordem_dos_vertices(self):
        grafo = {
            "Z": {},
            "C": {"D": 1},
            "A": {"B": 1, "C": 9},
            "B": {"C": 1},
            "D": {},
        }

        self.assertEqual(buscar(grafo, "A"), [math.inf, 2, 0, 1, 3])

    def test_rejeita_peso_negativo(self):
        with self.assertRaisesRegex(ValueError, "peso negativo"):
            dijkstra({"A": {"B": -1}, "B": {}}, "A")

    def test_origem_inexistente(self):
        with self.assertRaises(KeyError):
            dijkstra({"A": {}}, "Z")

    def test_contraexemplo_negativo_documentado(self):
        from exemplos.contraexemplo import demonstrar_falha_com_peso_negativo

        self.assertEqual(
            demonstrar_falha_com_peso_negativo(), {"A": 0, "B": 2, "C": 5, "D": 4}
        )
        with self.assertRaises(ValueError):
            dijkstra(
                {"A": {"B": 2, "C": 5}, "B": {"D": 2}, "C": {"B": -4}, "D": {}}, "A"
            )


if __name__ == "__main__":
    unittest.main()
