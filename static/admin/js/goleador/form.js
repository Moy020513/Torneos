document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('goleadorForm');
    const goalDisplay = document.getElementById('goalDisplay');

    function sumJornadaGoles() {
        const inputs = Array.from(form.querySelectorAll('input[name="goles"]'));
        let sum = 0;
        inputs.forEach(i => {
            const v = parseInt(i.value, 10);
            if (!isNaN(v)) sum += v;
        });
        return sum;
    }

    function updateGoalDisplay() {
        goalDisplay.textContent = sumJornadaGoles();
    }

    function validateJornadas() {
        let valid = true;
        const blocks = Array.from(form.querySelectorAll('.jornada-block'));
        blocks.forEach((block, idx) => {
            const selP = block.querySelector('select[name="partido"]');
            const selPe = block.querySelector('select[name="partido_eliminatoria"]');
            const valP = selP ? (selP.value || '') : '';
            const valPe = selPe ? (selPe.value || '') : '';
            // Limpiar errores anteriores
            selP && selP.classList.remove('is-invalid');
            selPe && selPe.classList.remove('is-invalid');
            if ((valP && valPe) || (!valP && !valPe)) {
                // marcar invalid
                if (selP) selP.classList.add('is-invalid');
                if (selPe) selPe.classList.add('is-invalid');
                valid = false;
            }
        });
        return valid;
    }

    // Validación del formulario
    form.addEventListener('submit', function(e) {
        const jornadasValid = validateJornadas();
        updateGoalDisplay();
        if (!jornadasValid) {
            e.preventDefault();
            e.stopPropagation();
            // Mostrar mensaje genérico
            alert('Revise las jornadas: cada fila debe tener exactamente un partido regular o uno de eliminatoria.');
        }
        form.classList.add('was-validated');
    });

    // Recalcular suma cuando cambien inputs/goles/selects
    document.addEventListener('input', function(e) {
        if (e.target && e.target.name === 'goles') updateGoalDisplay();
    });
    document.addEventListener('change', function(e) {
        if (e.target && (e.target.name === 'partido' || e.target.name === 'partido_eliminatoria')) updateGoalDisplay();
    });

    // Inicializar display
    updateGoalDisplay();
});

// Filtrar partidos según el equipo del jugador seleccionado
document.addEventListener('DOMContentLoaded', function() {
    const jugadorSelect = document.querySelector('select[name="jugador"]');
    // Mapa jugador->equipo inyectado desde la plantilla (ver form.html)
    const jugadorEquipoMap = (window && window.jugadorEquipoMap) ? window.jugadorEquipoMap : {};

    function filterPartidosByJugador(equipoId) {
        const selects = document.querySelectorAll('select[name="partido"]');
        selects.forEach(sel => {
            const options = Array.from(sel.options);
            options.forEach(opt => {
                const local = opt.getAttribute('data-local');
                const visita = opt.getAttribute('data-visitante');
                if (!local && !visita) return; // keep non-data options
                if (equipoId && (local === equipoId || visita === equipoId)) {
                    opt.hidden = false;
                    opt.disabled = false;
                } else {
                    // if it's currently selected, keep it visible so value isn't lost
                    if (opt.selected) {
                        opt.hidden = false;
                        opt.disabled = false;
                    } else {
                        opt.hidden = true;
                        opt.disabled = true;
                    }
                }
            });
        });

        // igual para partidos de eliminatoria
        const selectsElim = document.querySelectorAll('select[name="partido_eliminatoria"]');
        selectsElim.forEach(sel => {
            const options = Array.from(sel.options);
            options.forEach(opt => {
                const local = opt.getAttribute('data-local');
                const visita = opt.getAttribute('data-visitante');
                if (!local && !visita) return;
                if (equipoId && (local === equipoId || visita === equipoId)) {
                    opt.hidden = false;
                    opt.disabled = false;
                } else {
                    if (opt.selected) {
                        opt.hidden = false;
                        opt.disabled = false;
                    } else {
                        opt.hidden = true;
                        opt.disabled = true;
                    }
                }
            });
        });
    }

    if (jugadorSelect) {
        jugadorSelect.addEventListener('change', function() {
            const jId = this.value;
            const equipoId = jugadorEquipoMap[jId] || '';
            filterPartidosByJugador(equipoId);
        });

        // trigger initial filter if a jugador is preselected
        const initial = jugadorSelect.value;
        if (initial) {
            filterPartidosByJugador(jugadorEquipoMap[initial] || '');
        }
    }

    // Cuando clonamos una jornada, aplicar el filtro al nuevo bloque
    const addBtn = document.getElementById('addJornadaBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            setTimeout(function() {
                const currentJugador = document.querySelector('select[name="jugador"]').value;
                filterPartidosByJugador(jugadorEquipoMap[currentJugador] || '');
            }, 50);
        });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('jornadasContainer');
    const addBtn = document.getElementById('addJornadaBtn');
    const removeBtn = document.getElementById('removeJornadaBtn');

    function cloneJornadaBlock() {
        const blocks = container.querySelectorAll('.jornada-block');
        const last = blocks[blocks.length - 1];
        const clone = last.cloneNode(true);
        // Limpiar valores y quitar ids duplicados
        const selects = clone.querySelectorAll('select');
        selects.forEach(sel => {
            sel.selectedIndex = 0;
            sel.removeAttribute('id');
        });
        const inputGoles = clone.querySelector('input[name="goles"]');
        if (inputGoles) {
            inputGoles.value = 1;
            inputGoles.removeAttribute('id');
        }
        container.appendChild(clone);
    }

    addBtn.addEventListener('click', function() {
        cloneJornadaBlock();
    });

    removeBtn.addEventListener('click', function() {
        const blocks = container.querySelectorAll('.jornada-block');
        if (blocks.length > 1) {
            blocks[blocks.length - 1].remove();
        }
    });
});
