import {CodeJar} from '{{ request.app.url_path_for("static", path="/js/codejar.min.js") }}'
import hljs from '{{ request.app.url_path_for("static", path="/js/highlight/core.min.js") }}'
import sql from '{{ request.app.url_path_for("static", path="/js/highlight/sql.min.js") }}'
hljs.configure({ignoreUnescapedHTML: true});
hljs.registerLanguage('sql', sql);
var queryEditorEl = document.getElementById("query-editor");
window.queryJar = CodeJar(queryEditorEl, hljs.highlightElement);
function queryFormat() {
    var query_lang = document.getElementById("query-lang").value;
    var format = document.getElementById("result-format").value.trim();
    var viz = JSON.stringify(window.getChartOptions());
    var data = {query: queryJar.toString(), viz: viz, query_lang: query_lang, format: format, echart_id: '{{ echart_id }}'};
    return JSON.stringify(data)
}
window.queryFormat = queryFormat;
function generateLink() {
    var data = JSON.parse(queryFormat());
    delete data.echart_id;
    var path = window.location.pathname.split("/").slice(0, 3).join("/");
    var query = "?";
    for (let [key, value] of Object.entries(data)) {
        query += `${encodeURIComponent(key)}=${encodeURIComponent(value)}&`;
    }
    var url = `${window.location.origin}${path}${query}`;
    alert(url);
}
window.generateLink = generateLink;