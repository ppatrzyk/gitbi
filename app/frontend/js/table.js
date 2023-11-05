function create_table(table_id, data) {
    var table = document.getElementById(table_id);
    var perPageSelect = (data.data.length <= 25) ? false :[10, 25, 50, 100];
    data.headings = data.headings.map(e => html_escape(e))
    data.data = data.data.map(row => row.map(e => html_escape(e)))
    var data_table = new simpleDatatables.DataTable(table, {
        data: data,
        perPage: 25,
        perPageSelect: perPageSelect,
        classes: {bottom: "grid", top: "grid", selector: "no-margin", input: "no-margin"},
        type: "html",
        layout: {
            top: "{search}",
            bottom: "{select}{info}{pager}"
        },
    });
    var search_button = table.parentNode.parentNode.getElementsByClassName("datatable-search")[0];
    var csv_button = document.createElement("div"); 
    csv_button.setAttribute("class", "secondary");
    csv_button.setAttribute("role", "button");
    csv_button.innerText = "Export CSV";
    csv_button.addEventListener("click", () => {
        simpleDatatables.exportCSV(data_table, {
            download: true,
            lineDelimiter: "\n",
            columnDelimiter: ";"
        })
    });
    search_button.insertAdjacentElement('afterend', csv_button);
}