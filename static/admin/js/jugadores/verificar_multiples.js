/**
 * Script para manejar la verificación múltiple de jugadores
 */
(() => {
    const modalElement = document.getElementById('modalVerificarMultiples');
    const selectCategoria = document.getElementById('categoriasSeleccionar');
    const formVerificar = document.getElementById('formVerificarMultiples');
    const resumenDiv = document.getElementById('resumenVerificacion');
    const cargandoDiv = document.getElementById('cargandoVerificacion');
    const btnConfirmar = document.getElementById('btnVerificarConfirmar');
    const countEl = document.getElementById('countJugadores');
    const categoriaNombreResumen = document.getElementById('categoriaNombreResumen');
    const pluralEl = document.getElementById('pluralJugadores');

    if (!modalElement || !selectCategoria || !formVerificar) return;

    // Obtener URL desde atributo data del formulario
    const apiUrl = formVerificar.dataset.url;
    if (!apiUrl) {
        console.error('URL no disponible en el formulario');
        return;
    }

    // Cuando cambia la categoría
    selectCategoria.addEventListener('change', async (e) => {
        const categoriaId = e.target.value;
        
        if (!categoriaId) {
            resumenDiv.style.display = 'none';
            btnConfirmar.style.display = 'none';
            cargandoDiv.style.display = 'none';
            return;
        }

        // Mostrar cargando
        cargandoDiv.style.display = 'block';
        resumenDiv.style.display = 'none';
        btnConfirmar.style.display = 'none';

        try {
            const response = await fetch(
                `${apiUrl}?categoria=${encodeURIComponent(categoriaId)}`,
                {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }
            );

            const data = await response.json();

            if (data.success) {
                const count = data.count;
                const categoriaNombre = data.categoria_nombre;

                // Actualizar resumen
                countEl.textContent = count;
                categoriaNombreResumen.textContent = categoriaNombre;
                pluralEl.textContent = count !== 1 ? 'es' : '';

                // Si hay jugadores, mostrar resumen y botón, si no avisar
                cargandoDiv.style.display = 'none';
                
                if (count === 0) {
                    // Mostrar advertencia de que no hay jugadores
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-warning';
                    alertDiv.innerHTML = `
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No hay jugadores sin verificar en esta categoría que tengan al menos un partido jugado.
                    `;
                    cargandoDiv.parentNode.replaceChild(alertDiv, cargandoDiv);
                    btnConfirmar.style.display = 'none';
                } else {
                    resumenDiv.style.display = 'block';
                    btnConfirmar.style.display = 'inline-block';
                }

                // Guardar IDs para verificación posterior
                formVerificar.dataset.jugadorIds = JSON.stringify(data.jugador_ids);
            } else {
                alert('Error: ' + (data.error || 'Ocurrió un error'));
                cargandoDiv.style.display = 'none';
            }
        } catch (err) {
            console.error('Error:', err);
            alert('Error al cargar los jugadores');
            cargandoDiv.style.display = 'none';
        }
    });

    // Al enviar el formulario (confirmar verificación)
    formVerificar.addEventListener('submit', async (e) => {
        e.preventDefault();

        const categoriaId = selectCategoria.value;
        if (!categoriaId) {
            alert('Por favor selecciona una categoría');
            return;
        }

        const jugadorIds = JSON.parse(formVerificar.dataset.jugadorIds || '[]');
        if (jugadorIds.length === 0) {
            alert('No hay jugadores para verificar');
            return;
        }

        // Confirmar con el usuario antes de verificar
        const categoriaNombre = selectCategoria.options[selectCategoria.selectedIndex].text;
        if (!confirm(`¿Deseas verificar ${jugadorIds.length} jugador${jugadorIds.length !== 1 ? 'es' : ''} de ${categoriaNombre}?`)) {
            return;
        }

        // Cambiar botón a estado cargando
        const btnOriginalHTML = btnConfirmar.innerHTML;
        btnConfirmar.disabled = true;
        btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"><span class="visually-hidden">Cargando...</span></span>Verificando...';

        try {
            // Construir FormData con la categoría
            const formData = new FormData();
            formData.append('categoria', categoriaId);
            
            // Agregar token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Éxito - mostrar mensaje y cerrar modal
                alert(`✓ Se verificaron ${data.count} jugador${data.count !== 1 ? 'es' : ''} de la categoría ${categoriaNombre}`);
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();

                // Recargar lista de jugadores
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Ocurrió un error durante la verificación'));
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = btnOriginalHTML;
            }
        } catch (err) {
            console.error('Error:', err);
            alert('Error al verificar jugadores');
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = btnOriginalHTML;
        }
    });
})();
