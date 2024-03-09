// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')

    let topPerformersData = JSON.parse(dataContainer.getAttribute('data-top-performers'))
    let dailyPerformersData = JSON.parse(dataContainer.getAttribute('data-daily-performers'))
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))

    renderTable(topPerformersData, 'topPerformersTable')
    renderTable(dailyPerformersData, 'dailyPerformersTable')
    renderHistoryPlot(historyData)
    
})


/**
 * Renders a table in html
 * @param {JSON} data - transaction data
 */
let renderTable = (data, tableId) => {
    let table = $(`#${tableId}`)
    let thead = $('<thead>')
    let tbody = $('<tbody>')
    let tr = $('<tr>')

    // append headers
    $.each(data[0], (key, value) => {
        tr.append($('<th scope="col">').text(key))   
    })
    thead.append(tr)
    table.append(thead)

    // append data
    $.each(data, (index, row) => {
        tr = $('<tr>')
        $.each(row, (key, value) => {
            tr.append($('<td>').text(value))
        })
        tbody.append(tr)
    })
    table.append(tbody)
}


/**
 * creates interactive plot of portfolio performance history
 * @param {JSON} data - portfolio history  
 */
let renderHistoryPlot = (data) => {
    historyPlot = document.getElementById('historyPlot')

    let layout = {
        title: 'User Portfolio Values',
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',

        font: {
            size: 16,
            color: '#FFFFFF'
          },

        xaxis: {
            autorange: true,
            rangeselector: {
                bgcolor: 'black',
                buttons: [
                {
                    count: 7,
                    label: '1w',
                    step: 'day',
                    stepmode: 'backward'
                },
                {
                    count: 1,
                    label: '1m',
                    step: 'month',
                    stepmode: 'backward'
                },
                {step: 'all'}
            ]},
            title:  'Time'
        },

        yaxis: {
            autorange: true,
            type: 'linear',
            title: 'Portfolio Value ($)',
            showgrid: false
        }
    }

    Plotly.newPlot('historyPlot', data, layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize('historyPlot')
          }
    })
}