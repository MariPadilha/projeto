function gerar_graficos_relatorio(caminho_relatorio, pasta_saida)
    % Requer MATLAB R2020a ou posterior; entrada: relatório de comparação.
    if nargin < 2
        pasta_saida = "graficos";
    end

    dados = jsondecode(fileread(caminho_relatorio));
    campos = {'algoritmo', 'distancia', 'tempo_execucao_ms', 'vertices_expandidos'};
    if isempty(dados) || ~isstruct(dados) || ~all(isfield(dados, campos))
        error("Informe um relatório de comparação com origem e destino.");
    end
    if ~isfolder(pasta_saida)
        mkdir(pasta_saida);
    end

    algoritmos = string({dados.algoritmo});
    if numel(unique(algoritmos)) ~= numel(algoritmos)
        error("Use o relatório de uma única consulta, sem algoritmos repetidos.");
    end
    distancias = NaN(1, numel(dados));
    for indice = 1:numel(dados)
        if ~isempty(dados(indice).distancia)
            distancias(indice) = dados(indice).distancia;
        end
    end
    tempos = [dados.tempo_execucao_ms];
    vertices_expandidos = [dados.vertices_expandidos];

    figura = figure("Visible", "off", "Position", [100 100 1400 450]);
    limpeza = onCleanup(@() close(figura));
    disposicao = tiledlayout(figura, 1, 3, "TileSpacing", "compact");

    nexttile(disposicao);
    bar(categorical(algoritmos), distancias);
    title("Distância (NaN = inalcançável)");
    ylabel("Custo do caminho");
    grid on;

    nexttile(disposicao);
    bar(categorical(algoritmos), tempos);
    title("Tempo de execução mediano");
    ylabel("Milissegundos");
    grid on;

    nexttile(disposicao);
    bar(categorical(algoritmos), vertices_expandidos);
    title("Vértices fixados");
    ylabel("Quantidade");
    grid on;

    sgtitle("Comparação dos algoritmos");
    exportgraphics(figura, fullfile(pasta_saida, "comparacao_algoritmos.png"));
end
