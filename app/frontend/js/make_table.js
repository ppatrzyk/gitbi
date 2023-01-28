var table = document.getElementById("results-table");
var data_table = new simpleDatatables.DataTable(table, {
    perPageSelect: [10, 25, 50, 100],
    classes: {bottom: "grid", top: "grid", selector: "no-margin",},
    layout: {
        top: "{select}{search}",
        bottom: "{pager}{info}"
    },
});
var search_button = document.getElementsByClassName("datatable-search")[0];
var csv_button = document.createElement("div"); 
csv_button.setAttribute("class", "secondary")
csv_button.setAttribute("role", "button")
csv_button.innerText = "Export CSV";
csv_button.addEventListener("click", () => {
    simpleDatatables.exportCSV(data_table, {
        download: true,
        lineDelimiter: "\n",
        columnDelimiter: ";"
    })
});
search_button.insertAdjacentElement('afterend', csv_button);