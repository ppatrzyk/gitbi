function create_error(parent_id, message) {
    var template = document.createElement('template');
    template.innerHTML = `<article class="error"><h2>JS Error</h2><p>${String(message).trim()}</p></article>`;
    document.getElementById(parent_id).replaceChildren(template.content.firstChild);
}
function html_escape(str) {
    return new Option(str).innerHTML;
}