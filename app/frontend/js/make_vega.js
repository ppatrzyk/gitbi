function make_vega(vega_element, vega_spec) {
    vegaEmbed(vega_element, vega_spec, {
        mode: "vega-lite",
        renderer: "canvas",
    }).then(
        _res => {}
    ).catch(
        err => {
            console.error(err)
            var err_node = document.createTextNode(err)
            document.querySelector(vega_element).appendChild(err_node)
        }
    )
}
var vega_element = "#vega-viz";
var vega_spec = JSON.parse('{{ vega_viz }}');
if (! vega_spec.hasOwnProperty("width")) {
    var result_el = document.getElementById("query-result")
    var width = Math.floor(result_el.offsetWidth-100)
    vega_spec["width"] = width
    vega_spec["height"] = Math.floor(0.5*width)   
}
var vega_script = document.getElementById('vega-import-script');
if (typeof(vega_script) != 'undefined' && vega_script != null) {
    make_vega(vega_element, vega_spec)
} else {
    var script_tag = document.createElement('script');
    script_tag.setAttribute("id", "vega-import-script");
    script_tag.setAttribute("type", "text/javascript");
    script_tag.setAttribute("src", "{{ request.app.url_path_for('static', path='/js/vega.all.min.js') }}");
    script_tag.setAttribute("onload", `make_vega(vega_element, vega_spec)`);
    document.getElementsByTagName("head")[0].appendChild(script_tag);
}