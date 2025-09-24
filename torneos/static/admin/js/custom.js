// Ajustes de UI para compactar el admin (sin alto contraste/seguir sistema)
(function(){
  const ready = (fn)=> document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);
  ready(()=>{
    // Compactar cabeceras y paddings
    document.querySelectorAll('.module, .grp-module, .inline-group').forEach(el => {
      el.style.padding = '12px 14px';
    });

    // Resaltar foco en inputs
    document.querySelectorAll('input, select, textarea').forEach(el => {
      el.addEventListener('focus', () => {
        el.style.boxShadow = '0 0 0 2px rgba(8,247,254,.15)';
      });
      el.addEventListener('blur', () => {
        el.style.boxShadow = 'none';
      });
    });

  });
})();
