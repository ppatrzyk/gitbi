function get_val(row, index, dtypes) {
    return (dtypes[index] === 'time') ? new Date(row[index]) : row[index];
}
function format_row(row, chart_options, current_data) {
    var x = get_val(row, chart_options.x_index, current_data.dtypes);
    var y = get_val(row, chart_options.y_index, current_data.dtypes);
    var z = get_val(row, chart_options.z_index, current_data.dtypes);
    return [x, y, z]
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
    chart_options.z_index = current_data.headings.indexOf(chart_options.zaxis);
    chart_options.group_index = current_data.headings.indexOf(chart_options.group);
    chart_el.replaceChildren();
    chart_el.removeAttribute('_echarts_instance_')
    chart_el.style.width = `${chart_el.offsetWidth}px`;
    chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
    var title = `${chart_options.xaxis} x ${chart_options.yaxis}`;
    if (chart_options.group === '_NONE') {
        var series = series_single(current_data, chart_options);
    } else {
        if (chart_options.type === 'heatmap') {
            throw new Error('group does not make sense for this chart type');
        }
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
    if (chart_options.zaxis !== '_NONE') {
        var in_range;
        if (chart_options.type === 'heatmap') {
            echarts_conf.series.forEach(el => el['label'] = {show: true});
            in_range = {color: ['rgb(252, 255, 164)', 'rgb(249, 142, 9)', 'rgb(188, 55, 84)', 'rgb(87, 16, 110)', 'rgb(0, 0, 4)']};
        } else if (['line', 'scatter'].includes(chart_options.type)) {
            in_range = {symbolSize: [10, 60]}
        } else {
            throw new Error('z axis does not make sense for this chart type');
        }
        var z_data = series.map(el => el.data).flat().map(el => el[2])
        echarts_conf['visualMap'] = {min: Math.min(...z_data), max: Math.max(...z_data) , type: 'continuous', dimension: 2, inRange: in_range};
    }
    var chart = echarts.init(chart_el);
    chart.setOption(echarts_conf);
}