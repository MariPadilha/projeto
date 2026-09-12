function gerar_graficos_relatorio(caminho_relatorio, pasta_saida)
    if nargin < 2
        pasta_saida = "graficos";
    end

    dados = jsondecode(fileread(caminho_relatorio));
    campos = {'algoritmo', 'distancias', 'tempo_execucao_ms', 'desvio_tempo_ms'};
    if isempty(dados) || ~isstruct(dados) || ~all(isfield(dados, campos))
        error("Informe um relatório de avaliação do vetor completo de distâncias.");
    end
    if ~isfolder(pasta_saida)
        mkdir(pasta_saida);
    end

    algoritmos = string({dados.algoritmo});
    if numel(unique(algoritmos)) ~= numel(algoritmos)
        error("Use o relatório de uma única origem, sem algoritmos repetidos.");
    end
    tempos = [dados.tempo_execucao_ms];
    desvios = [dados.desvio_tempo_ms];

    figura = figure("Visible", "off", "Position", [100 100 1400 450]);
    limpeza = onCleanup(@() close(figura));
    disposicao = tiledlayout(figura, 1, 2, "TileSpacing", "compact");

    nexttile(disposicao);
    bar(categorical(algoritmos), tempos);
    title("Tempo de execução mediano");
    ylabel("Milissegundos");
    grid on;

    nexttile(disposicao);
    bar(categorical(algoritmos), desvios);
    title("Desvio padrão do tempo");
    ylabel("Milissegundos");
    grid on;

    sgtitle("Cálculo do vetor completo de distâncias");
    exportgraphics(figura, fullfile(pasta_saida, "comparacao_algoritmos.png"));
end
