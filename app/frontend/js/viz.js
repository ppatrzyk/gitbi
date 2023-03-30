function format_row(row, chart_options, current_data) {
    var x = (current_data.dtypes[chart_options.x_index] === 'time') ? new Date(row[chart_options.x_index]) : row[chart_options.x_index];
    var y = (current_data.dtypes[chart_options.y_index] === 'time') ? new Date(row[chart_options.y_index]) : row[chart_options.y_index];
    var group = (current_data.dtypes[chart_options.group_index] === 'time') ? new Date(row[chart_options.group_index]) : row[chart_options.group_index];
    return [x, y, group]
}
function series_single(current_data, chart_options) {
    var data = current_data.data.map(row => format_row(row, chart_options, current_data));
    var series = [{data: data, type: chart_options.type, name: chart_options.yaxis}];
    return series
}
function series_multi(current_data, chart_options) {
    var series = {};
    current_data.data.forEach(row => {
        if (series[row[chart_options.group_index]] === undefined) {
            series[row[chart_options.group_index]] = {data: [format_row(row, chart_options, current_data), ], type: chart_options.type, name: chart_options.group};
        } else {
            series[row[chart_options.group_index]].data.push(format_row(row, chart_options, current_data));
        }
    });
    series = Object.keys(series).map(k => {return Object.assign({}, series[k], {name: k})});
    return series
}
function create_viz(current_data, chart_options, chart_el) {
    var axis_opts = {
        nameLocation: 'middle',
        min: function (value) {return value.min - ((value.max-value.min)*0.1);},
        max: function (value) {return value.max + ((value.max-value.min)*0.1);},
        splitArea: {show: true},
    }
    chart_options.x_index = current_data.headings.indexOf(chart_options.xaxis);
    chart_options.y_index = current_data.headings.indexOf(chart_options.yaxis);
    chart_options.group_index = current_data.headings.indexOf(chart_options.group);
    chart_el.replaceChildren();
    chart_el.removeAttribute('_echarts_instance_')
    chart_el.style.width = `${chart_el.offsetWidth}px`;
    chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
    var title = `${chart_options.xaxis} x ${chart_options.yaxis}`;
    if (chart_options.group === '_NONE' | chart_options.type === 'heatmap') {
        var series = series_single(current_data, chart_options);
    } else {
        var series = series_multi(current_data, chart_options);
    }
    var echarts_conf = {
        legend: {show: true, },
        toolbox: {show: true, feature: {saveAsImage: {show: true}}},
        tooltip: {show: true, triggerOn: "mousemove", },
        title: {show: true, text: title},
        textStyle: {fontFamily: 'Ubuntu'},
        xAxis: Object.assign({}, {type: current_data.dtypes[chart_options.x_index], name: chart_options.xaxis}, axis_opts),
        yAxis: Object.assign({}, {type: current_data.dtypes[chart_options.y_index], name: chart_options.yaxis}, axis_opts),
        series: series,
    };
    if (chart_options.type === 'heatmap') {
        var heat_data = series[0].data.map(el => el[2])
        echarts_conf.series[0]['label'] = {show: true};
        echarts_conf['visualMap'] = {min: Math.min(...heat_data), max: Math.max(...heat_data) , type: 'continuous', dimension: 2, seriesIndex: 0, };
        // color conf https://echarts.apache.org/en/option.html#visualMap-continuous.inRange
    }
    var chart = echarts.init(chart_el);
    chart.setOption(echarts_conf);
}
