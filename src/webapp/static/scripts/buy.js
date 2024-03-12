// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))
    let plotDivId = 'historyPlot'

    renderHistoryPlot(historyData, plotDivId)
})

/**
 * creates interactive plot of stock price history
 * @param {JSON} data - portfolio history  
 */
let renderHistoryPlot = (data, plotDivId) => {
    let plotData = {
        x: data['date'],
        close: data['close'],
        high: data['high'],
        low: data['low'],
        open: data['open'],

        // cutomise colors
        increasing: {line: {color: 'green'}},
        decreasing: {line: {color: 'red'}},

        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y'
    }

    let layout = {
        title: 'Price History In Last 30 Days',
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
            t: 80,
            pad: 0
        },

        dragmode: false,

        xaxis: {
            rangeslider: {
                visible: false
            },
            showgrid: false
        },

        yaxis: {
            autorange: true,
            fixedrange: false,
            type: 'linear',
            tickangle: -45,
            showgrid: false
        }
    }

    Plotly.newPlot(plotDivId, [plotData], layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize(plotDivId)
          }
    })
}   


/**
 * Validates that user can afford to buy stock
 */
let validateBuy = () => {
    let numShares = Number(document.getElementById('shares').value)
    let maxShares = Number(document.getElementById('buyForm').getAttribute('data-max-shares'))
    let ticker = document.getElementById('ticker').value
    let price = Number(document.getElementById('price').value)

    if (numShares > maxShares) {
        flashMessage(`You cannot afford ${numShares} shares of ${ticker}!`, 'danger')
    } else if (numShares == 0) {
        flashMessage(`You must buy at least 1 share of ${ticker}!`, 'danger')
    } else {
        openConfirmPopup(numShares, ticker, price)
    }
}


/**
 * Opens the buying confirmation popup
 * 
 * @param {Integer} numShares - The number of shares user wants to buy
 * @param {String} ticker - The ticker symbol of the stock
 * @param {Float} price - The current price of the stock
 */
let openConfirmPopup = (numShares, ticker, price) => {
    let confirmPopup = new bootstrap.Modal(document.getElementById('confirmPopup'))
    let textElement = document.getElementById('confirmText')

    textElement.textContent = `Are you sure you want to buy ${numShares} shares of ${ticker} worth $${(numShares*price).toFixed(2)}?`

    confirmPopup.show()
}
