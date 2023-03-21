var current_data = null;
var initial_viz = true;
var saved_viz;
try {
    saved_viz = JSON.parse(`{{ viz }}`);
} catch (_e) {
    saved_viz = null;
}
const axis_opts = {
    nameLocation: 'middle',
    min: function (value) {return value.min - ((value.max-value.min)*0.1);},
    max: function (value) {return value.max + ((value.max-value.min)*0.1);},
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
        group: document.getElementById('echart-options-group').value,
    }
    return chart_options
}
window.get_chart_options = get_chart_options;
function update_chart_options() {
    var select_ids = ['echart-options-xaxis', 'echart-options-yaxis', 'echart-options-group', ];
    var headings = Array.from(document.getElementById(select_ids[0]).getElementsByTagName('option')).map((node) => node.value)
    var new_headings = ['_NONE', ].concat(current_data.headings);
    if (!array_ident(headings, new_headings)) {
        select_ids.forEach(id => {
            var columns = new_headings.map((name) => {
                var entry = document.createElement("option");
                entry.setAttribute('value', name);
                entry.innerText = name;
                return entry
            })
            document.getElementById(id).replaceChildren(...columns);
        });
        if (initial_viz) {
            initial_viz = false;
            if (saved_viz !== null) {
                document.getElementById('echart-options-type').value = saved_viz.type;
                document.getElementById('echart-options-xaxis').value = saved_viz.xaxis;
                document.getElementById('echart-options-yaxis').value = saved_viz.yaxis;
                document.getElementById('echart-options-group').value = saved_viz.group;
            }
        } else {
            select_ids.forEach(id => {
                document.getElementById(id).value = "_NONE";
            })
            document.getElementById('echart-options-type').value = "scatter"
        }
    }
}
function make_viz() {
    try {
        if (current_data === null || current_data.data.length === 0) {
            document.getElementById('echart-note').classList.remove("hidden");
            document.getElementById('echart-chart').classList.add("hidden");
            throw new Error('no data available');
        } else {
            document.getElementById('echart-note').classList.add("hidden");
            document.getElementById('echart-chart').classList.remove("hidden");
        }
        var chart_el = document.getElementById('echart');
        chart_el.replaceChildren();
        chart_el.removeAttribute('_echarts_instance_')
        chart_el.style.width = `${chart_el.offsetWidth}px`;
        chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
        var chart_options = get_chart_options();
        var x_index = current_data.headings.indexOf(chart_options.xaxis);
        var y_index = current_data.headings.indexOf(chart_options.yaxis);
        var title = `${chart_options.xaxis} x ${chart_options.yaxis}`;
        if (chart_options.group === '_NONE') {
            var data = current_data.data.map(r => [r[x_index], r[y_index]]);
            var series = [{data: data, type: chart_options.type, name: title}];
        } else {
            var group_index = current_data.headings.indexOf(chart_options.group);
            var series = {};
            current_data.data.forEach(r => {
                if (series[r[group_index]] === undefined) {
                    series[r[group_index]] = {data: [[r[x_index], r[y_index]], ], type: chart_options.type, name: chart_options.group};
                } else {
                    series[r[group_index]].data.push([r[x_index], r[y_index]]);
                }
            });
            series = Object.keys(series).map(k => {return Object.assign({}, series[k], {name: k})})
        }
        var x_type = (typeof(series[0].data[0][0]) === 'string' ? "category" : "value");
        var y_type = (typeof(series[0].data[0][1]) === 'string' ? "category" : "value");
        var echarts_conf = {
            legend: {show: true, },
            toolbox: {show: true, feature: {saveAsImage: {show: true}}},
            tooltip: {show: true, triggerOn: "mousemove", },
            title: {show: true, text: title},
            textStyle: {fontFamily: 'Ubuntu'},
            xAxis: Object.assign({}, {type: x_type, name: chart_options.xaxis}, axis_opts),
            yAxis: Object.assign({}, {type: y_type, name: chart_options.yaxis}, axis_opts),
            series: series,
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