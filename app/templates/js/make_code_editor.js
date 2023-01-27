import {CodeJar} from '{{ url_for("static", path="/js/codejar.min.js") }}'
import hljs from '{{ url_for("static", path="/js/highlight/core.min.js") }}'
import json from '{{ url_for("static", path="/js/highlight/json.min.js") }}'
import sql from '{{ url_for("static", path="/js/highlight/sql.min.js") }}'
hljs.configure({ignoreUnescapedHTML: true});
hljs.registerLanguage('json', json);
hljs.registerLanguage('sql', sql);
let query_editor = document.getElementById("query-editor");
let vega_editor = document.getElementById("vega-editor");
window.query_jar = CodeJar(query_editor, hljs.highlightElement);
window.vega_jar = CodeJar(vega_editor, hljs.highlightElement);
function query_format() {
    var include_vega = document.getElementById("include-vega").checked;
    var file_name = document.getElementById("file-name").value.trim();
    var data = {query: query_jar.toString(), file: file_name};
    if (include_vega) {
        data["vega"] = vega_jar.toString();
    }
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