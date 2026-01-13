// Funciones para gráficas de estadísticas
function getGolesPorJornada(partidos, jornadasCategoria, equipoId) {
            // Usar la lista completa de jornadas de la categoría para el eje X
            // y rellenar con ceros las jornadas que no tengan goles en la muestra.
            var jornadaNums = (jornadasCategoria || []).slice().map(function(x){ return parseInt(x,10); }).filter(function(n){ return !isNaN(n); }).sort(function(a,b){ return a - b; });
            var golesMap = {};
            jornadaNums.forEach(function(n){ golesMap[n] = 0; });

            partidos.forEach(function(p) {
                var jornadaLabel = p.jornada || '';
                var jornadaNum = parseInt((jornadaLabel + '').replace(/^J/i, ''), 10);
                if (isNaN(jornadaNum)) return;

                var goles = 0;
                if (equipoId === 'todos') {
                    goles = (p.goles_local || 0) + (p.goles_visitante || 0);
                } else if (String(p.equipo_local_id) === equipoId) {
                    goles = p.goles_local || 0;
                } else if (String(p.equipo_visitante_id) === equipoId) {
                    goles = p.goles_visitante || 0;
                } else {
                    return;
                }

                if (golesMap[jornadaNum] === undefined) golesMap[jornadaNum] = 0;
                golesMap[jornadaNum] += goles;
            });

        var jornadas = jornadaNums.map(function(n){ return 'J' + n; });
        var golesPorJornada = jornadaNums.map(function(n){ return golesMap[n] || 0; });
        return { jornadas: jornadas, golesPorJornada: golesPorJornada };
}

function initEstadisticasChart(partidos, jornadasCategoria) {
    var ctx = document.getElementById('golesJornadaChart').getContext('2d');
    var equipoFiltro = document.getElementById('equipoFiltro');
    
    var chartData = getGolesPorJornada(partidos, jornadasCategoria, 'todos');
    // Ajustar ancho mínimo del canvas: en móvil queremos que quepan 10 jornadas
    var canvas = document.getElementById('golesJornadaChart');
    var chartInner = canvas.parentElement;
    var chartScroll = chartInner.parentElement;
    // ancho visible disponible para la gráfica (fallback a innerWidth si no está calculado aún)
    var visibleWidth = (chartScroll && chartScroll.clientWidth) || (window.innerWidth - 32);
    var isMobile = window.innerWidth < 768 || visibleWidth < 480;
    if (isMobile) {
        // en móvil: asegurarnos que 10 labels quepan en el ancho visible
        var perLabelWidth = Math.max(24, Math.floor(visibleWidth / 10));
    } else {
        // en desktop: distribuir hasta 10 labels en el ancho pero no exceder 60px por etiqueta
        var maxVisible = Math.min(10, Math.max(1, chartData.jornadas.length));
        var perLabelWidth = Math.floor(visibleWidth / maxVisible);
        perLabelWidth = Math.max(24, Math.min(60, perLabelWidth));
    }
    var desiredWidth = Math.max(visibleWidth, chartData.jornadas.length * perLabelWidth);
    chartInner.style.minWidth = desiredWidth + 'px';
        var chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.jornadas,
                datasets: [{
                    label: 'Goles por Jornada',
                    data: chartData.golesPorJornada,
                    backgroundColor: '#08F7FE',
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

    equipoFiltro.addEventListener('change', function() {
        var equipoId = equipoFiltro.value;
        var data = getGolesPorJornada(partidos, jornadasCategoria, equipoId);
            chart.data.labels = data.jornadas;
            chart.data.datasets[0].data = data.golesPorJornada;
            // Ajustar ancho mínimo según nuevas jornadas
            // recalcular ancho teniendo en cuenta el área visible; mantener regla de 10 labels en móvil
            var visible = (chartInner.parentElement && chartInner.parentElement.clientWidth) || (window.innerWidth - 32);
            var mobile = window.innerWidth < 768 || visible < 480;
            if (mobile) {
                var perW = Math.max(24, Math.floor(visible / 10));
            } else {
                var maxVis = Math.min(10, Math.max(1, data.jornadas.length));
                var perW = Math.floor(visible / maxVis);
                perW = Math.max(24, Math.min(60, perW));
            }
            var newWidth = Math.max(visible, data.jornadas.length * perW);
            chartInner.style.minWidth = newWidth + 'px';
            chart.data.datasets[0].label = equipoId === 'todos' ? 'Goles por Jornada' : 'Goles por Jornada (equipo)';
        chart.update();
        // Forzar resize para que Chart.js recalcule tamaños
        try { chart.resize(); } catch (e) {}
    });
}