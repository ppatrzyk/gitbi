var table = document.querySelector("#commits-table tbody");
for (let row of table.getElementsByTagName("tr")) {
    try {
        var commit_cell = row.getElementsByTagName("td")[0];
        var hash = commit_cell.innerText
        commit_cell.innerHTML = `<a href="/home/${hash}">${hash}</a>`
    } catch (error) {
        console.error("Failed to make links in commits table")
        console.error(error)
    }
}