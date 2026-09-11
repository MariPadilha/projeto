function gerar_graficos_relatorio(caminho_relatorio, pasta_saida)
    if nargin < 2
        pasta_saida = "graficos";
    end

    dados = jsondecode(fileread(caminho_relatorio));
    if ~isfolder(pasta_saida)
        mkdir(pasta_saida);
    end

    algoritmos = string({dados.algoritmo});
    distancias = [dados.distancia];
    tempos = [dados.tempo_execucao_ms];
    vertices_expandidos = [dados.vertices_expandidos];

    figura = figure("Visible", "off", "Position", [100 100 1400 450]);
    layout = tiledlayout(figura, 1, 3, "TileSpacing", "compact");

    nexttile(layout);
    bar(categorical(algoritmos), distancias);
    title("Distância");
    ylabel("Custo do caminho");
    grid on;

    nexttile(layout);
    bar(categorical(algoritmos), tempos);
    title("Tempo de execução");
    ylabel("Milissegundos");
    grid on;

    nexttile(layout);
    bar(categorical(algoritmos), vertices_expandidos);
    title("Vértices expandidos");
    ylabel("Quantidade");
    grid on;

    sgtitle("Comparação dos algoritmos");
    exportgraphics(figura, fullfile(pasta_saida, "comparacao_algoritmos.png"));
    close(figura);
end
