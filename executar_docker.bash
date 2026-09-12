#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    printf '%s\n' \
        'Uso: bash executar_docker.bash' \
        'Constrói a imagem Docker e executa os exemplos e a geração de datasets.' \
        'Salva relatórios, gráficos e datasets em resultados/.' \
        'Arquivos de saída com o mesmo nome são substituídos.'
    exit 0
fi
if (( $# > 0 )); then
    printf 'Argumento desconhecido: %s. Use --help.\n' "$1" >&2
    exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
    printf 'Erro: instale o Docker antes de executar este script.\n' >&2
    exit 1
fi
if ! docker info >/dev/null; then
    printf 'Erro: verifique se o Docker está em execução e se você tem acesso a ele.\n' >&2
    exit 1
fi

pasta_projeto="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
pasta_resultados="$pasta_projeto/resultados"
imagem="caminhos-minimos"
mkdir -p "$pasta_resultados"

printf '\nConstruindo a imagem Docker...\n'
docker build --tag "$imagem" "$pasta_projeto"

executar_python() {
    docker run --rm \
        --user "$(id -u):$(id -g)" \
        --env MPLCONFIGDIR=/tmp/matplotlib \
        --volume "$pasta_resultados:/app/resultados" \
        --entrypoint python \
        "$imagem" "$@"
}

printf '\nCalculando as distâncias a partir da origem 0...\n'
executar_python main.py exemplos/grafo.json 0 \
    --relatorio resultados/distancias.json

printf '\nComparando Dijkstra e A* e gerando os gráficos...\n'
executar_python main.py exemplos/grafo.csv A D \
    --relatorio resultados/comparacao.json \
    --grafico resultados/grafo.png \
    --comparacao resultados/metricas.png

printf '\nGerando também os relatórios CSV e HTML...\n'
for formato in csv html; do
    executar_python main.py exemplos/grafo.csv A D \
        --relatorio "resultados/comparacao.$formato"
done

printf '\nExecutando A* com a heurística do exemplo de desvios...\n'
executar_python main.py exemplos/desvios.json A D \
    --heuristica exemplos/heuristica_desvios.json \
    --relatorio resultados/heuristica.json \
    --grafico resultados/desvios.png \
    --comparacao resultados/heuristica.png

printf '\nDemonstrando um destino inalcançável...\n'
executar_python main.py exemplos/desconexo.json A D \
    --relatorio resultados/desconexo.json \
    --grafico resultados/desconexo.png

printf '\nDemonstrando a falha de Dijkstra sem validação de pesos negativos...\n'
executar_python exemplos/contraexemplo.py | tee "$pasta_resultados/contraexemplo.txt"

printf '\nGerando seis datasets com a semente 42...\n'
executar_python -m complementos.gerar_dataset \
    --saida resultados/datasets --semente 42

printf '\nConcluído. Resultados salvos em: %s\n' "$pasta_resultados"
