function format_row(row, x_index, y_index, dtypes) {
    var x = (dtypes[x_index] === 'time') ? new Date(row[x_index]) : row[x_index];
    var y = (dtypes[y_index] === 'time') ? new Date(row[y_index]) : row[y_index];
    return [x, y]
}
function create_viz(current_data, chart_options, chart_el) {
    var axis_opts = {
        nameLocation: 'middle',
        min: function (value) {return value.min - ((value.max-value.min)*0.1);},
        max: function (value) {return value.max + ((value.max-value.min)*0.1);},
    }
    chart_el.replaceChildren();
    chart_el.removeAttribute('_echarts_instance_')
    chart_el.style.width = `${chart_el.offsetWidth}px`;
    chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
    var x_index = current_data.headings.indexOf(chart_options.xaxis);
    var y_index = current_data.headings.indexOf(chart_options.yaxis);
    var title = `${chart_options.xaxis} x ${chart_options.yaxis}`;
    if (chart_options.group === '_NONE') {
        var data = current_data.data.map(r => format_row(r, x_index, y_index, current_data.dtypes));
        var series = [{data: data, type: chart_options.type, name: title}];
    } else {
        var group_index = current_data.headings.indexOf(chart_options.group);
        var series = {};
        current_data.data.forEach(r => {
            if (series[r[group_index]] === undefined) {
                series[r[group_index]] = {data: [format_row(r, x_index, y_index, current_data.dtypes), ], type: chart_options.type, name: chart_options.group};
            } else {
                series[r[group_index]].data.push(format_row(r, x_index, y_index, current_data.dtypes));
            }
        });
        series = Object.keys(series).map(k => {return Object.assign({}, series[k], {name: k})})
    }
    var echarts_conf = {
        legend: {show: true, },
        toolbox: {show: true, feature: {saveAsImage: {show: true}}},
        tooltip: {show: true, triggerOn: "mousemove", },
        title: {show: true, text: title},
        textStyle: {fontFamily: 'Ubuntu'},
        xAxis: Object.assign({}, {type: current_data.dtypes[x_index], name: chart_options.xaxis}, axis_opts),
        yAxis: Object.assign({}, {type: current_data.dtypes[y_index], name: chart_options.yaxis}, axis_opts),
        series: series,
    };
    var chart = echarts.init(chart_el);
    chart.setOption(echarts_conf);
}