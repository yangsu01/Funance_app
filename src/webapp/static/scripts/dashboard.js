// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')

    let transactionData = JSON.parse(dataContainer.getAttribute('data-transactions'))
    let holdingsData = JSON.parse(dataContainer.getAttribute('data-holdings'))
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))
    let holdingsPieData = JSON.parse(dataContainer.getAttribute('data-holdings-pie'))
    let sectorPieData = JSON.parse(dataContainer.getAttribute('data-sector-pie'))

    let historyPlotDiv = 'historyPlot'
    let holdingsPieChartDiv = 'holdingsPie'
    let sectorPieChartDiv = 'sectorPie'

    if (holdingsData.length > 0) {
        renderTable(holdingsData, 'holdingsTable')
        populateSellDropdown(holdingsData)

        renderPieChart(holdingsPieData, holdingsPieChartDiv, 'Holdings Breakdown')
        renderPieChart(sectorPieData, sectorPieChartDiv, 'Sector Breakdown')
    }

    if (transactionData.length > 0) {
        renderTable(transactionData, 'transactionsTable')
    }

    if (historyData['date'].length > 1) {
        renderHistoryPlot(historyData, historyPlotDiv)
    } else {
        document.getElementById('historyPlot').innerHTML = '<h3 class="text-center my-5">No history available yet!</h3>'
    }
})


/**
 * Opens popup
 */
let openPopup = (popupId) => {
    let popup = new bootstrap.Modal(document.getElementById(popupId))
    popup.show()
}


/**
 * creates interactive plot of portfolio performance history
 * @param {JSON} data - portfolio history  
 */
let renderHistoryPlot = (data, historyPlotDiv) => {
    let dates = data['date']
    let values = data['value']

    let indexes = dates.map((date, index) => index)

    let plotData = {
        x: indexes,
        y: values,
        type: 'scatter',
        marker: {color: 'blue'},
        name: 'Portfolio Value',
        line: {color: '#17BECF'}
    }

    let layout = {
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',

        font: {
            size: 12,
            color: '#FFFFFF'
        },

        margin: {
            l: 30,
            r: 30,
            b: 50,
            t: 50,
            pad: 0
        },

        xaxis: {
            autorange: true,
            tickvals: indexes,
            ticktext: dates,
            tickmode: 'array',
            showgrid: false,
            showticklabels: false
        },

        yaxis: {
            autorange: true,
            type: 'linear',
            tickangle: -45,
            showgrid: false
        }
    }

    Plotly.newPlot(historyPlotDiv, [plotData], layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize(historyPlotDiv)
          }
    })
}


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
    tr.append($('<th scope="col">').text('#'))
    $.each(data[0], (key, value) => {
        tr.append($('<th scope="col">').text(key))   
    })
    thead.append(tr)
    table.append(thead)

    // append data
    $.each(data, (index, row) => {
        tr = $('<tr>')
        tr.append($('<th scope="row">').text(index + 1))
        $.each(row, (key, value) => {
            tr.append($('<td>').text(value))
        })
        tbody.append(tr)
    })
    table.append(tbody)

    $(`#${tableId}`). DataTable({searching: false})
}


/**
 * Populates the buy dropdown with tickers of holdings in the portfolio
 */
let populateSellDropdown = (data) => {
    let dropdown = document.getElementById('sellDropdown')
    let option = document.createElement('option')
    option.text = 'Select ticker'
    option.value = ''
    dropdown.append(option)

    data.forEach(data => {
        let option = document.createElement('option')
        option.text = data['Ticker']
        option.value = data['Ticker']
        dropdown.append(option)
    })
}


let renderPieChart = (data, plotDiv, title) => {

    let plotData = [{
        type: 'pie',
        values: data['values'],
        labels: data['labels'],
        domain: {column: 0},
        textinfo: 'label',
        hoverinfo: 'label+percent+value',
        insidetextorientation: "radial"
    }]

    let layout = {
        title: {
            text: title,
            font: {
                size: 16
            }
        },
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',

        font: {
            size: 10,
            color: '#FFFFFF'
        },

        margin: {
            l: 20,
            r: 20,
            b: 50,
            t: 100,
            pad: 0
        },

        showlegend: false
    };
    
    Plotly.newPlot(plotDiv, plotData, layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize(plotDiv)
          }
    })
}