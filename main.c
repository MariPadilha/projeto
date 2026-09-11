#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>

#define TAM 10
#define INF INT_MAX

typedef struct Tabela_dijkstra {
    int visitado;
    int vertice;
    int distancia;
    int anterior;
} Tabela_dijkstra;

typedef struct Dijkstra {
    int atual;
    int distancia;
    int n_visitados;
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

void imprime_vetor(Vertice v[], int n) {
    printf("Vetor =\n[ ");
    for (int i = 0; i < n - 1; i++) {
        printf("%d, ", v[i].valor);
    }
    printf("%d ]\n\n", v[n - 1].valor);
}

void imprime_heap(Vertice v[], int n) {
    printf("Heap =\n");
    int count = 1;
    for (int i = 1; i <= n; i++) {
        printf("%d ", v[i - 1].valor);
        if (i == pow(2, count) - 1) {
            printf("\n");
            count++;
        }
    }
    printf("\n\n");
}

int left(int i) {
    return 2 * i + 1;
}

int right(int i) {
    return 2 * i + 2;
}

int parent(int i) {
    return (i - 1) / 2;
}

void min_heapify(Heap *h, int i) {
    int l = left(i);
    int r = right(i);
    int menor = i;

    if (l < h->tam_heap && h->v[l].distancia < h->v[i].distancia) {
        menor = l;
    }
    if (r < h->tam_heap && h->v[r].distancia < h->v[menor].distancia) {
        menor = r;
    }
    if (menor != i) {
        Vertice temp = h->v[i];
        h->v[i] = h->v[menor];
        h->v[menor] = temp;
        min_heapify(h, menor);
    }
}

void build_min_heap(Heap *h) {
    for (int i = h->comprimento / 2 - 1; i >= 0; i--) {
        min_heapify(h, i);
    }
}

Vertice heap_pop(Heap *h) {
    if (h->tam_heap <= 0) {
        printf("Heap vazia\n");
        exit(1);
    }

    Vertice menor = h->v[0];
    h->v[0] = h->v[h->tam_heap - 1];
    h->tam_heap--;
    min_heapify(h, 0);
    return menor;
}

Heap *inicia_heap_vertices(int n) {
    Heap *h = (Heap *) malloc(sizeof(Heap));
    h->comprimento = n;
    h->tam_heap = n;
    h->v = (Vertice *) malloc(sizeof(Vertice) * n);

    for (int i = 0; i < n; i++) {
        h->v[i].valor = i;
        h->v[i].distancia = (i == 0 ? 0 : INF);
    }
    build_min_heap(h);
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

void heap_decrease_key(Heap *h, int vertice, int nova_dist) {
    int i = posicao_vertice(h, vertice);
    if (i == -1) {
        return;
    }
    if (nova_dist >= h->v[i].distancia) {
        return;
    }

    h->v[i].distancia = nova_dist;
    while (i > 0 && h->v[parent(i)].distancia > h->v[i].distancia) {
        Vertice temp = h->v[i];
        h->v[i] = h->v[parent(i)];
        h->v[parent(i)] = temp;
        i = parent(i);
    }
}

void inicializa_tabela(Tabela_dijkstra *aux) {
    for (int i = 0; i < TAM; i++) {
        aux[i].distancia = (i == 0) ? 0 : INT_MAX;
        aux[i].visitado = 0;
        aux[i].anterior = -1;
    }
}

Dijkstra *inicializa_dijkstra() {
    Dijkstra *aux = (Dijkstra *) malloc(sizeof(Dijkstra));
    aux->tabela = (Tabela_dijkstra *) malloc(sizeof(Tabela_dijkstra) * TAM);
    inicializa_tabela(aux->tabela);
    aux->atual = 0;
    aux->n_visitados = TAM - 1;
    aux->distancia = 0;
    return aux;
}

void dijkstra_com_heap() {
    Dijkstra *aux = inicializa_dijkstra();
    Heap *heap = inicia_heap_vertices(TAM);

    while (heap->tam_heap > 0) {
        Vertice u = heap_pop(heap);
        int vertice_u = u.valor;
        aux->tabela[vertice_u].visitado = 1;

        for (int v = 0; v < TAM; v++) {
            if (grafo[vertice_u][v] != 0 && !aux->tabela[v].visitado) {
                int nova_dist = aux->tabela[vertice_u].distancia + grafo[vertice_u][v];
                if (nova_dist < aux->tabela[v].distancia) {
                    aux->tabela[v].distancia = nova_dist;
                    aux->tabela[v].anterior = vertice_u;
                    heap_decrease_key(heap, v, nova_dist);
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

int main() {
    printf("Executando Dijkstra com min-heap:\n");
    dijkstra_com_heap();
    return 0;
}
