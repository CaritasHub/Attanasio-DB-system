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

    var currentTable = 'specialists';
    var currentColumns = [];

    function loadTable(name) {
        currentTable = name;
        $.getJSON(endpoints[name], function(data) {
            var thead = '';
            var tbody = '';
            if (data.length > 0) {
                currentColumns = Object.keys(data[0]);
                thead = '<tr><th><input type="checkbox" id="select-all"></th>' +
                    currentColumns.map(function(k){ return '<th>' + k + '</th>'; }).join('') + '</tr>';
                tbody = data.map(function(row){
                    var tds = currentColumns.map(function(k){
                        var val = row[k];
                        return '<td>' + (val === null ? '' : val) + '</td>';
                    }).join('');
                    var dataAttrs = currentColumns.map(function(k){ return 'data-' + k + '="' + row[k] + '"'; }).join(' ');
                    return '<tr ' + dataAttrs + '><td><input type="checkbox" class="row-check"></td>' + tds + '</tr>';
                }).join('');
            }
            $('#data-table thead').html(thead);
            $('#data-table tbody').html(tbody);
            $('#delete-selected').prop('disabled', true);
            $('#search-bar').trigger('keyup');
        });
    }

    $('#data-table').on('change', '.row-check, #select-all', function(){
        if (this.id === 'select-all') {
            $('.row-check').prop('checked', this.checked);
        }
        $('#delete-selected').prop('disabled', $('#data-table .row-check:checked').length === 0);
    });

    $('#delete-selected').on('click', function(){
        var checks = $('#data-table .row-check:checked');
        if (checks.length === 0) return;
        checks.each(function(){
            var row = $(this).closest('tr');
            var data = row.data();
            var url = endpoints[currentTable];
            if (currentTable === 'afferenze') {
                url += data.utente_id + '/' + data.specialista_id + '/' + data.data_inizio;
            } else {
                url += data.id;
            }
            $.ajax({url: url, method: 'DELETE'});
        });
        loadTable(currentTable);
    });

    $('#add-row').on('click', function(){
        var form = $('#add-form');
        form.empty();
        currentColumns.forEach(function(c){
            if (c === 'id') return;
            form.append('<div class="mb-3"><label class="form-label">'+c+'</label><input class="form-control" name="'+c+'"></div>');
        });
        new bootstrap.Modal(document.getElementById('addModal')).show();
    });

    $('#add-form').on('submit', function(e){
        e.preventDefault();
        var data = {};
        $(this).serializeArray().forEach(function(i){ data[i.name] = i.value; });
        $.ajax({
            url: endpoints[currentTable],
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function(){
            bootstrap.Modal.getInstance(document.getElementById('addModal')).hide();
            loadTable(currentTable);
        });
    });

    $('#import-csv-btn').on('click', function(){
        $('#csv-input').val('');
        new bootstrap.Modal(document.getElementById('importModal')).show();
    });

    $('#import-form').on('submit', function(e){
        e.preventDefault();
        var file = $('#csv-input')[0].files[0];
        if (!file) return;
        var formData = new FormData();
        formData.append('file', file);
        $.ajax({
            url: '/extras/import/' + currentTable,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false
        }).done(function(){
            bootstrap.Modal.getInstance(document.getElementById('importModal')).hide();
            loadTable(currentTable);
        });
    });

    $('#export-excel').on('click', function(){
        window.location = '/extras/export/' + currentTable;
    });

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
