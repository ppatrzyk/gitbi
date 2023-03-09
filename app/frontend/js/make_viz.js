function get_chart_options() {
    var chart_options = {
        type: document.getElementById('echart-options-type').value,
        xaxis: document.getElementById('echart-options-xaxis').value,
        yaxis: document.getElementById('echart-options-yaxis').value,
    }
    return chart_options
}
function update_chart_options(data) {
    console.log('update_chart_options called');
    // TODO don't update if headings indentical
    var select_ids = ['echart-options-xaxis', 'echart-options-yaxis'];
    select_ids.forEach(id => {
        var columns = data.headings.map((name) => {
            var entry = document.createElement("option");
            entry.setAttribute('value', name);
            entry.innerText = name;
            return entry
        })
        document.getElementById(id).replaceChildren(...columns);
    });
}
function make_viz(data) {
    try {
        var chart_el = document.getElementById('echart');
        chart_el.style.width = `${chart_el.offsetWidth}px`;
        chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
        console.log('make_viz called');
        console.log(data);
        var chart_options = get_chart_options();
        console.log('chart_options')
        console.log(chart_options)
        // TODO read form on viz type, create chart options from it
        var chart_options = {
            xAxis: {
                type: 'category',
                data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                data: [150, 230, 224, 218, 135, 147, 260],
                type: 'line'
                }
            ]
        };
        var chart = echarts.init(chart_el);
        chart.setOption(chart_options);
    } catch (error) {
        console.error(`Failed to draw chart`);
        console.error(error);
    }
}
document.getElementById('echart').addEventListener("newdata", (e) => make_viz(e.detail.data));
document.getElementById('echart-options').addEventListener("newdata", (e) => update_chart_options(e.detail.data));
// TODO onlick for this button does not work document.data undefined? other approach?
// document.getElementById('echart-render').addEventListener('onclick', make_viz(document.data));