var table = document.getElementById("results-table");
var data_table = new simpleDatatables.DataTable(table, {
    perPageSelect: [10, 25, 50, 100],
    classes: {bottom: "grid", top: "grid"},
    layout: {
        top: "{select}{search}",
        bottom: "{pager}{info}"
    },
});
document.getElementById('csv-button').addEventListener("click", () => {
    simpleDatatables.exportCSV(data_table, {
        download: true,
        lineDelimiter: "\n",
        columnDelimiter: ";"
    })
});