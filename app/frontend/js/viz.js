function getVal(row, index, dtypes) {
    return (dtypes[index] === 'time') ? new Date(row[index]) : row[index];
}
function formatRow(row, chartOptions, currentData) {
    var x = getVal(row, chartOptions.xIndex, currentData.dtypes);
    var y = getVal(row, chartOptions.yIndex, currentData.dtypes);
    var z = getVal(row, chartOptions.zIndex, currentData.dtypes);
    return [x, y, z]
}
function seriesSingle(currentData, chartOptions) {
    var data = currentData.data.map(row => formatRow(row, chartOptions, currentData));
    var series = [{data: data, type: chartOptions.type, name: chartOptions.yaxis}];
    return series
}
function seriesMulti(currentData, chartOptions) {
    var series = {};
    currentData.data.forEach(row => {
        if (series[row[chartOptions.groupIndex]] === undefined) {
            series[row[chartOptions.groupIndex]] = {data: [formatRow(row, chartOptions, currentData), ], type: chartOptions.type, name: chartOptions.group};
        } else {
            series[row[chartOptions.groupIndex]].data.push(formatRow(row, chartOptions, currentData));
        }
    });
    series = Object.keys(series).map(k => {return Object.assign({}, series[k], {name: k})});
    return series
}
function createViz(currentData, chartOptions, chartEl) {
    var axisOpts = {nameLocation: 'middle', nameTextStyle: {padding: 20}, splitArea: {show: true}, }
    if (['line', 'scatter'].includes(chartOptions.type)) {
        axisOpts.min = function (value) {return value.min - ((value.max-value.min)*0.1);};
        axisOpts.max = function (value) {return value.max + ((value.max-value.min)*0.1);};
    }
    chartOptions.xIndex = currentData.headings.indexOf(chartOptions.xaxis);
    chartOptions.yIndex = currentData.headings.indexOf(chartOptions.yaxis);
    chartOptions.zIndex = currentData.headings.indexOf(chartOptions.zaxis);
    chartOptions.groupIndex = currentData.headings.indexOf(chartOptions.group);
    chartEl.replaceChildren();
    chartEl.removeAttribute('_echarts_instance_')
    chartEl.style.width = `${chartEl.offsetWidth}px`;
    chartEl.style.height = `${Math.floor(chartEl.offsetWidth * 0.5)}px`;
    var title = `${chartOptions.xaxis} x ${chartOptions.yaxis}`;
    if (chartOptions.group === '_NONE') {
        var series = seriesSingle(currentData, chartOptions);
    } else {
        if (chartOptions.type === 'heatmap') {
            throw new Error('group does not make sense for this chart type');
        }
        var series = seriesMulti(currentData, chartOptions);
    }
    var echartsConf = {
        legend: {show: true, top: 20, },
        toolbox: {show: true, feature: {saveAsImage: {show: true}}},
        tooltip: {show: true, triggerOn: "mousemove", },
        title: {show: true, text: title},
        textStyle: {fontFamily: 'Ubuntu', fontSize: 16},
        xAxis: Object.assign({}, {type: currentData.dtypes[chartOptions.xIndex], name: chartOptions.xaxis}, axisOpts),
        yAxis: Object.assign({}, {type: currentData.dtypes[chartOptions.yIndex], name: chartOptions.yaxis}, axisOpts),
        series: series,
    };
    if (chartOptions.zaxis !== '_NONE') {
        var inRange;
        if (chartOptions.type === 'heatmap') {
            echartsConf.series.forEach(el => el['label'] = {show: true});
            inRange = {color: ['rgb(252, 255, 164)', 'rgb(249, 142, 9)', 'rgb(188, 55, 84)', 'rgb(87, 16, 110)', 'rgb(0, 0, 4)']};
        } else if (['line', 'scatter'].includes(chartOptions.type)) {
            inRange = {symbolSize: [10, 60]}
        } else {
            throw new Error('z axis does not make sense for this chart type');
        }
        var z_data = series.map(el => el.data).flat().map(el => el[2])
        echartsConf['visualMap'] = {min: Math.min(...z_data), max: Math.max(...z_data) , type: 'continuous', dimension: 2, inRange: inRange};
    }
    var chart = echarts.init(chartEl);
    chart.setOption(echartsConf);
}