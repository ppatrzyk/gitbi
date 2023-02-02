var vega_spec = JSON.parse('{{ vega }}');
if (! vega_spec.hasOwnProperty("width")) {
    var result_el = document.getElementById("query-result")
    var width = Math.floor(result_el.offsetWidth-100)
    vega_spec["width"] = width
    vega_spec["height"] = Math.floor(0.5*width)   
}
var script_tag = document.createElement('script');
script_tag.setAttribute("type", "text/javascript");
script_tag.setAttribute("src", "{{ vega_script }}");
script_tag.setAttribute("onload", `
vegaEmbed('#vega-viz', vega_spec, {
    mode: "vega-lite",
    renderer: "canvas",
});
`);
document.getElementsByTagName("head")[0].appendChild(script_tag);