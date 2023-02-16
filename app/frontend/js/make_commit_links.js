var table = document.getElementById("commits-table");
for (let row of table.getElementsByTagName("tr")) {
    try {
        var commit_cell = row.getElementsByTagName("td")[0];
        var hash = commit_cell.innerText
        commit_cell.innerHTML = `<a href="/home/${hash}">${hash}</a>`
        // TODO: link to current page instead of home?
    } catch (error) {
        // pass
    }
}