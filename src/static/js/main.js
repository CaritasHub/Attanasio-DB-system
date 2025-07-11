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

    // Map visible table names to backend endpoints
    var endpoints = {
        specialists: '/specialists/',
        users: '/users/',
        sedi: '/sedi/'
    };

    var defaultTable = new URLSearchParams(window.location.search).get('table') || 'users';
    var currentTable = defaultTable;
    var currentPage = 1;
    var totalPages = 1;
    var perPage = parseInt($('#per-page-select').val(), 10) || 50;
    var sortBy = null;
    var sortOrder = 'asc';
    var allColumns = [];
    var currentColumns = [];
    var columnConfig = {};
    var hiddenColumns = ['id', 'created_at', 'updated_at'];

    function updatePageInfo(){
        $('#page-info').text(currentPage + ' / ' + totalPages);
        $('#prev-page').prop('disabled', currentPage <= 1);
        $('#next-page').prop('disabled', currentPage >= totalPages);
    }

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
        sortBy = null;
        sortOrder = 'asc';
        currentPage = 1;
        $.getJSON('/extras/column-config/' + name, function(cfg){
            columnConfig = {};
            if(cfg.columns){
                cfg.columns.forEach(function(c){ columnConfig[c.column_name] = {visible: c.visible, order: c.display_order, highlight: c.highlight}; });
            }
            fetchData();
        });

        function fetchData(){
        var params = {page: currentPage, per_page: perPage, query: $('#search-bar').val()};
        if(sortBy){ params.sort_by = sortBy; params.order = sortOrder; }
        $.getJSON(endpoints[name], params, function(res) {
            var data = res.rows || res;
            totalPages = Math.max(1, Math.ceil((res.total || data.length) / perPage));
            var thead = '';
            var tbody = '';
            if (data.length > 0) {
                allColumns = Object.keys(data[0]);
                currentColumns = orderColumns(allColumns);
                if (userRole === 'viewer') {
                    thead = '<tr>' + currentColumns.map(function(k){
                        var arrow = '';
                        if (sortBy === k) arrow = sortOrder === 'asc' ? ' \u25B2' : ' \u25BC';
                        return '<th class="sortable" data-col="' + k + '">' + normalize(k) + arrow + '</th>';
                    }).join('') + '</tr>';
                    tbody = data.map(function(row){
                        var tds = currentColumns.map(function(k){
                            var val = row[k];
                            return '<td>' + (val === null ? '' : val) + '</td>';
                        }).join('');
                        return '<tr>' + tds + '</tr>';
                    }).join('');
                } else {
                    thead = '<tr><th><input type="checkbox" id="select-all"></th>' +
                        currentColumns.map(function(k){
                            var arrow = '';
                            if (sortBy === k) arrow = sortOrder === 'asc' ? ' \u25B2' : ' \u25BC';
                            return '<th class="sortable" data-col="' + k + '">' + normalize(k) + arrow + '</th>'; }).join('') + '</tr>';
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
                updatePageInfo();
            } else {
                $.getJSON('/extras/columns/' + name, function(cols){
                    allColumns = cols;
                    currentColumns = orderColumns(cols);
                    if (userRole === 'viewer') {
                        thead = '<tr>' + currentColumns.map(function(k){
                            return '<th class="sortable" data-col="' + k + '">' + normalize(k) + '</th>';
                        }).join('') + '</tr>';
                    } else {
                        thead = '<tr><th><input type="checkbox" id="select-all"></th>' +
                            currentColumns.map(function(k){
                                return '<th class="sortable" data-col="' + k + '">' + normalize(k) + '</th>';
                            }).join('') + '</tr>';
                    }
                    $('#data-table thead').html(thead);
                    $('#data-table tbody').empty();
                    $('#delete-selected').prop('disabled', true);
                    updatePageInfo();
                });
            }
        });
        }
        window.fetchData = fetchData;
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
            function deleteRow(row, force){
                var data = row.data();
                var url = endpoints[currentTable] + data.id + (force ? '?force=1' : '');
                return $.ajax({url:url, method:'DELETE'}).then(null, function(xhr){
                    if(!force && xhr.status === 409){
                        if(confirm('Record collegato ad altre tabelle. Eliminare comunque?')){
                            return deleteRow(row, true);
                        }
                    }
                });
            }
            var chain = $.Deferred().resolve();
            checks.each(function(){
                var row = $(this).closest('tr');
                chain = chain.then(function(){ return deleteRow(row, false); });
            });
            chain.then(function(){ loadTable(currentTable); });
        });

    }

    // Open detail page for all roles
    $('#data-table').on('click', 'tbody tr', function(e){
        if ($(e.target).is('input')) return;
        var id = $(this).data('id');
        if (id) window.location = '/record/' + currentTable + '/' + id;
    });

    $('#data-table').on('click', 'th.sortable', function(){
        var col = $(this).data('col');
        if (sortBy === col) {
            sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            sortBy = col;
            sortOrder = 'asc';
        }
        fetchData();
    });

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
            var cfg = columnConfig[c] || {visible:true, order:0, highlight:false};
            var item = $('<li class="list-group-item d-flex align-items-center" data-col="'+c+'"></li>');
            item.append('<input type="checkbox" class="form-check-input me-2 column-visible" '+(cfg.visible?'checked':'')+'>');
            item.append('<span class="flex-grow-1">'+normalize(c)+'</span>');
            item.append('<input type="checkbox" class="form-check-input highlight-check ms-2" '+(cfg.highlight?'checked':'')+' title="In rilievo">');
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
                visible: $(this).find('.column-visible').is(':checked'),
                highlight: $(this).find('.highlight-check').is(':checked'),
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
        currentPage = 1;
        loadTable(name);
    });

    $('#search-bar').on('input', function(){
        currentPage = 1;
        fetchData();
    });

    $('#prev-page').on('click', function(){
        if(currentPage > 1){
            currentPage--;
            fetchData();
        }
    });

    $('#next-page').on('click', function(){
        if(currentPage < totalPages){
            currentPage++;
            fetchData();
        }
    });

    $('#per-page-select').on('change', function(){
        perPage = parseInt($(this).val(), 10) || 50;
        currentPage = 1;
        fetchData();
    });

    $('.table-link').removeClass('active');
    $(".table-link[data-table='" + defaultTable + "']").addClass('active');
    loadTable(defaultTable);
});
