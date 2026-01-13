        document.addEventListener('DOMContentLoaded', function() {
            const jornadaFiltroRes = document.getElementById('jornadaFiltroResultados');
            const resultados = document.querySelectorAll('#ultimos-resultados-lista .match-card');
            jornadaFiltroRes.addEventListener('change', function() {
                const val = jornadaFiltroRes.value;
                resultados.forEach(function(card) {
                    if (val === 'todos' || card.getAttribute('data-jornada') === val) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });

            // Hacer las tarjetas clicables pero respetar enlaces/botones internos
            resultados.forEach(function(card) {
                const url = card.getAttribute('data-url');
                if (!url) return;
                card.style.cursor = 'pointer';
                card.addEventListener('click', function(e) {
                    // Si el click fue sobre un enlace o botón, no navegamos
                    if (e.target.closest('a') || e.target.closest('button')) return;
                    window.location.href = url;
                });
            });
        });