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
}