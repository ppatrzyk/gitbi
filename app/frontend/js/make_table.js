try {
    var table_id = `{{ id }}`;
    var data = JSON.parse(`{{ data_json }}`)
    // send new data to viz
    const new_data = new CustomEvent("newdata", {detail: {data: data, id: table_id}});
    var chart_el = document.getElementById('echart');
    chart_el.dispatchEvent(new_data)
    // generate table
    var table = document.getElementById(table_id);
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
    console.error(`Failed to make interactive table id=${table_id}`);
    console.error(error);
}