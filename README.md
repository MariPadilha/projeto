# Projeto de Teoria da Computação

### Integrantes

| Integrante | Matrícula |
|---|---:|
| Mariana Padilha | 2410100712 |
| Emanuel Carricio | 223941292 |
| Matheus Ciocca | 239999999 |
| Rafaela Fernandes | 2188988983 |
| Livia Barros | 249898898 |

## Sobre o projeto

O projeto implementa e compara algoritmos de caminhos mínimos em grafos
direcionados. A implementação em Python foi baseada no arquivo `main.c`.

Os algoritmos utilizados são Dijkstra e A estrela. Ambos foram implementados
sem heap. O próximo vértice é escolhido por uma busca linear entre os vértices
ainda não visitados.

## Objetivos

- Aplicar conceitos de grafos e caminhos mínimos;
- compreender a estratégia gulosa de Dijkstra;
- comparar Dijkstra e A estrela;
- analisar distância, caminho, tempo e vértices expandidos;
- trabalhar com diferentes datasets;
- gerar relatórios e gráficos dos resultados;
- utilizar Docker para garantir um ambiente reproduzível.

## Representação do grafo

O projeto utiliza uma única representação: um dicionário de adjacência. Cada
vértice possui um dicionário com seus vizinhos e os pesos das arestas.

```python
grafo = {
    "A": {"B": 4, "C": 1},
    "B": {"D": 1},
    "C": {"B": 2, "D": 5},
    "D": {},
}
```

O grafo é direcionado e os pesos devem ser números não negativos. Para uma
aresta nos dois sentidos, as duas direções devem ser informadas.

## Funcionamento dos algoritmos

### Dijkstra

Dijkstra começa com distância zero na origem e distância infinita nos demais
vértices. Em cada etapa, seleciona o vértice não visitado com menor distância
conhecida e atualiza os custos dos seus vizinhos.

### A estrela

A estrela seleciona o vértice com menor prioridade:

```text
f(v) = g(v) + h(v)
```

Onde `g(v)` é o custo acumulado e `h(v)` é a estimativa até o destino. Como os
datasets do projeto não possuem coordenadas, a heurística padrão é `h(v) = 0`.
Nesse cenário, A estrela produz o mesmo resultado que Dijkstra.

### Seleção sem heap

Os algoritmos não utilizam `heapq` nem outra fila de prioridade. A seleção é
feita percorrendo linearmente os vértices não visitados.

Complexidade:

```text
O(V² + E)
```

`V` representa a quantidade de vértices e `E`, a quantidade de arestas.

## Formato dos datasets

### JSON

```json
{
  "A": {"B": 4, "C": 1},
  "B": {"D": 1},
  "C": {"B": 2, "D": 5},
  "D": {}
}
```

Também é aceito um objeto JSON com a chave `graph` contendo o grafo.

### CSV

O arquivo CSV deve possuir as colunas `source`, `target` e `weight`:

```csv
source,target,weight
A,B,4
A,C,1
B,D,1
C,B,2
C,D,5
```

O arquivo de exemplo `grafo.json` utiliza o grafo de `main.c`.

## Execução local

Execute os dois algoritmos informando o dataset, a origem e o destino:

```bash
python main.py grafo.json 0 9
```

Saída esperada, com pequenas variações no tempo:

```text
dijkstra: distância=9, tempo=...
a_estrela: distância=9, tempo=...
```

## Relatórios

É possível salvar os resultados em JSON, CSV ou HTML.

```bash
python main.py grafo.json 0 9 --relatorio relatorio.json
python main.py grafo.json 0 9 --relatorio relatorio.csv
python main.py grafo.json 0 9 --relatorio relatorio.html
```

O relatório contém algoritmo, distância, caminho, alcance do destino, vértices
expandidos, tempo de execução, quantidade de vértices, arestas e complexidade.

## Gráficos com Python

Para desenhar o grafo e destacar o caminho encontrado:

```bash
python main.py grafo.json 0 9 --grafico grafo.png
```

## Gráficos dos relatórios com MATLAB

O arquivo `gerar_graficos_relatorio.m` lê um relatório JSON e cria um gráfico
comparativo de distância, tempo de execução e vértices expandidos.

No MATLAB, execute:

```matlab
gerar_graficos_relatorio("relatorio.json", "graficos")
```

O arquivo `graficos/comparacao_algoritmos.png` será criado.

## Execução com Docker

Todos os comandos devem ser executados na raiz do projeto.

### Construir a imagem

```bash
docker build -t caminhos-minimos .
```

### Executar JSON

```bash
docker run --rm -v "$(pwd):/app" caminhos-minimos grafo.json 0 9
```

### Executar CSV

```bash
docker run --rm -v "$(pwd):/app" caminhos-minimos grafo.csv A D
```

### Gerar relatórios

```bash
docker run --rm -v "$(pwd):/app" caminhos-minimos \
  grafo.json 0 9 --relatorio relatorio.json

docker run --rm -v "$(pwd):/app" caminhos-minimos \
  grafo.json 0 9 --relatorio relatorio.csv

docker run --rm -v "$(pwd):/app" caminhos-minimos \
  grafo.json 0 9 --relatorio relatorio.html
```

### Gerar relatório e gráfico

```bash
docker run --rm -v "$(pwd):/app" caminhos-minimos \
  grafo.json 0 9 \
  --relatorio relatorio.json \
  --grafico grafo.png
```

### Executar os testes

```bash
docker run --rm -v "$(pwd):/app" \
  --entrypoint python caminhos-minimos -m pytest -q
```

Ou usando `unittest`:

```bash
docker run --rm -v "$(pwd):/app" \
  --entrypoint python caminhos-minimos -m unittest -q
```

### Abrir um terminal no container

```bash
docker run --rm -it -v "$(pwd):/app" \
  --entrypoint bash caminhos-minimos
```

### Consultar e remover a imagem

```bash
docker images caminhos-minimos
docker rmi caminhos-minimos
```

### Limpar containers parados

```bash
docker container prune
```

## Estrutura dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Recebe os argumentos e coordena a execução. |
| `algorithms.py` | Implementa Dijkstra e A estrela com caminhos. |
| `dijkstra.py` | Define os tipos do grafo e Dijkstra básico. |
| `datasets.py` | Carrega, valida, salva e gera datasets. |
| `evaluation.py` | Mede os resultados dos algoritmos. |
| `reports.py` | Exporta relatórios JSON, CSV e HTML. |
| `visualization.py` | Gera imagens dos grafos. |
| `complexity.py` | Informa as complexidades dos componentes. |
| `gerar_graficos_relatorio.m` | Gera gráficos dos relatórios no MATLAB. |
| `grafo.json` | Dataset de exemplo baseado na versão em C. |
| `main.c` | Implementação original usada como referência. |
| `test_dijkstra.py` | Testes da implementação básica. |
| `test_features.py` | Testes dos recursos do projeto. |
| `Dockerfile` | Define o ambiente de execução do Docker. |
| `.dockerignore` | Define arquivos ignorados durante o build. |
| `requirements.txt` | Lista as dependências Python. |

## Testes

Com as dependências instaladas:

```bash
pytest -q
```

Também é possível executar:

```bash
python -m unittest -q
```
