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
    let x = data['date']
    let y = data['price']

    let plotData = {
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines',
        marker: {color: 'blue'},
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
            t: 80,
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
                        count: 1,
                        label: 'YTD',
                        step: 'year',
                        stepmode: 'todate'
                    },
                    {
                        count: 1,
                        label: '1y',
                        step: 'year',
                        stepmode: 'backward'
                    },
                    {step: 'all'}
                ]
            },
            rangeslider: {range: [x[0], x[x.length - 1]]},
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