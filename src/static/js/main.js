$(function() {
    var csrfToken = $("meta[name='csrf-token']").attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
        }
    });

    var userRole = window.userRole || 'viewer';

    var endpoints = {
        specialists: '/specialists/',
        users: '/users/',
        afferenze: '/afferenze/',
        sedi: '/sedi/',
        provvedimenti: '/provvedimenti/'
    };

    var currentTable = 'specialists';
    var allColumns = [];
    var currentColumns = [];
    var columnConfig = {};
    var hiddenColumns = ['id', 'created_at', 'updated_at'];

    function normalize(name){
        return name.replace(/_/g, ' ');
    }

    if (userRole === 'viewer') {
        $('#add-row').hide();
        $('#delete-selected').hide();
        $('#import-csv-btn').hide();
    }

    function orderColumns(cols) {
        return cols.slice().sort(function(a,b){
            var oa = columnConfig[a] ? columnConfig[a].order : 0;
            var ob = columnConfig[b] ? columnConfig[b].order : 0;
            return oa - ob;
        }).filter(function(c){
            return !hiddenColumns.includes(c) && (!columnConfig[c] || columnConfig[c].visible);
        });
    }

    function loadTable(name) {
        currentTable = name;
        $.getJSON('/extras/column-config/' + name, function(cfg){
            columnConfig = {};
            if(cfg.columns){
                cfg.columns.forEach(function(c){ columnConfig[c.column_name] = {visible: c.visible, order: c.display_order}; });
            }
            fetchData();
        });

        function fetchData(){
        $.getJSON(endpoints[name], function(data) {
            var thead = '';
            var tbody = '';
            if (data.length > 0) {
                allColumns = Object.keys(data[0]);
                currentColumns = orderColumns(allColumns);
                if (userRole === 'viewer') {
                    thead = '<tr>' + currentColumns.map(function(k){ return '<th>' + normalize(k) + '</th>'; }).join('') + '</tr>';
                    tbody = data.map(function(row){
                        var tds = currentColumns.map(function(k){
                            var val = row[k];
                            return '<td>' + (val === null ? '' : val) + '</td>';
                        }).join('');
                        return '<tr>' + tds + '</tr>';
                    }).join('');
                } else {
                    thead = '<tr><th><input type="checkbox" id="select-all"></th>' +
                        currentColumns.map(function(k){ return '<th>' + normalize(k) + '</th>'; }).join('') + '</tr>';
                    tbody = data.map(function(row){
                        var tds = currentColumns.map(function(k){
                            var val = row[k];
                            return '<td>' + (val === null ? '' : val) + '</td>';
                        }).join('');
                        var dataAttrs = allColumns.map(function(k){ return 'data-' + k + '="' + row[k] + '"'; }).join(' ');
                        return '<tr ' + dataAttrs + '><td><input type="checkbox" class="row-check"></td>' + tds + '</tr>';
                    }).join('');
                }
                $('#data-table thead').html(thead);
                $('#data-table tbody').html(tbody);
                $('#delete-selected').prop('disabled', true);
                $('#search-bar').trigger('keyup');
            } else {
                $.getJSON('/extras/columns/' + name, function(cols){
                    allColumns = cols;
                    currentColumns = orderColumns(cols);
                    if (userRole === 'viewer') {
                        thead = '<tr>' + currentColumns.map(function(k){ return '<th>' + normalize(k) + '</th>'; }).join('') + '</tr>';
                    } else {
                        thead = '<tr><th><input type="checkbox" id="select-all"></th>' +
                            currentColumns.map(function(k){ return '<th>' + normalize(k) + '</th>'; }).join('') + '</tr>';
                    }
                    $('#data-table thead').html(thead);
                    $('#data-table tbody').empty();
                    $('#delete-selected').prop('disabled', true);
                    $('#search-bar').trigger('keyup');
                });
            }
        });
        }
    }

    if (userRole !== 'viewer') {
        $('#data-table').on('change', '.row-check, #select-all', function(){
            if (this.id === 'select-all') {
                $('.row-check').prop('checked', this.checked);
            }
            $('#delete-selected').prop('disabled', $('#data-table .row-check:checked').length === 0);
        });

        $('#delete-selected').on('click', function(){
            var checks = $('#data-table .row-check:checked');
            if (checks.length === 0) return;
            var calls = [];
            checks.each(function(){
                var row = $(this).closest('tr');
                var data = row.data();
                var url = endpoints[currentTable];
                if (currentTable === 'afferenze') {
                    url += data.utente_id + '/' + data.specialista_id + '/' + data.data_inizio;
                } else {
                    url += data.id;
                }
                calls.push($.ajax({url: url, method: 'DELETE'}));
            });
            $.when.apply($, calls).then(function(){
                loadTable(currentTable);
            });
        });
    }

    function showAddModal(cols){
        var form = $('#add-form .modal-body');
        form.empty();
        cols.forEach(function(c){
            if (hiddenColumns.indexOf(c) !== -1) return;
            form.append('<div class="mb-3"><label class="form-label">'+normalize(c)+'</label><input class="form-control" name="'+c+'"></div>');
        });
        new bootstrap.Modal(document.getElementById('addModal')).show();
    }

    if (userRole !== 'viewer') {
    $('#add-row').on('click', function(){
        if (currentColumns.length === 0 && allColumns.length === 0) {
            $.getJSON('/extras/columns/' + currentTable, function(cols){
                if (!cols.length) return;
                allColumns = cols;
                currentColumns = orderColumns(cols);
                showAddModal(currentColumns);
            });
            return;
        }
        var visibleCols = allColumns.length ? orderColumns(allColumns) : currentColumns;
        showAddModal(visibleCols);
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
    }

    $('#export-excel').on('click', function(){
        window.location = '/extras/export/' + currentTable;
    });

    $('#table-settings').on('click', function(){
        var list = $('#columns-list');
        list.empty();
        var cols = allColumns.length ? allColumns : [];
        var load = function(c){
            if(hiddenColumns.indexOf(c) !== -1) return;
            var cfg = columnConfig[c] || {visible:true, order:0};
            var item = $('<li class="list-group-item" data-col="'+c+'"></li>');
            item.append('<input type="checkbox" class="form-check-input me-2" '+(cfg.visible?'checked':'')+'>');
            item.append('<span>'+normalize(c)+'</span>');
            list.append(item);
        };
        if(cols.length){
            cols.forEach(load);
            list.sortable();
            new bootstrap.Modal(document.getElementById('columnsModal')).show();
        } else {
            $.getJSON('/extras/columns/' + currentTable, function(data){
                allColumns = data;
                data.forEach(load);
                list.sortable();
                new bootstrap.Modal(document.getElementById('columnsModal')).show();
            });
        }
    });

    $('#save-columns').on('click', function(){
        var cols = [];
        $('#columns-list li').each(function(i){
            cols.push({
                column_name: $(this).data('col'),
                visible: $(this).find('input').is(':checked'),
                display_order: i
            });

        });
        $.ajax({
            url: '/extras/column-config/' + currentTable,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({columns: cols})
        }).done(function(){
            bootstrap.Modal.getInstance(document.getElementById('columnsModal')).hide();
            loadTable(currentTable);

        }).fail(function(){
            alert('Impossibile salvare la configurazione');

        });
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
