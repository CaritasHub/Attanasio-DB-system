$(function() {
    var csrfToken = $("meta[name='csrf-token']").attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
        }
    });

    function loadSpecialists() {
        $.getJSON('/specialists/', function(data) {
            var rows = data.map(function(item) {
                return '<tr><td>' + item.id + '</td><td>' + item.nome + '</td><td>' + item.cognome +
                       '</td><td>' + item.ruolo +
                       '</td><td class="table-actions"><button class="btn btn-sm btn-danger delete-specialist" data-id="' + item.id + '">Delete</button></td></tr>';
            }).join('');
            $('#specialists-table tbody').html(rows);
        });
    }

    $('#add-specialist-form').submit(function(e) {
        e.preventDefault();
        var data = {
            nome: $('#specialist-nome').val(),
            cognome: $('#specialist-cognome').val(),
            ruolo: $('#specialist-ruolo').val()
        };
        $.ajax({
            url: '/specialists/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function() {
                $('#addSpecialistModal').modal('hide');
                loadSpecialists();
                $('#add-specialist-form')[0].reset();
            }
        });
    });

    $('#specialists-table').on('click', '.delete-specialist', function() {
        var id = $(this).data('id');
        $.ajax({
            url: '/specialists/' + id,
            method: 'DELETE',
            success: loadSpecialists
        });
    });

    loadSpecialists();
});
