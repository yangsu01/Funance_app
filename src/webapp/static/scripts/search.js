// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))
    let ticker = dataContainer.getAttribute('data-ticker')

    renderHistoryPlot(historyData, ticker)
})

/**
 * creates interactive plot of stock price history
 * @param {JSON} data - portfolio history  
 */
let renderHistoryPlot = (data, ticker) => {
    historyPlot = document.getElementById('historyPlot')

    let x = data['Date']
    let y = data['Price']

    let plotData = {
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines',
        marker: {color: 'blue'},
        name: 'Stock Price',
        line: {color: '#17BECF'}
    }

    let layout = {
        title: `Price History of ${ticker}`,
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',

        font: {
            size: 16,
            color: '#FFFFFF'
        },

        margin: {
            l: 40,
            r: 40,
            b: 50,
            t: 100,
            pad: 0
        },

        xaxis: {
            autorange: true,
            rangeselector: {
                bgcolor: 'black',

                buttons: [
                {
                    count: 1,
                    label: '1m',
                    step: 'month',
                    stepmode: 'backward'
                },
                {
                    count: 6,
                    label: '6m',
                    step: 'month',
                    stepmode: 'backward'
                },
                {
                    step: 'year',
                    stepmode: 'todate',
                    count: 1,
                    label: 'YTD'
                },
                {
                    step: 'year',
                    stepmode: 'backward',
                    count: 1,
                    label: '1y'
                },
                {
                    step: 'all'
                }
            ]},
            rangeslider: {range: [x[0], x[x.length - 1]]},
            type: 'date'
        },

        yaxis: {
            autorange: true,
            type: 'linear',
            tickangle: -45,
            showgrid: false
        }
    }

    Plotly.newPlot('historyPlot', [plotData], layout).then(() => {
        window.onresize = function() {
            Plotly.Plots.resize('historyPlot')
          }
    })
}   