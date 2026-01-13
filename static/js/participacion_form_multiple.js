// Manejar cambio de equipos en móvil
document.addEventListener('DOMContentLoaded', function() {
  const tabLocal = document.getElementById('tab-local');
  const tabVisitante = document.getElementById('tab-visitante');
  const containerLocal = document.getElementById('container-local');
  const containerVisitante = document.getElementById('container-visitante');
  
  // Mostrar local por defecto en móvil
  if (window.innerWidth < 768) {
    containerLocal.classList.add('active');
  }
  
  // Cambiar equipo al hacer click en los botones
  if (tabLocal && tabVisitante) {
    tabLocal.addEventListener('change', function() {
      if (this.checked) {
        containerLocal.style.display = 'block';
        containerVisitante.style.display = 'none';
        containerLocal.classList.add('active');
        containerVisitante.classList.remove('active');
      }
    });
    
    tabVisitante.addEventListener('change', function() {
      if (this.checked) {
        containerLocal.style.display = 'none';
        containerVisitante.style.display = 'block';
        containerLocal.classList.remove('active');
        containerVisitante.classList.add('active');
      }
    });
  }
  
  // Actualizar contador de jugadores seleccionados
  function actualizarContador() {
    const checkboxes = document.querySelectorAll('.jugador-checkbox');
    const total = Array.from(checkboxes).filter(cb => cb.checked).length;
    document.getElementById('jugadores-seleccionados').textContent = total;
    
    // Actualizar contadores por equipo
    const local = Array.from(checkboxes).filter(cb => cb.checked && cb.dataset.equipo === 'local').length;
    const visitante = Array.from(checkboxes).filter(cb => cb.checked && cb.dataset.equipo === 'visitante').length;
    document.getElementById('contador-local').textContent = local;
    document.getElementById('contador-visitante').textContent = visitante;
  }
  
  // Seleccionar todos los jugadores
  window.seleccionarTodos = function() {
    // En móvil, solo seleccionar del equipo actual
    const equipo = document.querySelector('input[name="equipo-tab"]:checked')?.value || 'local';
    document.querySelectorAll('.jugador-checkbox').forEach(cb => {
      if (window.innerWidth < 768 && cb.dataset.equipo !== equipo) {
        return; // No seleccionar del otro equipo en móvil
      }
      cb.checked = true;
    });
    actualizarContador();
  }
  
  // Limpiar selección
  window.limpiarSeleccion = function() {
    document.querySelectorAll('.jugador-checkbox').forEach(cb => cb.checked = false);
    actualizarContador();
  }
  
  const checkboxes = document.querySelectorAll('.jugador-checkbox');
  checkboxes.forEach(cb => cb.addEventListener('change', actualizarContador));
  actualizarContador();
});