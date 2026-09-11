import math
import unittest

from dijkstra import dijkstra


class TestesDijkstra(unittest.TestCase):
    def test_encontra_menores_distancias(self):
        grafo = {
            "A": {"B": 4, "C": 1},
            "B": {"D": 1},
            "C": {"B": 2, "D": 5},
            "D": {},
        }

        self.assertEqual(dijkstra(grafo, "A"), {"A": 0, "B": 3, "C": 1, "D": 4})

    def test_marca_vertices_inalcancaveis_com_infinito(self):
        self.assertEqual(
            dijkstra({"A": {"B": 2}, "B": {}, "C": {}}, "A"),
            {"A": 0, "B": 2, "C": math.inf},
        )

    def test_rejeita_peso_negativo(self):
        with self.assertRaisesRegex(ValueError, "peso negativo"):
            dijkstra({"A": {"B": -1}, "B": {}}, "A")

    def test_origem_inexistente(self):
        with self.assertRaises(KeyError):
            dijkstra({"A": {}}, "Z")


if __name__ == "__main__":
    unittest.main()
