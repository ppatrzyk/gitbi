try {
    var data = JSON.parse(`{{ data_json }}`)
    // TODO pass data for document to make it accessible by viz
    var table = document.getElementById("{{ id }}");
    var perPageSelect = (data.data.length <= 25) ? false :[10, 25, 50, 100];
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
} catch (error) {
    console.error(`Failed to make interactive table id={{ id }}`);
    console.error(error);
}