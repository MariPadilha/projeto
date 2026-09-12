# Caminhos mínimos de fonte única com pesos não negativos

Implementação em **Python**, com Dijkstra e comparação complementar com A*.

## Como executar com Docker

Com o Docker instalado e em execução, abra um terminal na raiz do projeto.
Em um shell Bash (Linux/macOS ou WSL), execute:

```bash
bash executar_docker.bash
```

O script constrói a imagem, calcula as distâncias, compara Dijkstra e A*,
gera relatórios JSON/CSV/HTML e gráficos, executa os exemplos de heurística,
grafo desconexo e pesos negativos e gera seis datasets com semente 42.
As saídas ficam em `resultados/`; arquivos com o mesmo nome são substituídos.
Use `bash executar_docker.bash --help` para consultar a ajuda.

Para executar apenas uma consulta manualmente em Linux/macOS:

```bash
mkdir -p resultados
docker build -t caminhos-minimos .
docker run --rm --user "$(id -u):$(id -g)" -e MPLCONFIGDIR=/tmp/matplotlib \
  -v "$(pwd):/app" caminhos-minimos exemplos/grafo.json 0 \
  --relatorio resultados/distancias.json
docker run --rm --user "$(id -u):$(id -g)" -e MPLCONFIGDIR=/tmp/matplotlib \
  -v "$(pwd):/app" caminhos-minimos exemplos/grafo.csv A D \
  --relatorio resultados/comparacao.json --comparacao resultados/metricas.png
```

Os relatórios e gráficos ficam na pasta `resultados/` do projeto.
A opção `--user` evita criar relatórios pertencentes ao usuário
root do contêiner. O Docker usa Python 3.11 e inclui o programa, seus complementos,
os exemplos e as dependências de execução. O script MATLAB requer uma instalação
separada do MATLAB. Reconstrua a imagem após alterar o código.

## Integrantes

| Integrante | Matrícula |
|---|---:|
| Mariana Padilha | 2410100712 |
| Emanuel Carricio | 223941292 |
| Matheus Ciocca | 239999999 |
| Rafaela Nunes | 2188988983 |
| Livia Barbosa | 249898898 |

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
| Saída | Vetor de distâncias mínimas da origem até todos os vértices, na ordem de inserção das chaves do grafo. |
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

No VS Code, use as extensões Python e Python Debugger, selecione o ambiente
`.venv` e execute a configuração **Depurar caminhos mínimos** com F5.
Ela chama `main.py` com `exemplos/grafo.json`, origem `0`, e salva o relatório
em `resultados/distancias.json`. A descoberta de testes usa `pytest` em `tests/`.

### Resolver o enunciado: uma origem, todos os vértices

```bash
python main.py exemplos/grafo.json 0 --relatorio resultados/distancias.json
```

Distâncias esperadas:

| Vértice | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Distância | 0 | 2 | 5 | 1 | 4 | 5 | 5 | 8 | 10 | 9 |

A função equivalente é `dijkstra(grafo, origem)`, em `caminhos_minimos/algoritmos.py`.
Ela e `buscar(grafo, origem)` retornam uma lista com todas as distâncias definitivas:

```python
[0, 2, 5, 1, 4, 5, 5, 8, 10, 9]
```

A posição `i` corresponde ao vértice `list(grafo)[i]`; a ordem não é ordenada
automaticamente pelo nome do vértice. A origem tem distância zero e vértices
inalcançáveis recebem `math.inf`. O terminal mostra os vértices e o vetor nessa ordem.
O relatório contém uma linha por algoritmo, com o vetor completo, a ordem dos
vértices e as métricas de tempo. Sem destino, avalia somente Dijkstra.

### Comparar o cálculo do vetor completo com Dijkstra e A*

```bash
python main.py exemplos/grafo.json 0 9 \
  --repeticoes 15 \
  --relatorio resultados/comparacao.json \
  --grafico resultados/grafo.png \
  --comparacao resultados/metricas.png
```

O terminal mostra **todas** as distâncias. Neste modo, o relatório contém duas
linhas, uma por algoritmo, com o mesmo vetor completo. O destino `9` orienta a
heurística do A*, mas a busca continua até esgotar os vértices alcançáveis.
Todas as execuções medidas calculam o vetor inteiro a partir da mesma origem.
Quando solicitado com `--grafico`, o caminho `0 → 3 → 4 → 6 → 7 → 9`, de custo 9,
é reconstruído separadamente para destaque na imagem, fora da medição.
`dijkstra_com_caminho()` e `a_estrela()` retornam o custo até esse destino,
o caminho e a contagem de vértices fixados. O estado parcial dessas consultas
fica interno. `buscar()`, `dijkstra()` e `a_estrela_distancias()` entregam o
vetor completo; a avaliação usa as duas últimas funções.

Use `python main.py --help` para listar as opções. A saída padrão é
`resultados/relatorio.json`; um arquivo existente nesse caminho será substituído.
A pasta do relatório é criada automaticamente. Para as imagens, crie a pasta de saída previamente. As opções antigas `--report` e `--plot`
continuam aceitas por compatibilidade, mas os exemplos usam português.

## Funcionamento e correção de Dijkstra

1. Inicializa a origem com distância zero e os demais vértices com infinito.
2. Seleciona, por busca linear, o vértice ainda não fixado de menor estimativa.
3. Se a menor estimativa é infinita, encerra: os restantes são inalcançáveis.
4. Fixa o vértice e relaxa suas arestas: se `d[u] + w(u,v) < d[v]`, atualiza
   a distância e registra `u` como predecessor de `v`.
5. Repete até esgotar os alcançáveis. Na consulta a um destino, pode parar
   quando esse destino é fixado.

Exemplo de `exemplos/grafo.csv`, origem A (valores após o relaxamento):

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
python exemplos/contraexemplo.py
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

As funções `a_estrela()` e `a_estrela_distancias()` ficam em
`complementos/a_estrela.py`. Para usar a API diretamente:

```python
from complementos.a_estrela import a_estrela, a_estrela_distancias
```

A* prioriza `f(v) = g(v) + h(v)`: custo já percorrido mais estimativa até o
destino. Como a implementação não reabre vértices fixados, exige uma
heurística **consistente**: `h(u) ≤ w(u,v) + h(v)` para toda aresta, com
`h(destino)=0` e valores finitos não negativos. A validação verifica essas
condições no grafo inteiro. Apenas ser admissível (não superestimar o custo
restante) não basta para esta versão sem reabertura. Veja as
[notas de busca informada da UC Berkeley](https://inst.eecs.berkeley.edu/~cs188/fa22/assets/notes/cs188-fa22-note02.pdf).

Sem `--heuristica`, usa-se `h=0`, equivalente a Dijkstra, inclusive na ordem de
visita com os mesmos empates. Pequenas diferenças de tempo não demonstram
superioridade do A*. Ambos compartilham o núcleo de busca.

Um exemplo didático com estimativas não nulas:

```bash
python main.py exemplos/desvios.json A D \
  --heuristica exemplos/heuristica_desvios.json \
  --relatorio resultados/heuristica.json \
  --comparacao resultados/heuristica.png
```

Na consulta isolada até D, `a_estrela()` fixa 3 vértices e
`dijkstra_com_caminho()` fixa 4; ambos encontram `A → C → D`, de custo 4.
Já a avaliação acima mede o vetor completo: `a_estrela_distancias()` continua
após D, processando todos os vértices alcançáveis, assim como Dijkstra.
O arquivo de heurística contém estimativas para **esse destino D**:
`A=4, B=10, C=2, D=0`. Esses valores foram calculados manualmente para um exemplo
pequeno e não representam o custo de construir uma heurística em uma aplicação
real. Menos vértices fixados não garante menor tempo total, pois há validação
adicional. Com estimativa `O(1)` por vértice, ambos mantêm o limite
`O(V² + E)` nesta implementação sobre um grafo explícito.

## Gerenciamento de datasets

### Formatos

JSON preferencial: objeto de adjacência, como `exemplos/grafo.json`:

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
| `exemplos/grafo.json` | 10 vértices, 26 arcos com pesos não negativos | `0 → 9`, custo 9 |
| `exemplos/grafo.csv` | 4 vértices, 5 arcos; menos arestas não implica menor custo | `A → D`, custo 4 |
| `exemplos/desvios.json` | 4 vértices; permite demonstrar orientação por heurística | `A → D`, custo 4 |
| `exemplos/desconexo.json` | Aresta de custo zero e vértice isolado | `A → D`, inalcançável |

`exemplos/heuristica_desvios.json` é uma tabela de estimativas, não um grafo.
Os datasets são exemplos didáticos, não dados coletados de uma aplicação real.

### Geração de datasets reproduzíveis

```bash
python -m complementos.gerar_dataset --saida resultados/datasets --semente 42
```

Gera seis grafos: 10, 50 e 100 vértices, cada tamanho com probabilidade de aresta
0,1 e 0,5. Para cada par ordenado de vértices distintos, a inclusão de uma
aresta é sorteada independentemente; os pesos são inteiros de 1 a 100.
A geração custa `O(V²)`, pode produzir grafos desconexos e não garante caminhos.
A semente permite repetir os dados no mesmo ambiente Python.

A pasta recebe os seis datasets em JSON. A saída padrão é `resultados/datasets`.
O script cria a pasta de saída e substitui arquivos homônimos ao ser repetido.
Para usar a geração diretamente, importe `gerar_grafo_aleatorio` de
`complementos.gerar_dataset` e chame `gerar_grafo_aleatorio(50, 0.2, 42)`.
As funções de `caminhos_minimos.ler_salvar_grafos` cuidam dos arquivos:

```python
from caminhos_minimos.ler_salvar_grafos import carregar_grafo, salvar_grafo

grafo = carregar_grafo("exemplos/grafo.json")
salvar_grafo(grafo, "resultados/copia.csv")
```

## Métricas, relatórios e visualização

| Métrica/campo | Interpretação |
|---|---|
| `distancias` | Vetor com as distâncias mínimas da origem até todos os vértices. |
| `ordem_vertices` | Identifica o vértice correspondente a cada posição do vetor. |
| `tempo_execucao_ms` | Mediana das execuções medidas, em milissegundos. |
| `desvio_tempo_ms` | Desvio padrão populacional dos tempos, em milissegundos. |
| `repeticoes`, `vertices`, `arestas` | Número de medições e tamanho da instância; arcos opostos contam separadamente. |
| `origem`, `conjunto_dados` | Origem da busca completa e arquivo de entrada. |
| `destino_heuristica`, `heuristica` | Referência usada para ordenar a busca completa do A*; aparece na comparação. |
| `complexidade` | Limite teórico, não uma estimativa derivada do cronômetro. |

Há uma execução de aquecimento por algoritmo e sete repetições por padrão.
A ordem dos algoritmos alterna entre repetições. Cada chamada medida inclui
validação, busca completa e construção do vetor de distâncias. Para A*, inclui
também a avaliação e validação da heurística. Exclui leitura, impressão,
exportação, gráficos e a consulta separada usada para destacar um caminho.
Uma tabela de heurística já carregada não inclui no tempo o esforço de produzi-la.
Para conclusões mais gerais, varie sementes, tamanhos dos grafos e origens.

Uso direto da avaliação:

```python
from caminhos_minimos.algoritmos import dijkstra
from complementos.avaliacao import avaliar

resultados = avaliar(grafo, origem, {"dijkstra": dijkstra}, repeticoes=7)
```

Cada função recebida deve aceitar `(grafo, origem)` e retornar uma lista com
uma distância por vértice, na ordem das chaves do grafo. A avaliação verifica
o formato e a estabilidade entre execuções; essa verificação não prova a
correção matemática dos resultados.

JSON mantém o vetor como lista e usa `null` para distância inalcançável.
CSV e HTML apresentam o vetor como texto, com `inalcançável` nas posições sem
caminho. O HTML escapa os dados de entrada.
Para escolher o formato, altere a extensão:

```bash
python main.py exemplos/grafo.csv A D --relatorio resultados/comparacao.csv
python main.py exemplos/grafo.csv A D --relatorio resultados/comparacao.html
python main.py exemplos/desconexo.json A D --relatorio resultados/desconexo.json
```

`--grafico` desenha o grafo, preserva isolados e destaca o caminho selecionado
em vermelho. `--comparacao` gera barras de mediana e desvio padrão dos tempos
de cálculo do vetor completo; também pode ser usado sem destino para Dijkstra.
As imagens são salvas sem abrir uma janela; desenhos grandes podem ficar pouco
legíveis. O custo do posicionamento visual não está incluído na complexidade
de Dijkstra. Use `resultados/` para gerar relatórios e imagens.

## Visualização complementar em MATLAB

`complementos/matlab/gerar_graficos_relatorio.m` é uma alternativa de visualização para
**MATLAB R2020a ou posterior**. Recebe o relatório de avaliação do vetor completo,
com uma linha por algoritmo e métricas de tempo:

```matlab
addpath("complementos/matlab")
gerar_graficos_relatorio("resultados/comparacao.json", "resultados/matlab")
```

Cria `resultados/matlab/comparacao_algoritmos.png`. MATLAB é opcional;
a mesma comparação já pode ser gerada inteiramente em Python.

## Organização, limpeza e SOLID

```text
.
├── caminhos_minimos/
├── tests/
├── exemplos/
├── complementos/
│   ├── __init__.py
│   ├── a_estrela.py
│   ├── avaliacao.py
│   ├── gerar_dataset.py
│   ├── relatorios.py
│   ├── visualizacao.py
│   └── matlab/
├── resultados/
├── main.py
├── README.md
├── Dockerfile
├── executar_docker.bash
├── requirements.txt
└── requirements-dev.txt
```

Execute os comandos a partir da raiz. Para usar a API Python, importe o pacote,
por exemplo: `from caminhos_minimos.algoritmos import dijkstra`.

`caminhos_minimos/` reúne Dijkstra, a estrutura do grafo e sua leitura e gravação.
`complementos/` reúne A*, avaliação dos algoritmos, geração de datasets,
exportação de relatórios e gráficos em Python e MATLAB. Os exemplos de entrada ficam em `exemplos/`, os testes em
`tests/` e os arquivos gerados em `resultados/`.

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada, argumentos, coordenação e mensagens do terminal. |
| `caminhos_minimos/grafo.py` | Tipos e validação pura das restrições. |
| `caminhos_minimos/algoritmos.py` | Consultas com Dijkstra, com vetor completo ou caminho até um destino. |
| `caminhos_minimos/_busca.py` | Núcleo interno de busca, validação de heurísticas e reconstrução de caminhos, compartilhado por Dijkstra e A*. |
| `complementos/a_estrela.py` | Consultas complementares com A*, com vetor completo ou caminho até um destino. |
| `caminhos_minimos/ler_salvar_grafos.py` | Leitura e gravação de grafos em arquivos JSON e CSV. |
| `complementos/avaliacao.py` | Medição de algoritmos recebidos como funções e textos dos limites teóricos usados nos relatórios. |
| `complementos/relatorios.py` | Exportação das tabelas em três formatos. |
| `complementos/visualizacao.py` | Desenho dos grafos e das métricas. |
| `complementos/gerar_dataset.py` | Geração e gravação de datasets de grafos aleatórios em JSON. |
| `exemplos/contraexemplo.py` | Demonstração isolada da falha com peso negativo. |
| `tests/test_dijkstra.py`, `tests/test_recursos.py` | Testes unitários e de integração. |
| `requirements.txt`, `Dockerfile`, `.dockerignore` | Dependências e ambiente Docker. |
| `executar_docker.bash` | Construção da imagem e execução dos exemplos e da geração de datasets com Docker. |
| `requirements-dev.txt` | Dependências para testes, análise estática e formatação. |
| `.gitignore`, `.vscode/` | Exclusão de arquivos gerados e configuração opcional do editor. |
| `complementos/matlab/gerar_graficos_relatorio.m` | Gráficos MATLAB opcionais. |

Os nomes próprios do projeto usam português, `snake_case` e anotações de tipo.
Nomes obrigatórios de bibliotecas e ferramentas (`main.py`, `test_`, `weight`,
`Dockerfile`, `README.md`) seguem suas convenções. Os módulos Python ficam nos
pacotes `caminhos_minimos` e `complementos`.

A separação de responsabilidades aplica **SRP**. A avaliação recebe funções
com o mesmo contrato, permitindo acrescentar algoritmos sem alterar o medidor
(**OCP** e redução do acoplamento conforme **DIP**). Os algoritmos compartilham
a busca para evitar duplicação. **LSP** e **ISP** são princípios voltados a
subtipos e interfaces; aqui não há hierarquia de herança que exija essa análise.
Não se declara uma certificação “100% SOLID”: a organização é modular e
proporcional ao trabalho acadêmico, com funções pequenas e contratos explícitos.

## Verificação e roteiro para apresentação

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m unittest -q
```

`pytest` executa toda a suíte. `unittest` executa apenas os testes de
`tests/test_dijkstra.py`; não substitui a verificação dos recursos adicionais.
Para verificar erros básicos e a formatação sem um arquivo de configuração, execute:

```bash
ruff check --isolated --select E4,E7,E9,F .
ruff format --isolated --check .
```

Os testes abrangem casos normais e limites, formatos, heurísticas, terminal,
gráficos e relatórios. Em grafos aleatórios, as distâncias são conferidas
contra Bellman–Ford do NetworkX, que não é usado para resolver as consultas
na implementação entregue.
