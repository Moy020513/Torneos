document.addEventListener('DOMContentLoaded', function() {
  const tabLocal = document.getElementById('tab-local');
  const tabVisitante = document.getElementById('tab-visitante');
  const containerLocal = document.getElementById('container-local');
  const containerVisitante = document.getElementById('container-visitante');

  // Mostrar local por defecto en móvil
  if (window.innerWidth < 768) {
    containerLocal.classList.add('active');
  }

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
});