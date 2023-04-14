var chart_id = '{{ echart_id }}'
var current_data = null;
var initial_viz = true;
var saved_viz = {{ viz }};

function array_ident(arr1, arr2) {
    // https://stackoverflow.com/a/19746771
    return (arr1.length === arr2.length && arr1.every((value, index) => value === arr2[index]))
}
function get_chart_options() {
    var chart_options = {
        type: document.getElementById('echart-options-type').value,
        xaxis: document.getElementById('echart-options-xaxis').value,
        yaxis: document.getElementById('echart-options-yaxis').value,
        zaxis: document.getElementById('echart-options-zaxis').value,
        group: document.getElementById('echart-options-group').value,
    }
    return chart_options
}
window.get_chart_options = get_chart_options;
function update_chart_options() {
    var select_ids = ['echart-options-xaxis', 'echart-options-yaxis', 'echart-options-zaxis','echart-options-group', ];
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
                document.getElementById('echart-options-zaxis').value = saved_viz.zaxis;
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
    // this function wraps viz creation for query page
    try {
        var chart_el = document.getElementById(chart_id);
        var chart_options = get_chart_options();
        if (current_data === null || current_data.data.length === 0) {
            document.getElementById('echart-note').classList.remove("hidden");
            document.getElementById('echart-chart').classList.add("hidden");
            throw new Error('no data available');
        } else {
            document.getElementById('echart-note').classList.add("hidden");
            document.getElementById('echart-chart').classList.remove("hidden");
            create_viz(current_data, chart_options, chart_el);
        }
    } catch (error) {
        console.error(`Failed to draw chart`);
        console.error(error);
        create_error(chart_id, error)
    }
}
