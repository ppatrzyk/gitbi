var vega_spec = JSON.parse('{{ vega }}');
if (! vega_spec.hasOwnProperty("width")) {
    var result_el = document.getElementById("query-result")
    var width = Math.floor(result_el.offsetWidth-100)
    vega_spec["width"] = width
    vega_spec["height"] = Math.floor(0.5*width)   
}
vegaEmbed('#vega-viz', vega_spec, {
    mode: "vega-lite",
    renderer: "canvas",
});