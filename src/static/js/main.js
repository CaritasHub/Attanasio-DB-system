$(function() {
    var csrfToken = $("meta[name='csrf-token']").attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
        }
    });

    var endpoints = {
        specialists: '/specialists/',
        users: '/users/',
        afferenze: '/afferenze/',
        sedi: '/sedi/',
        provvedimenti: '/provvedimenti/',
        loginusers: '/loginusers/'
    };

    function loadTable(name) {
        $.getJSON(endpoints[name], function(data) {
            var thead = '';
            var tbody = '';
            if (data.length > 0) {
                var keys = Object.keys(data[0]);
                thead = '<tr>' + keys.map(function(k){ return '<th>' + k + '</th>'; }).join('') + '</tr>';
                tbody = data.map(function(row){
                    var tds = keys.map(function(k){
                        var val = row[k];
                        return '<td>' + (val === null ? '' : val) + '</td>';
                    }).join('');
                    return '<tr>' + tds + '</tr>';
                }).join('');
            }
            $('#data-table thead').html(thead);
            $('#data-table tbody').html(tbody);
            $('#search-bar').trigger('keyup');
        });
    }

    $('.table-link').on('click', function(e){
        e.preventDefault();
        var name = $(this).data('table');
        $('.table-link').removeClass('active');
        $(this).addClass('active');
        $('#search-bar').val('');
        loadTable(name);
    });

    $('#search-bar').on('keyup', function(){
        var value = $(this).val().toLowerCase();
        $('#data-table tbody tr').filter(function(){
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    loadTable('specialists');
});
