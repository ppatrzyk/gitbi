var chart_id = '{{ echart_id }}'
var currentData = null;
var initialViz = true;
var savedViz = {{ viz }};

function arrayIdent(arr1, arr2) {
    // https://stackoverflow.com/a/19746771
    return (arr1.length === arr2.length && arr1.every((value, index) => value === arr2[index]))
}
function getChartOptions() {
    var chartOptions = {
        type: document.getElementById('echart-options-type').value,
        xaxis: document.getElementById('echart-options-xaxis').value,
        yaxis: document.getElementById('echart-options-yaxis').value,
        zaxis: document.getElementById('echart-options-zaxis').value,
        group: document.getElementById('echart-options-group').value,
    }
    return chartOptions
}
window.getChartOptions = getChartOptions;
function updateChartOptions() {
    var selectIds = ['echart-options-xaxis', 'echart-options-yaxis', 'echart-options-zaxis','echart-options-group', ];
    var headings = Array.from(document.getElementById(selectIds[0]).getElementsByTagName('option')).map((node) => node.value)
    var newHeadings = ['_NONE', ].concat(currentData.headings);
    if (!arrayIdent(headings, newHeadings)) {
        selectIds.forEach(id => {
            var columns = newHeadings.map((name) => {
                var entry = document.createElement("option");
                entry.setAttribute('value', name);
                entry.innerText = name;
                return entry
            })
            document.getElementById(id).replaceChildren(...columns);
        });
        if (initialViz) {
            initialViz = false;
            if (savedViz !== null) {
                document.getElementById('echart-options-type').value = savedViz.type;
                document.getElementById('echart-options-xaxis').value = savedViz.xaxis;
                document.getElementById('echart-options-yaxis').value = savedViz.yaxis;
                document.getElementById('echart-options-zaxis').value = savedViz.zaxis;
                document.getElementById('echart-options-group').value = savedViz.group;
            }
        } else {
            selectIds.forEach(id => {
                document.getElementById(id).value = "_NONE";
            })
            document.getElementById('echart-options-type').value = "scatter"
        }
    }
}
function makeViz() {
    // this function wraps viz creation for query page
    try {
        var chartEl = document.getElementById(chart_id);
        var chartOptions = getChartOptions();
        if (currentData === null || currentData.data.length === 0) {
            document.getElementById('echart-note').classList.remove("hidden");
            document.getElementById('echart-chart').classList.add("hidden");
            throw new Error('no data available');
        } else {
            document.getElementById('echart-note').classList.add("hidden");
            document.getElementById('echart-chart').classList.remove("hidden");
            createViz(currentData, chartOptions, chartEl);
        }
    } catch (error) {
        console.error(`Failed to draw chart`);
        console.error(error);
        alert(error)
    }
}
