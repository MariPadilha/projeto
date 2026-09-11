# Registro da revisão

Revisão realizada em 11/09/2026, considerando o enunciado fornecido e os
arquivos do projeto. As correções estão aplicadas no diretório de trabalho.

## Atendimento ao enunciado após os ajustes

| Requisito | Evidência |
|---|---|
| Algoritmo em Python | `dijkstra.py` e núcleo compartilhado em `algoritmos.py`. |
| Distâncias da origem a todos os vértices | `python main.py grafo.json 0`; teste das dez distâncias esperadas. |
| Instância, entrada, saída e restrições | Seção inicial do README e validação de todo o grafo. |
| Complexidade e classe P | Derivação de tempo/espaço e distinção entre decisão em P e função em FP no README. |
| Justificativa gulosa | Invariante e argumento por contradição no README. |
| Falha com peso negativo | Contraexemplo explicado, executável e testado em `contraexemplo.py`. |
| Aplicações | Modelos de entregas, comunicação em rede e deslocamento em jogos. |
| Gerenciamento de datasets | JSON/CSV, validação, preservação de isolados e geração com semente. |
| Múltiplas métricas | Custo, caminho, alcance, vértices fixados, tempo mediano e dispersão. |
| Visualização | Imagem do grafo e comparação das métricas em Python. |
| Relatórios | JSON, CSV e HTML; experimentos consolidados com parâmetros e ambiente. |
| Bônus A* | Heurística zero e exemplo consistente não nulo, com redução de vértices fixados. |

## Problemas encontrados e corrigidos

- A interface exigia destino e não exibia a saída completa de fonte única.
- A validação durante a busca deixava passar arestas negativas em partes não
  visitadas; valores booleanos, NaN e infinitos também não eram tratados corretamente.
- A* aceitava heurísticas sem verificar as condições necessárias à versão sem
  reabertura de vértices.
- JSON podia exportar `Infinity`, que não pertence ao formato JSON padrão.
- HTML interpolava diretamente os rótulos da entrada.
- A visualização omitia vértices isolados.
- A gravação de datasets sempre usava JSON, independentemente da extensão.
- Havia pouca cobertura de casos limites, apenas uma medição de tempo e
  mistura de nomes de módulos e cabeçalhos em português e inglês.
- Faltavam no README partes centrais da teoria, instalação local completa,
  limites da comparação e distinção entre as implementações Python e C.
- A referência C possuía funções/campos sem uso e não verificava falhas de
  alocação nem protegia a soma após encontrar um vértice inalcançável.
- O repositório continha bytecode Python gerado; ele foi removido e incluído
  nas regras de exclusão, junto com ambiente virtual e resultados novos.

## Verificações concluídas

| Verificação | Resultado |
|---|---|
| Suíte completa local, Python 3.10.12 | **66 testes passaram**. |
| Suíte completa no Docker, Python 3.11 | **66 testes passaram**. |
| `unittest` | 5 testes básicos passaram; é apenas um subconjunto da suíte. |
| Ruff: análise estática e formatação | Sem erros, 14 arquivos Python padronizados. |
| Dependências instaladas | `pip check` sem conflitos. |
| Referência independente | Comparação com Bellman–Ford do NetworkX em 12 grafos, para todas as origens e destinos. |
| Docker | Imagem `caminhos-minimos:revisao` construída; consulta e gráficos executados sem rede nem volumes. |
| C | GCC com C11, `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror`; compilou e retornou as dez distâncias corretas. |
| Experimentos | Seis datasets e 12 avaliações, exportados em JSON/CSV/HTML com 15 repetições. |
| Imagens | Geração e inspeção visual do grafo e da comparação com heurística. |
| Integridade do diff | `git diff --check` sem problemas. |

Os resultados gerados nesta revisão estão em `resultados/`, incluindo
`distancias.json`, `comparacao.json`, `comparacao.html`, `grafo.png`,
`metricas.png`, `heuristica.json`, `heuristica.png` e `experimentos/`.
Os JSONs de comparação e os gráficos gerais usam `grafo.json`; o HTML de
comparação foi gerado a partir de `grafo.csv`. O diretório é ignorado pelo Git,
mas pode ser incluído no pacote entregue ao professor se desejado.

## Limites da verificação

O script MATLAB foi revisado e ajustado, mas **não foi executado**, pois MATLAB
e Octave não estão instalados. A geração equivalente de gráficos em Python
foi executada. A configuração do depurador no VS Code foi revisada, mas uma
sessão gráfica de depuração não foi iniciada; a extensão C/C++ Runner pode
recriar seu próprio perfil, além do perfil portátil adicionado.

Os resultados antigos da raiz foram preservados e estão identificados como
anteriores no README. Os nomes e matrículas dos integrantes foram preservados
como informados no projeto; não foram verificados em cadastro acadêmico.

SOLID foi aplicado de forma proporcional: responsabilidades separadas,
dependência de funções recebidas pelo avaliador e núcleo compartilhado.
Não foi acrescentada uma hierarquia de classes apenas para demonstrar os
cinco princípios. Os nomes do domínio estão em português; identificadores
exigidos por bibliotecas e ferramentas mantêm suas convenções.
