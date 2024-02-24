// on page load
document.addEventListener('DOMContentLoaded', () => {
    let dataContainer = document.getElementById('data-container')

    let transactionData = JSON.parse(dataContainer.getAttribute('data-transactions'))
    let holdingsData = JSON.parse(dataContainer.getAttribute('data-holdings'))
    let historyData = JSON.parse(dataContainer.getAttribute('data-history'))

    if (historyData.length > 0) {
        renderHistoryPlot(historyData)
    }

    if (holdingsData.length > 0) {
        renderTable(holdingsData, 'holdingsTable')
    }

    if (transactionData.length > 0) {
        renderTable(transactionData, 'transactionsTable')
    }

})


/**
 * Opens the buying stock popup
 */
let openBuyPopup = () => {
    let buyPopup = new bootstrap.Modal(document.getElementById('buyPopup'))
    buyPopup.show()
}


/**
 * creates interactive plot of portfolio performance history
 * @param {JSON} data - portfolio history  
 */
let renderHistoryPlot = (data) => {

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
}