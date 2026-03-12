        function filtrarPorGrupoProximo(grupo) {
            const url = new URL(window.location);
            if (grupo === 'todos') {
                url.searchParams.delete('grupo_filtro_proximo');
            } else {
                url.searchParams.set('grupo_filtro_proximo', grupo);
            }
            url.searchParams.delete('page_proximo');
            window.location.href = url.toString();
        }

        function filtrarPorGrupoPendiente(grupo) {
            const url = new URL(window.location);
            if (grupo === 'todos') {
                url.searchParams.delete('grupo_filtro_pendiente');
            } else {
                url.searchParams.set('grupo_filtro_pendiente', grupo);
            }
            url.searchParams.delete('page_pendiente');
            window.location.href = url.toString();
        }

        function filtrarPorJornadaPendiente(jornada) {
            const url = new URL(window.location);
            if (jornada === 'todos') {
                url.searchParams.delete('jornada_filtro_pendiente');
            } else {
                url.searchParams.set('jornada_filtro_pendiente', jornada);
            }
            url.searchParams.delete('page_pendiente');
            window.location.href = url.toString();
        }

        document.addEventListener('DOMContentLoaded', function() {
            // Hacer las tarjetas clicables pero respetar enlaces/botones internos
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

            const pendienteCards = document.querySelectorAll('#jornadas-pendientes-lista .match-card.proximo');
            pendienteCards.forEach(function(card){
                const url = card.getAttribute('data-url');
                if (!url) return;
                card.addEventListener('click', function(e){
                    if (e.target.closest('a, button, input, select, label, textarea')) return;
                    window.location.href = url;
                });
            });
        });