 document.addEventListener('DOMContentLoaded', function() {
            const jornadaFiltro = document.getElementById('jornadaFiltro');
            const partidos = document.querySelectorAll('#proximos-partidos-lista .match-card');
            jornadaFiltro.addEventListener('change', function() {
                const val = jornadaFiltro.value;
                partidos.forEach(function(card) {
                    if (val === 'todos' || card.getAttribute('data-jornada') === val) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });

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