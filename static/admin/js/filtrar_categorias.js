

console.log('filtrar_categorias.js cargado');
(function($) {
    $(document).ready(function() {
        var torneoField = $('#id_torneo');
        var categoriaField = $('#id_categoria');

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        var csrftoken = getCookie('csrftoken');

        torneoField.change(function() {
            var torneoId = $(this).val();
            categoriaField.html('<option value="">---------</option>');
            if (torneoId) {
                $.ajax({
                    url: '/get_categorias/',
                    type: 'GET',
                    data: {
                        'torneo_id': torneoId
                    },
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    },
                    success: function(data) {
                        $.each(data.categorias, function(index, categoria) {
                            categoriaField.append('<option value="' + categoria.id + '">' + categoria.nombre + '</option>');
                        });
                    }
                });
            }
        });
    });
})(window.django && window.django.jQuery ? window.django.jQuery : window.jQuery);