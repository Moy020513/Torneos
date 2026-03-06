 document.addEventListener('DOMContentLoaded', function() {
            const jornadaFiltro = document.getElementById('jornadaFiltro');
            const grupoFiltro = document.getElementById('grupoFiltro');
            const partidos = document.querySelectorAll('#proximos-partidos-lista .match-card');
            
            function aplicarFiltros() {
                const jornadaVal = jornadaFiltro.value;
                const grupoVal = grupoFiltro ? grupoFiltro.value : 'todos';
                
                partidos.forEach(function(card) {
                    const jornada = card.getAttribute('data-jornada');
                    const grupo = card.getAttribute('data-grupo');
                    
                    const jornadaCoinc = (jornadaVal === 'todos' || jornada === jornadaVal);
                    const grupoCoinc = (grupoVal === 'todos' || grupo === grupoVal);
                    
                    if (jornadaCoinc && grupoCoinc) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
            
            jornadaFiltro.addEventListener('change', aplicarFiltros);
            if (grupoFiltro) {
                grupoFiltro.addEventListener('change', aplicarFiltros);
            }

            // Navegación por clic a detalle del partido (evita interferir con enlaces internos)
            const proximoCards = document.querySelectorAll('#proximos-partidos-lista .match-card.proximo');
            proximoCards.forEach(function(card){
                const url = card.getAttribute('data-url');
                if (!url) return;
                card.addEventListener('click', function(e){
                    // No interceptar si clic en controles interactivos
                    if (e.target.closest('a, button, input, select, label, textarea')) return;
                    window.location.href = url;
                });
            });
        });