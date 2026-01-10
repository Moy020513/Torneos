(() => {
    const form = document.getElementById('partidos-filter-form');
    const results = document.getElementById('partidos-results');
    if (!form || !results) return;

    const loadingClass = 'is-loading';
    const debounce = (fn, delay = 200) => {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn(...args), delay);
        };
    };

    const buildUrl = (href, includePartial = true) => {
        if (href) {
            // Si href es relativo o contiene query string, completar la URL
            let url;
            if (href.startsWith('http')) {
                url = href;
            } else if (href.startsWith('?')) {
                url = window.location.pathname + href;
            } else {
                url = window.location.pathname + (href.startsWith('/') ? '' : '?') + href;
            }
            const urlObj = new URL(url, window.location.origin);
            if (includePartial) {
                urlObj.searchParams.set('_partial', '1');
            }
            return urlObj.toString();
        }
        const params = new URLSearchParams(new FormData(form));
        params.delete('page');
        if (includePartial) {
            params.set('_partial', '1');
        }
        const qs = params.toString();
        return qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    };

    const renderResults = async (href) => {
        const fetchUrl = buildUrl(href, true);
        const historyUrl = buildUrl(href, false);
        results.classList.add(loadingClass);
        try {
            const res = await fetch(fetchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!res.ok) throw new Error('Error al cargar los partidos');
            const html = await res.text();
            
            // Limpiar contenedor
            results.innerHTML = '';
            
            // Si por algún motivo llega el HTML completo, extraer sólo el contenedor interno
            const temp = document.createElement('div');
            temp.innerHTML = html;
            const inner = temp.querySelector('#partidos-results');
            const contentToInsert = inner ? inner.innerHTML : html;
            
            // Insertar nuevo contenido
            results.innerHTML = contentToInsert;
            
            // Eliminar paginaciones duplicadas
            const navs = results.querySelectorAll('nav[aria-label="Paginación"]');
            if (navs.length > 1) {
                for (let i = 0; i < navs.length - 1; i++) {
                    navs[i].remove();
                }
            }
            
            window.history.replaceState({}, '', historyUrl);
        } catch (err) {
            console.error(err);
        } finally {
            results.classList.remove(loadingClass);
        }
    };

    const handleChange = debounce(() => renderResults());

    form.addEventListener('input', handleChange);
    form.addEventListener('change', handleChange);
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        renderResults();
    });

    results.addEventListener('click', (e) => {
        const link = e.target.closest('.pagination a');
        if (link) {
            e.preventDefault();
            renderResults(link.href);
        }
    });
})();