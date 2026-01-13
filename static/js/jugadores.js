    let paginaActual = 1;
    const porPagina = 12;

    function expandirFoto(urlFoto, nombreJugador) {
        document.getElementById('fotoExpandida').src = urlFoto;
        document.getElementById('fotoExpandida').alt = nombreJugador;
        document.getElementById('fotoModalLabel').textContent = nombreJugador;
        var modal = new bootstrap.Modal(document.getElementById('fotoModal'));
        modal.show();
    }

    function mostrarPaginaJugadores(pagina) {
        var allItems = Array.from(document.querySelectorAll('.jugador-item'));
        var visibles = allItems.filter(item => item.classList.contains('filtrado'));
        var total = visibles.length;
        var totalPaginas = Math.max(1, Math.ceil(total / porPagina));
        pagina = Math.max(1, Math.min(pagina, totalPaginas));
        paginaActual = pagina;

        // Ocultar todos
        allItems.forEach(function(item) {
            item.style.display = 'none';
        });

        // Mostrar solo los de la página actual
        visibles.forEach(function(item, idx) {
            if (idx >= (pagina-1)*porPagina && idx < pagina*porPagina) {
                item.style.display = 'block';
            }
        });

        // Actualizar paginación
        var paginacion = document.getElementById('paginacionJugadores');
        if (paginacion) {
            paginacion.innerHTML = '';
            
            if (totalPaginas > 1) {
                let pagContainer = document.createElement('div');
                pagContainer.style.display = 'flex';
                pagContainer.style.flexWrap = 'wrap';
                pagContainer.style.justifyContent = 'center';
                pagContainer.style.gap = '0.5rem';
                pagContainer.style.width = '100%';
                
                for (let i = 1; i <= totalPaginas; i++) {
                    let btn = document.createElement('button');
                    btn.textContent = i;
                    btn.className = 'btn btn-lg ' + (i === pagina ? 'btn-primary' : 'btn-outline-primary');
                    btn.style.minWidth = '40px';
                    btn.style.minHeight = '40px';
                    btn.style.fontSize = '1.1em';
                    btn.style.borderRadius = '8px';
                    btn.style.marginBottom = '6px';
                    btn.style.cursor = 'pointer';
                    btn.type = 'button';
                    btn.onclick = function() { 
                        mostrarPaginaJugadores(i); 
                        window.scrollTo({top: document.getElementById('jugadoresLista').offsetTop-60, behavior:'smooth'}); 
                    };
                    pagContainer.appendChild(btn);
                }
                paginacion.appendChild(pagContainer);
            }
        }
    }

    // Reordena las tarjetas según el select de admin
    function sortJugadores(order) {
        const container = document.getElementById('jugadoresLista');
        if (!container) return;
        const items = Array.from(container.querySelectorAll('.jugador-item'));
        if (order === 'default') {
            // opcional: devolver al orden DOM original (por equipo) — aquí simplemente no hacemos nada
            // para mantener la consistencia, podríamos reload = true; pero dejamos el orden actual
        } else {
            items.sort((a, b) => {
                const fa = a.getAttribute('data-fecha') || '';
                const fb = b.getAttribute('data-fecha') || '';
                if (!fa || !fb) return 0;
                const da = new Date(fa);
                const db = new Date(fb);
                if (order === 'ultimos') return db - da; // descendente
                if (order === 'antiguos') return da - db; // ascendente
                return 0;
            });
            // Re-append en el nuevo orden
            items.forEach(item => container.appendChild(item));
        }
        // después de reordenar, recalcula filtrado y paginación
        filtrarJugadores();
    }

    // Event listener para el select admin
    document.addEventListener('DOMContentLoaded', function() {
        const ordenSelect = document.getElementById('ordenJugadores');
        if (ordenSelect) {
            ordenSelect.addEventListener('change', function(e) {
                sortJugadores(e.target.value);
            });
        }
    });

    function filtrarJugadores() {
        var filtroEquipo = document.getElementById('equipoFiltro').value.trim();
        var filtroPosicion = document.getElementById('posicionFiltro').value.trim();
        var filtroNombre = document.getElementById('buscadorNombre').value.trim().toLowerCase();
        
        var items = document.querySelectorAll('.jugador-item');
        var totalJugadores = items.length;
        var visiblesCount = 0;

        items.forEach(function(item) {
            var equipoId = item.getAttribute('data-equipo-id') || '';
            var posicion = item.getAttribute('data-posicion') || '';
            var nombre = (item.getAttribute('data-nombre') || '').toLowerCase();

            var coincideEquipo = (filtroEquipo === '' || equipoId === filtroEquipo);
            var coincidePosicion = (filtroPosicion === '' || posicion === filtroPosicion);
            var coincideNombre = (filtroNombre === '' || nombre.includes(filtroNombre));

            if (coincideEquipo && coincidePosicion && coincideNombre) {
                item.classList.add('filtrado');
                visiblesCount++;
            } else {
                item.classList.remove('filtrado');
            }
        });

        document.getElementById('totalJugadores').textContent = totalJugadores;
        document.getElementById('jugadoresMostrados').textContent = visiblesCount;
        mostrarPaginaJugadores(1);
    }

    document.addEventListener('DOMContentLoaded', function() {
        var items = document.querySelectorAll('.jugador-item');
        
        // Marcar todos como filtrados inicialmente
        items.forEach(function(item) {
            item.classList.add('filtrado');
        });

        // Actualizar contadores
        document.getElementById('totalJugadores').textContent = items.length;
        document.getElementById('jugadoresMostrados').textContent = items.length;
        
        // Mostrar primera página
        mostrarPaginaJugadores(1);

        // Event listeners para filtros
        var equipoFiltro = document.getElementById('equipoFiltro');
        var posicionFiltro = document.getElementById('posicionFiltro');
        var buscadorNombre = document.getElementById('buscadorNombre');

        if (equipoFiltro) {
            equipoFiltro.addEventListener('change', filtrarJugadores);
        }
        if (posicionFiltro) {
            posicionFiltro.addEventListener('change', filtrarJugadores);
        }
        if (buscadorNombre) {
            buscadorNombre.addEventListener('input', filtrarJugadores);
        }

        // Hacer que toda la card del jugador sea clicable (salta a detalle), excepto al clicar la foto
        var cards = document.querySelectorAll('.jugador-item');
        cards.forEach(function(card) {
            var href = card.getAttribute('data-href');
            if (!href) return;
            // add click handler
            card.addEventListener('click', function(e) {
                // si el click fue sobre la imagen (que abre el modal) o sobre un enlace/btn, no navegar
                if (e.target.closest('img') || e.target.closest('a') || e.target.closest('button')) return;
                window.location.href = href;
            });
        });
    });