function dashboard_format() {
    var file_name = document.getElementById("dashboard-file-name").value.trim();
    var fieldset = document.getElementById('dashboard-choices');
    var queries = Array.from(fieldset.getElementsByTagName('input')).filter(e => e.checked).map(e => e.id);
    var data = {queries: queries, file: file_name};
    return JSON.stringify(data)
}