// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')

    let transactionData = JSON.parse(dataContainer.getAttribute('data-transactions'))
    let holdingsData = JSON.parse(dataContainer.getAttribute('data-holdings'))
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))

    if (holdingsData.length > 0) {
        renderTable(holdingsData, 'holdingsTable')
        populateSellDropdown(holdingsData)
    }

    if (transactionData.length > 0) {
        renderTable(transactionData, 'transactionsTable')
    }

    if (historyData['Date'].length > 1) {
        renderHistoryPlot(historyData)
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
let renderHistoryPlot = (data) => {
    historyPlot = document.getElementById('historyPlot')

    let x = data['Date']
    let y = data['Value']

    let plotData = {
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines',
        marker: {color: 'blue'},
        name: 'Portfolio Value',
        line: {color: '#17BECF'}
    }

    let layout = {
        title: 'Portfolio Value Over Time',
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
            rangeslider: {range: [x[0], x[x.length - 1]]},
            title: 'Time'
        },

        yaxis: {
            autorange: true,
            type: 'linear',
            title: 'Portfolio Value ($)',
            showgrid: false
        }
    }

    Plotly.newPlot('historyPlot', [plotData], layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize('historyPlot')
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
populateSellDropdown = (data) => {
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