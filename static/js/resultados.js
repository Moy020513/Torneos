        function filtrarPorJornada(jornada) {
            const url = new URL(window.location);
            if (jornada === 'todos') {
                url.searchParams.delete('jornada_filtro');
            } else {
                url.searchParams.set('jornada_filtro', jornada);
            }
            url.searchParams.delete('page');
            window.location.href = url.toString();
        }

        document.addEventListener('DOMContentLoaded', function() {
            // Hacer las tarjetas clicables pero respetar enlaces/botones internos
            const resultados = document.querySelectorAll('#ultimos-resultados-lista .match-card');
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