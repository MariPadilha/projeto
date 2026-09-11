/* Referência complementar em C. A entrega principal é a implementação Python.
 * Nesta matriz, zero significa ausência de aresta; não representa aresta de custo zero.
 * A busca de posição no heap é linear: esta versão não tem decrease-key O(log V).
 */
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define TAM 10
#define INF INT_MAX

typedef struct Tabela_dijkstra {
    int visitado;
    int distancia;
} Tabela_dijkstra;

typedef struct Dijkstra {
    Tabela_dijkstra *tabela;
} Dijkstra;

int grafo[TAM][TAM] = {
    {0, 2, 0, 1, 0, 0, 0, 0, 0, 0},
    {2, 0, 3, 2, 0, 0, 0, 0, 0, 0},
    {0, 3, 0, 0, 0, 1, 0, 0, 0, 0},
    {1, 2, 0, 0, 3, 0, 0, 0, 0, 0},
    {0, 0, 0, 3, 0, 1, 1, 0, 0, 0},
    {0, 0, 1, 0, 1, 0, 1, 0, 0, 0},
    {0, 0, 0, 0, 1, 1, 0, 3, 0, 0},
    {0, 0, 0, 0, 0, 0, 3, 0, 2, 1},
    {0, 0, 0, 0, 0, 0, 0, 2, 0, 4},
    {0, 0, 0, 0, 0, 0, 0, 1, 4, 0}
};

typedef struct {
    int valor;
    int distancia;
} Vertice;

typedef struct {
    int comprimento;
    int tam_heap;
    Vertice *v;
} Heap;

int filho_esquerdo(int i) {
    return 2 * i + 1;
}

int filho_direito(int i) {
    return 2 * i + 2;
}

int pai(int i) {
    return (i - 1) / 2;
}

void restaurar_heap_minimo(Heap *h, int i) {
    int l = filho_esquerdo(i);
    int r = filho_direito(i);
    int menor = i;

    if (l < h->tam_heap && h->v[l].distancia < h->v[i].distancia) {
        menor = l;
    }
    if (r < h->tam_heap && h->v[r].distancia < h->v[menor].distancia) {
        menor = r;
    }
    if (menor != i) {
        Vertice temporario = h->v[i];
        h->v[i] = h->v[menor];
        h->v[menor] = temporario;
        restaurar_heap_minimo(h, menor);
    }
}

void construir_heap_minimo(Heap *h) {
    for (int i = h->comprimento / 2 - 1; i >= 0; i--) {
        restaurar_heap_minimo(h, i);
    }
}

Vertice extrair_minimo(Heap *h) {
    if (h->tam_heap <= 0) {
        printf("Heap vazia\n");
        exit(1);
    }

    Vertice menor = h->v[0];
    h->v[0] = h->v[h->tam_heap - 1];
    h->tam_heap--;
    restaurar_heap_minimo(h, 0);
    return menor;
}

Heap *inicia_heap_vertices(int n) {
    Heap *h = malloc(sizeof(*h));
    if (h == NULL) {
        fputs("Falha ao alocar heap\n", stderr);
        exit(EXIT_FAILURE);
    }
    h->comprimento = n;
    h->tam_heap = n;
    h->v = malloc(sizeof(*h->v) * (size_t)n);
    if (h->v == NULL) {
        free(h);
        fputs("Falha ao alocar vértices\n", stderr);
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < n; i++) {
        h->v[i].valor = i;
        h->v[i].distancia = (i == 0 ? 0 : INF);
    }
    construir_heap_minimo(h);
    return h;
}

int posicao_vertice(Heap *h, int vertice) {
    for (int i = 0; i < h->tam_heap; i++) {
        if (h->v[i].valor == vertice) {
            return i;
        }
    }
    return -1;
}

void diminuir_prioridade(Heap *h, int vertice, int nova_distancia) {
    int i = posicao_vertice(h, vertice);
    if (i == -1) {
        return;
    }
    if (nova_distancia >= h->v[i].distancia) {
        return;
    }

    h->v[i].distancia = nova_distancia;
    while (i > 0 && h->v[pai(i)].distancia > h->v[i].distancia) {
        Vertice temporario = h->v[i];
        h->v[i] = h->v[pai(i)];
        h->v[pai(i)] = temporario;
        i = pai(i);
    }
}

void inicializa_tabela(Tabela_dijkstra *aux) {
    for (int i = 0; i < TAM; i++) {
        aux[i].distancia = (i == 0) ? 0 : INT_MAX;
        aux[i].visitado = 0;
    }
}

Dijkstra *inicializa_dijkstra(void) {
    Dijkstra *aux = malloc(sizeof(*aux));
    if (aux == NULL) {
        fputs("Falha ao alocar estado\n", stderr);
        exit(EXIT_FAILURE);
    }
    aux->tabela = malloc(sizeof(*aux->tabela) * TAM);
    if (aux->tabela == NULL) {
        free(aux);
        fputs("Falha ao alocar tabela\n", stderr);
        exit(EXIT_FAILURE);
    }
    inicializa_tabela(aux->tabela);
    return aux;
}

void dijkstra_com_heap(void) {
    Dijkstra *aux = inicializa_dijkstra();
    Heap *heap = inicia_heap_vertices(TAM);

    while (heap->tam_heap > 0) {
        Vertice minimo = extrair_minimo(heap);
        if (minimo.distancia == INF) {
            break;
        }
        int vertice_u = minimo.valor;
        aux->tabela[vertice_u].visitado = 1;

        for (int v = 0; v < TAM; v++) {
            if (grafo[vertice_u][v] != 0 && !aux->tabela[v].visitado) {
                if (aux->tabela[vertice_u].distancia > INF - grafo[vertice_u][v]) {
                    continue;
                }
                int nova_distancia = aux->tabela[vertice_u].distancia + grafo[vertice_u][v];
                if (nova_distancia < aux->tabela[v].distancia) {
                    aux->tabela[v].distancia = nova_distancia;
                    diminuir_prioridade(heap, v, nova_distancia);
                }
            }
        }
    }

    printf("\nDistâncias mínimas a partir do vértice 0:\n");
    for (int i = 0; i < TAM; i++) {
        printf("0 -> %d = %d\n", i, aux->tabela[i].distancia);
    }

    free(aux->tabela);
    free(aux);
    free(heap->v);
    free(heap);
}

int main(void) {
    printf("Executando Dijkstra com min-heap:\n");
    dijkstra_com_heap();
    return 0;
}
