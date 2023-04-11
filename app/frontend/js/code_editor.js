import {CodeJar} from '{{ request.app.url_path_for("static", path="/js/codejar.min.js") }}'
import hljs from '{{ request.app.url_path_for("static", path="/js/highlight/core.min.js") }}'
import sql from '{{ request.app.url_path_for("static", path="/js/highlight/sql.min.js") }}'
hljs.configure({ignoreUnescapedHTML: true});
hljs.registerLanguage('sql', sql);
var query_editor = document.getElementById("query-editor");
window.query_jar = CodeJar(query_editor, hljs.highlightElement);
function query_format() {
    var file_name = document.getElementById("file-name").value.trim();
    var data = {query: query_jar.toString(), viz: JSON.stringify(window.get_chart_options()), file: file_name, echart_id: '{{ echart_id }}'};
    return JSON.stringify(data)
}
window.query_format = query_format;
function generate_link() {
    var data = JSON.parse(query_format());
    var path = window.location.pathname.split("/").slice(0, 3).join("/");
    var query = "?";
    for (let [key, value] of Object.entries(data)) {
        query += `${encodeURIComponent(key)}=${encodeURIComponent(value)}&`;
    }
    var url = `${window.location.origin}${path}${query}`;
    alert(url);
}
window.generate_link = generate_link;