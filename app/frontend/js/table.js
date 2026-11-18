function htmlEscape(str) {
    return new Option(str).innerHTML;
}
function createTable(table_id, data) {
    var table = document.getElementById(table_id);
    var perPageSelect = (data.data.length <= 25) ? false :[10, 25, 50, 100];
    data.headings = data.headings.map(e => htmlEscape(e))
    data.data = data.data.map(row => row.map(e => htmlEscape(e)))
    var dataTable = new simpleDatatables.DataTable(table, {
        data: data,
        perPage: 25,
        perPageSelect: perPageSelect,
        classes: {
            top: "pure-form",
            bottom: "datatable-container",
            table: "pure-table pure-table-striped",
            search: "datatable-search bottom-margin",
            dropdown: "datatable-dropdown bottom-margin"
        },
        type: "html",
        layout: {
            top: "{search}",
            bottom: "{select}{info}{pager}"
        },
    });
}