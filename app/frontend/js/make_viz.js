var current_data = null;

function array_ident(arr1, arr2) {
    // https://stackoverflow.com/a/19746771
    return (arr1.length === arr2.length && arr1.every((value, index) => value === arr2[index]))
}
function get_chart_options() {
    var chart_options = {
        type: document.getElementById('echart-options-type').value,
        xaxis: document.getElementById('echart-options-xaxis').value,
        yaxis: document.getElementById('echart-options-yaxis').value,
    }
    return chart_options
}
function update_chart_options() {
    console.log('update_chart_options called');
    var select_ids = ['echart-options-xaxis', 'echart-options-yaxis'];
    document.getElementById(select_ids[0]).childNodes
    var headings = Array.from(document.getElementById(select_ids[0]).getElementsByTagName('option')).map((node) => node.value)
    if (!array_ident(headings, current_data.headings)) {
        console.log('different headers, replacing')
        select_ids.forEach(id => {
            var columns = current_data.headings.map((name) => {
                var entry = document.createElement("option");
                entry.setAttribute('value', name);
                entry.innerText = name;
                return entry
            })
            document.getElementById(id).replaceChildren(...columns);
        });
    }
}
function make_viz() {
    try {
        var chart_el = document.getElementById('echart');
        chart_el.style.width = `${chart_el.offsetWidth}px`;
        chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
        console.log('make_viz called');
        console.log(current_data);
        var chart_options = get_chart_options();
        console.log('chart_options')
        console.log(chart_options)
        // TODO read form on viz type, create chart options from it
        // TODO maybe go back to reading default (saved) viz here - will be used on empty chart options
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
document.getElementById('echart').addEventListener("newdata", (e) => {
    current_data = e.detail.data;
    update_chart_options();
    make_viz();
});