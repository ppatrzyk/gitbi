var current_data = null;
var initial_viz = true;
var saved_viz;
try {
    saved_viz = JSON.parse(`{{ viz }}`);
} catch (_e) {
    saved_viz = null;
}

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
window.get_chart_options = get_chart_options;
function update_chart_options() {
    console.log('update_chart_options called');
    var select_ids = ['echart-options-xaxis', 'echart-options-yaxis'];
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
    if (initial_viz) {
        initial_viz = false;
        console.log("initial render")
        console.log(saved_viz)
        if (saved_viz !== null) {
            document.getElementById('echart-options-type').value = saved_viz.type;
            document.getElementById('echart-options-xaxis').value = saved_viz.xaxis;
            document.getElementById('echart-options-yaxis').value = saved_viz.yaxis;
        }
    }
}
function make_viz() {
    try {
        console.log('make_viz called');
        console.log(current_data);
        if (current_data === null || current_data.data.length === 0) {
            document.getElementById('echart-note').classList.remove("hidden");
            document.getElementById('echart-chart').classList.add("hidden");
            throw new Error('no data available');
        } else {
            document.getElementById('echart-note').classList.add("hidden");
            document.getElementById('echart-chart').classList.remove("hidden");
        }
        var chart_el = document.getElementById('echart');
        chart_el.style.width = `${chart_el.offsetWidth}px`;
        chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
        var chart_options = get_chart_options();
        console.log('chart_options')
        console.log(chart_options)
        // TODO add groupby column
        var x_index = current_data.headings.indexOf(chart_options.xaxis);
        var y_index = current_data.headings.indexOf(chart_options.yaxis);
        var data = current_data.data.map((r) => [r[x_index], r[y_index]]);
        console.log('data fromatted')
        console.log(data)
        // TODO handle time
        var echarts_conf = {
            xAxis: {type: (typeof(data[0][0]) === 'string' ? "category" : "value")},
            yAxis: {type: (typeof(data[0][1]) === 'string' ? "category" : "value")},
            series: [
                {data: data, type: chart_options.type}
            ]
        };
        var chart = echarts.init(chart_el);
        chart.setOption(echarts_conf);
    } catch (error) {
        console.error(`Failed to draw chart`);
        console.error(error);
    }
}
window.make_viz = make_viz;
document.getElementById('echart').addEventListener("newdata", (e) => {
    current_data = e.detail.data;
    update_chart_options();
    make_viz();
});