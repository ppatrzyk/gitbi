function make_viz(chart_el, event_data) {
    if (event_data.id == 'results-table') {
        try {
            var data = event_data.data;
            console.log('make_viz called');
            console.log(data);
            chart_el.style.width = `${chart_el.offsetWidth}px`;
            chart_el.style.height = `${Math.floor(chart_el.offsetWidth * 0.5)}px`;
            var chart = echarts.init(chart_el);
            // TODO plot actual data here, options what taken from form
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
        } catch (error) {
            console.error(`Failed to draw chart`);
            console.error(error);
        }
    }
}
var viz_spec = JSON.parse(`{{ viz }}`);
// TODO set defaults on chart if this exists
// TODO maybe this viz spec is needed only when generating initial html (default choices )
console.log(viz_spec);
var chart_el = document.getElementById('echart');
chart_el.addEventListener("newdata", (e) => make_viz(chart_el, e.detail));
