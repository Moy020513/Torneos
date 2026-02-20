// Límite de jugadores: 16
document.addEventListener('DOMContentLoaded', function() {
  var addBtn = document.getElementById('addPlayerBtn');
  if (addBtn) {
    addBtn.addEventListener('click', function(e) {
      var jugadoresCount = parseInt(addBtn.dataset.jugadoresCount, 10);
      var limite = parseInt(addBtn.dataset.limite, 10);
      var createUrl = addBtn.dataset.createUrl;
      if (jugadoresCount >= limite) {
        e.preventDefault();
        window.location.href = window.location.pathname + '?limite_jugadores=1';
      } else {
        window.location.href = createUrl;
      }
    });
  }
});
// Search functionality
document.getElementById('playerSearch').addEventListener('keyup', function(e) {
  const searchTerm = e.target.value.toLowerCase();
  const rows = document.querySelectorAll('.player-row');
  
  rows.forEach(row => {
    const playerName = row.dataset.playerName;
    row.style.display = playerName.includes(searchTerm) ? '' : 'none';
  });
});

// Delete modal functionality
let deletePlayerId = null;
let deletePlayerUrl = null;

function confirmDelete(btn) {
  deletePlayerId = btn.dataset.playerId;
  deletePlayerUrl = btn.dataset.deleteUrlBase.replace('0', deletePlayerId);
  document.getElementById('playerNameConfirm').textContent = btn.dataset.playerName;
  document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
  document.getElementById('deleteModal').classList.remove('active');
  deletePlayerId = null;
  deletePlayerUrl = null;
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
  if (deletePlayerUrl) {
    window.location.href = deletePlayerUrl;
  }
});

document.getElementById('deleteModal').addEventListener('click', function(e) {
  if (e.target === this) {
    closeDeleteModal();
  }
});

// Add player action
document.querySelector('[data-action="add-player"]').addEventListener('click', function() {
  window.location.href = "{% url 'representante_jugador_create' %}";
});

// Toast notification
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  const toastMessage = toast.querySelector('.toast-message');
  
  let icon = '';
  if (type === 'success') {
    icon = '<i class="fas fa-check-circle"></i>';
    toast.style.background = 'var(--success-color)';
  } else if (type === 'error') {
    icon = '<i class="fas fa-exclamation-circle"></i>';
    toast.style.background = 'var(--danger-color)';
  } else {
    icon = '<i class="fas fa-info-circle"></i>';
    toast.style.background = 'var(--primary-color)';
  }
  
  toastMessage.innerHTML = `${icon} ${message}`;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Esc para cerrar modal
  if (e.key === 'Escape') {
    closeDeleteModal();
  }
  // Ctrl/Cmd + K para buscar
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    document.getElementById('playerSearch').focus();
  }
});

// Función para expandir foto (reutiliza modal similar al listado público)
function expandirFoto(urlFoto, nombreJugador) {
  var img = document.getElementById('fotoExpandidaRepresentante');
  if (!img) return;
  img.src = urlFoto;
  img.alt = nombreJugador;
  var label = document.getElementById('fotoModalRepresentanteLabel');
  if (label) label.textContent = nombreJugador;
  var modalEl = document.getElementById('fotoModalRepresentante');
  if (modalEl) {
    var modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}