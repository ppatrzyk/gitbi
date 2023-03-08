try {
    var viz_spec = JSON.parse(`{{ viz }}`);
    // TODO set defaults on chart if this exists
    console.log(viz_spec)
    // TODO stop when data not yet available
    // console.log(document.data)
    // TODO re-render on document.data change
    var chart_el = document.getElementById('echart');
    chart_el.style.width = `${chart_el.offsetWidth}px`;
    chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
    var chart = echarts.init(chart_el);
    option = {
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
    chart.setOption(option);
    // TODO echarts interactivity
} catch (error) {
    console.error(`Failed to draw chart`);
    console.error(error);
}