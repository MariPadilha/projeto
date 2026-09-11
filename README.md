# Caminhos mínimos de fonte única com pesos não negativos

Trabalho de Teoria da Computação — Ciência da Computação.
Implementação em **Python**, com Dijkstra e comparação complementar com A*.

O [registro da revisão](REVISAO.md) descreve as correções, verificações executadas
e limitações conhecidas do ambiente de teste.

## Integrantes

| Integrante | Matrícula |
|---|---:|
| Mariana Padilha | 2410100712 |
| Emanuel Carricio | 223941292 |
| Matheus Ciocca | 239999999 |
| Rafaela Fernandes | 2188988983 |
| Livia Barros | 249898898 |

## Problema, instância, entrada, saída e restrições

Dado um grafo ponderado e uma origem, queremos minimizar a **soma dos pesos**
das arestas percorridas. Minimizar o número de arestas é outro objetivo:
`A → B`, de custo 4, tem menos arestas que `A → C → B`, de custo `1 + 2 = 3`,
mas é mais caro.

| Elemento | Definição |
|---|---|
| Problema | Encontrar a menor distância de uma origem até cada vértice. |
| Instância | Um grafo finito `G = (V, E)`, uma função de pesos `w` e uma origem `s ∈ V`. |
| Entrada | Dicionário de adjacência ou arquivo JSON/CSV com pesos não negativos, mais a origem. |
| Saída | Para cada `v ∈ V`, `δ(s,v)`, a menor soma dos pesos de um caminho de `s` até `v`. |
| Sem caminho | Infinito na API Python; `null` no relatório JSON; “inalcançável” no terminal e nas tabelas. |
| Origem | Tem distância zero até si mesma, inclusive quando está isolada. |

Os vértices são textos não vazios, como `"A"` e `"0"`. Os pesos são inteiros
ou números de ponto flutuante finitos e não negativos; zero é permitido.
Booleanos, `NaN`, infinito e pesos negativos são rejeitados, mesmo em componentes
inalcançáveis. A origem e o destino opcional devem existir. Um grafo vazio pode
ser armazenado, mas não possui uma origem válida para executar a busca.

O grafo é **direcionado**. Para representar uma ligação nos dois sentidos,
informe ambas as arestas. São permitidos ciclos, laços e vértices isolados.
Há no máximo uma aresta por par ordenado: o CSV rejeita duplicatas, e as chaves
do JSON devem ser únicas. Ao usar a API, todos os destinos devem ser chaves do
dicionário; durante a importação, destinos implícitos são completados com `{}`.

Para os experimentos e a análise exata, use pesos inteiros (por exemplo,
centavos ou metros). Decimais usam a aritmética aproximada de `float`; um
estouro numérico é reportado como erro. Os algoritmos não alteram o grafo recebido.

## Como executar

Requer **Python 3.10 ou posterior**. Na raiz do projeto, em Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p resultados
```

No Windows, crie o ambiente com `py -m venv .venv`, ative com
`.venv\Scripts\Activate.ps1` no PowerShell e crie a pasta `resultados`.
As versões das dependências diretas estão fixadas; dependências transitivas e
o sistema operacional ainda podem variar. O núcleo dos algoritmos usa apenas
a biblioteca padrão; Matplotlib e NetworkX são usados para gráficos, e NetworkX
também fornece uma referência independente nos testes.

### Resolver o enunciado: uma origem, todos os vértices

```bash
python main.py grafo.json 0 --relatorio resultados/distancias.json
```

Distâncias esperadas:

| Vértice | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Distância | 0 | 2 | 5 | 1 | 4 | 5 | 5 | 8 | 10 | 9 |

A função equivalente é `dijkstra(grafo, origem)`, em `dijkstra.py`.
Sem destino, o relatório contém uma linha para cada vértice.

### Comparar Dijkstra e A* até um destino

```bash
python main.py grafo.json 0 9 \
  --repeticoes 15 \
  --relatorio resultados/comparacao.json \
  --grafico resultados/grafo.png \
  --comparacao resultados/metricas.png
```

O terminal continua mostrando **todas** as distâncias. Neste modo, o relatório
contém duas linhas, uma por algoritmo, referentes à consulta `0 → 9`.
Ambos retornam custo 9 e caminho `0 → 3 → 4 → 6 → 7 → 9`.
As medições comparam consultas com o mesmo destino e parada antecipada;
a execução completa de fonte única fica fora dessa medição.

Use `python main.py --help` para listar as opções. A saída padrão é
`relatorio.json`; um arquivo existente nesse caminho será substituído.
Crie previamente a pasta de saída. As opções antigas `--report` e `--plot`
continuam aceitas por compatibilidade, mas os exemplos usam português.

## Funcionamento e correção de Dijkstra

1. Inicializa a origem com distância zero e os demais vértices com infinito.
2. Seleciona, por busca linear, o vértice ainda não fixado de menor estimativa.
3. Se a menor estimativa é infinita, encerra: os restantes são inalcançáveis.
4. Fixa o vértice e relaxa suas arestas: se `d[u] + w(u,v) < d[v]`, atualiza
   a distância e registra `u` como predecessor de `v`.
5. Repete até esgotar os alcançáveis. Na consulta a um destino, pode parar
   quando esse destino é fixado.

Exemplo de `grafo.csv`, origem A (valores após o relaxamento):

| Vértice fixado | d(A) | d(B) | d(C) | d(D) |
|---|---:|---:|---:|---:|
| Inicialização | 0 | ∞ | ∞ | ∞ |
| A | 0 | 4 | 1 | ∞ |
| C | 0 | 3 | 1 | 6 |
| B | 0 | 3 | 1 | 4 |
| D | 0 | 3 | 1 | 4 |

### Por que a escolha gulosa é segura?

O invariante é: **todo vértice fixado já tem sua distância mínima correta**.
A origem satisfaz essa propriedade, pois pesos não negativos não permitem
um caminho de custo menor que zero até ela.

Suponha que o próximo vértice escolhido, `u`, tivesse um caminho mais barato
que `d[u]`. Nesse caminho, considere o primeiro vértice ainda não fixado, `y`,
e seu predecessor já fixado, `x`. Ao processar `x`, o relaxamento já teria
atribuído a `y` uma estimativa no máximo igual ao custo do prefixo até `y`.
Como o restante do caminho tem custo não negativo, teríamos `d[y] < d[u]`.
Isso contradiz a escolha de `u` como menor estimativa. Logo, fixar `u` é seguro.
A explicação acompanha a [aula de Dijkstra do MIT](https://courses.csail.mit.edu/6.006/fall11/lectures/lecture16.pdf).

### Contraexemplo com peso negativo

Considere `A → B = 2`, `A → C = 5`, `C → B = -4` e `B → D = 2`.
Não existe ciclo nesse grafo.

Uma versão de Dijkstra que ignorasse a restrição fixaria A, B, D e C,
retornando `d(B)=2` e `d(D)=4`. Porém, `A → C → B` custa 1 e
`A → C → B → D` custa 3. A aresta negativa melhora um vértice já fixado,
invalidando o argumento anterior. Um peso negativo pode causar erro, mesmo
sem um ciclo negativo; isso não significa que toda entrada negativa falhe.

```bash
python contraexemplo.py
```

Esse arquivo é uma demonstração deliberadamente incorreta fora das restrições.
O resolvedor principal rejeita a entrada antes de iniciar a busca.

## Complexidade e pertinência à classe P

Nesta implementação Python, selecionar o próximo vértice custa `O(V)` e
ocorre no máximo `V` vezes. Cada aresta é examinada no máximo uma vez na busca;
a validação inicial também percorre vértices e arestas. Assim:

- **Tempo:** `O(V² + E)`, ou `O(V²)` no grafo simples representado aqui.
- **Espaço auxiliar:** `O(V)` para distâncias, prioridades, predecessores e visitados.
- **Armazenamento da entrada:** `O(V + E)` para as listas de adjacência.

Esses limites contam operações aritméticas e acessos a dicionários/conjuntos
com custo constante esperado. Inteiros muito grandes exigem considerar o
custo em bits das somas e comparações, que continua polinomial no tamanho da
entrada. Para pesos inteiros codificados em binário com até `b` bits, uma
distância ótima finita pode ser representada com `O(b + log V)` bits, pois há
um caminho ótimo simples com no máximo `V-1` arestas. Pesos racionais com
codificação finita também admitem aritmética exata de custo polinomial.

Formalmente, **P é uma classe de problemas de decisão**. A pergunta
“existe caminho de `s` até `t` com custo no máximo `K`?” pertence a P:
calculamos as distâncias e verificamos se `δ(s,t) ≤ K`. A versão que calcula
as distâncias é um problema de função resolvido em tempo polinomial (FP).
É nesse sentido que o problema de otimização do trabalho é tratável em tempo
polinomial. Para as definições, veja a [aula de complexidade do MIT](https://courses.csail.mit.edu/6.006/fall11/lectures/lecture23.pdf).

Uma versão com heap binário e operações adequadas pode atingir
`O((V + E) log V)`. O Python deste trabalho usa seleção linear para facilitar
a explicação; os tempos medidos não substituem a análise assintótica.

## Aplicações: como modelar situações reais

| Situação | Vértices | Arestas e pesos | Utilidade da fonte única |
|---|---|---|---|
| Entregas a partir de um depósito | Cruzamentos e endereços | Ruas, com distância ou tempo não negativo | Calcular custos mínimos do depósito até cada endereço. |
| Comunicação em rede | Roteadores | Conexões, com latência ou custo administrativo não negativo | Obter custos de encaminhamento a partir de um roteador. |
| Deslocamento em jogos | Posições ou regiões | Movimentos, com custo de terreno | Encontrar posições mais baratas de alcançar a partir do personagem. |

São modelos ilustrativos. Os pesos são considerados fixos durante uma busca.
O algoritmo não resolve, por si só, a ordem de visita de várias entregas, nem
adapta rotas automaticamente a alterações de trânsito.

## Bônus: A* e heurísticas

A* prioriza `f(v) = g(v) + h(v)`: custo já percorrido mais estimativa até o
destino. Como a implementação não reabre vértices fixados, exige uma
heurística **consistente**: `h(u) ≤ w(u,v) + h(v)` para toda aresta, com
`h(destino)=0` e valores finitos não negativos. A validação verifica essas
condições no grafo inteiro. Apenas ser admissível (não superestimar o custo
restante) não basta para esta versão sem reabertura. Veja as
[notas de busca informada da UC Berkeley](https://inst.eecs.berkeley.edu/~cs188/fa22/assets/notes/cs188-fa22-note02.pdf).

Sem `--heuristica`, usa-se `h=0`, equivalente a Dijkstra, inclusive na ordem de
visita com os mesmos empates. Pequenas diferenças de tempo são ruído de medição;
não demonstram superioridade do A*. Ambos compartilham o núcleo de busca.

Um exemplo didático com estimativas não nulas:

```bash
python main.py exemplos/desvios.json A D \
  --heuristica exemplos/heuristica_desvios.json \
  --relatorio resultados/heuristica.json \
  --comparacao resultados/heuristica.png
```

Nesse grafo, A* fixa 3 vértices e Dijkstra fixa 4; ambos encontram `A → C → D`,
de custo 4. O arquivo de heurística contém estimativas para **esse destino D**:
`A=4, B=10, C=2, D=0`. Esses valores foram calculados manualmente para um exemplo
pequeno e não representam o custo de construir uma heurística em uma aplicação
real. Menos vértices fixados não garante menor tempo total, pois há validação
adicional. Com estimativa `O(1)` por vértice, ambos mantêm o limite
`O(V² + E)` nesta implementação sobre um grafo explícito.

## Gerenciamento de datasets

### Formatos

JSON preferencial: objeto de adjacência, como `grafo.json`:

```json
{"A": {"B": 4, "C": 1}, "B": {"D": 1}, "C": {"B": 2, "D": 5}, "D": {}}
```

Também se aceita um envelope com a única chave `grafo` ou `graph` contendo
um grafo não vazio. CSV preferencial: `origem,destino,peso`, nesta ordem:

```csv
origem,destino,peso
A,B,4
A,C,1
B,D,1
C,B,2
C,D,5
isolado,,
```

Uma linha com destino e peso vazios declara um vértice isolado. O cabeçalho
antigo `source,target,weight` continua aceito. A gravação usa português.

| Dataset incluído | Características | Consulta sugerida |
|---|---|---|
| `grafo.json` | 10 vértices, 26 arcos; mesmo grafo da referência C | `0 → 9`, custo 9 |
| `grafo.csv` | 4 vértices, 5 arcos; menos arestas não implica menor custo | `A → D`, custo 4 |
| `exemplos/desvios.json` | 4 vértices; permite demonstrar orientação por heurística | `A → D`, custo 4 |
| `exemplos/desconexo.json` | Aresta de custo zero e vértice isolado | `A → D`, inalcançável |

`exemplos/heuristica_desvios.json` é uma tabela de estimativas, não um grafo.
Os datasets são exemplos didáticos, não dados coletados de uma aplicação real.

### Geração e experimentos reproduzíveis

```bash
python experimentos.py --saida resultados/experimentos --repeticoes 15 --semente 42
```

Gera seis grafos: 10, 50 e 100 vértices, cada tamanho com probabilidade de aresta
0,1 e 0,5. Para cada par ordenado de vértices distintos, a inclusão de uma
aresta é sorteada independentemente; os pesos são inteiros de 1 a 100.
A geração custa `O(V²)`, pode produzir grafos desconexos e não garante caminhos.
A semente permite repetir os dados no mesmo ambiente Python.

A pasta contém os seis datasets, relatórios consolidados JSON/CSV/HTML e
`ambiente.json` com versão do Python, sistema e parâmetros. São comparadas as
consultas de `0` até o último vértice. A* usa heurística zero nesses grafos.
O script cria a pasta de saída e substitui arquivos homônimos ao ser repetido.
Para usar a geração diretamente: `GerenciadorDeDados.aleatorio(50, 0.2, 42)`;
`salvar(grafo, caminho)` exporta JSON ou CSV.

## Métricas, relatórios e visualização

| Métrica/campo | Interpretação |
|---|---|
| `distancia`, `alcancavel`, `caminho` | Qualidade da solução, existência e sequência de vértices. |
| `arestas_caminho` | Número de arestas do caminho; zero também ocorre quando não há caminho, então consulte `alcancavel`. |
| `vertices_expandidos` | Vértices retirados para fixação; inclui origem e destino, mesmo que suas arestas não sejam examinadas. |
| `tempo_execucao_ms` | Mediana das execuções medidas, em milissegundos. |
| `desvio_tempo_ms` | Desvio padrão populacional dos tempos, em milissegundos. |
| `repeticoes`, `vertices`, `arestas` | Número de medições e tamanho da instância; arcos opostos contam separadamente. |
| `origem`, `destino`, `conjunto_dados`, `heuristica` | Contexto da consulta; a heurística aparece nos relatórios de comparação. |
| `complexidade` | Limite teórico, não uma estimativa derivada do cronômetro. |

Há uma execução de aquecimento por algoritmo e sete repetições por padrão.
A ordem dos algoritmos alterna entre repetições. A medição inclui validação,
cálculo da heurística e reconstrução do caminho; exclui leitura, impressão,
exportação e gráficos. Uma tabela de heurística já carregada não inclui no
tempo o esforço de produzi-la. Um único par por dataset é uma amostra limitada;
para conclusões mais gerais, varie também sementes e pares de vértices.

JSON mantém caminhos como listas e usa `null` para distância inalcançável.
CSV e HTML apresentam o caminho como texto. O HTML escapa os dados de entrada.
Para escolher o formato, altere a extensão:

```bash
python main.py grafo.csv A D --relatorio resultados/comparacao.csv
python main.py grafo.csv A D --relatorio resultados/comparacao.html
python main.py exemplos/desconexo.json A D --relatorio resultados/desconexo.json
```

`--grafico` desenha o grafo, preserva isolados e destaca o caminho selecionado
em vermelho. `--comparacao` gera barras de distância, tempo e vértices fixados.
As imagens são salvas sem abrir uma janela; desenhos grandes podem ficar pouco
legíveis. O custo do posicionamento visual não está incluído na complexidade
de Dijkstra. Os arquivos `grafo.png`, `relatorio.json` e `report.json` na raiz
são resultados anteriores preservados, com esquema/tempos da versão anterior;
use `resultados/` para gerar a versão atual.

## Docker

```bash
docker build -t caminhos-minimos .
docker run --rm --user "$(id -u):$(id -g)" -e MPLCONFIGDIR=/tmp/matplotlib \
  -v "$(pwd):/app" caminhos-minimos grafo.json 0 \
  --relatorio resultados/distancias.json
docker run --rm --user "$(id -u):$(id -g)" -e MPLCONFIGDIR=/tmp/matplotlib \
  -v "$(pwd):/app" caminhos-minimos grafo.csv A D \
  --relatorio resultados/comparacao.json --comparacao resultados/metricas.png
docker run --rm --entrypoint python caminhos-minimos -m pytest -q
```

Esses exemplos usam um shell Linux/macOS e a pasta `resultados` criada na
instalação. A opção `--user` evita criar relatórios pertencentes ao usuário
root do contêiner. O Docker usa Python 3.11. Testes sem volume verificam os
arquivos copiados para a imagem; reconstrua a imagem após alterar o código.

## Arquivos complementares: C e MATLAB

A entrega obrigatória é Python. `main.c` é uma referência complementar com
matriz fixa de 10 vértices, origem 0 e heap mínimo; o grafo corresponde a
`grafo.json`. Nesta matriz, **zero representa ausência de aresta**, portanto
não serve para demonstrar pesos zero. A busca linear da posição no heap e a
matriz tornam inadequado atribuir a ela o limite de uma implementação
otimizada com heap indexado: generalizada, tem limite `O(V² + EV)`.

```bash
mkdir -p build/Debug
gcc -std=c11 -Wall -Wextra -Wpedantic -g main.c -o build/Debug/outDebug
./build/Debug/outDebug
```

`gerar_graficos_relatorio.m` é uma alternativa de visualização para
**MATLAB R2020a ou posterior**. Recebe um relatório de comparação (duas linhas,
com métricas), e não o relatório de todas as distâncias:

```matlab
gerar_graficos_relatorio("resultados/comparacao.json", "resultados/matlab")
```

Cria `resultados/matlab/comparacao_algoritmos.png`. MATLAB é opcional;
a mesma comparação já pode ser gerada inteiramente em Python.

## Organização, limpeza e SOLID

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Argumentos, coordenação e mensagens do terminal. |
| `grafo.py` | Tipos e validação pura das restrições. |
| `algoritmos.py` | Núcleo compartilhado, predecessores e consultas com A*/Dijkstra. |
| `dijkstra.py` | Interface que retorna todas as distâncias da fonte única. |
| `dados.py` | Carregamento, gravação e geração de datasets. |
| `avaliacao.py` | Medição de algoritmos recebidos como funções. |
| `complexidade.py` | Textos dos limites teóricos usados nos relatórios. |
| `relatorios.py` | Exportação das tabelas em três formatos. |
| `visualizacao.py` | Desenho dos grafos e das métricas. |
| `experimentos.py` | Experimentos com diferentes tamanhos e densidades. |
| `contraexemplo.py` | Demonstração isolada da falha com peso negativo. |
| `test_dijkstra.py`, `test_recursos.py` | Testes unitários e de integração. |
| `requirements.txt`, `Dockerfile`, `.dockerignore` | Dependências e ambiente Docker. |
| `requirements-dev.txt`, `ruff.toml` | Dependências e convenções para análise estática e formatação. |
| `.gitignore`, `.vscode/` | Exclusão de arquivos gerados e configuração opcional do editor. |
| `main.c`, `gerar_graficos_relatorio.m` | Referência C e gráficos MATLAB opcionais. |

Os nomes próprios do projeto usam português, `snake_case` e anotações de tipo.
Nomes obrigatórios de bibliotecas e ferramentas (`main.py`, `test_`, `weight`,
`Dockerfile`, `README.md`) seguem suas convenções. Os antigos módulos
`algorithms`, `datasets`, `evaluation`, `reports`, `visualization` e `complexity`
foram renomeados; código externo deve atualizar os imports.

A separação de responsabilidades aplica **SRP**. A avaliação recebe funções
com o mesmo contrato, permitindo acrescentar algoritmos sem alterar o medidor
(**OCP** e redução do acoplamento conforme **DIP**). Os algoritmos compartilham
a busca para evitar duplicação. **LSP** e **ISP** são princípios voltados a
subtipos e interfaces; aqui não há hierarquia de herança que exija essa análise.
Não se declara uma certificação “100% SOLID”: a organização é modular e
proporcional ao trabalho acadêmico, com funções pequenas e contratos explícitos.

## Verificação e roteiro para apresentação

```bash
python -m pytest -q
python -m unittest -q
```

`pytest` executa toda a suíte. `unittest` executa apenas os testes de
`test_dijkstra.py`; não substitui a verificação dos recursos adicionais.
Para conferir a padronização, instale `requirements-dev.txt` e execute
`ruff check .` e `ruff format --check .`.
Os testes abrangem casos normais e limites, formatos, heurísticas, terminal,
gráficos e relatórios. Em grafos aleatórios, as distâncias são conferidas
contra Bellman–Ford do NetworkX, que não é usado para resolver as consultas
na implementação entregue.
