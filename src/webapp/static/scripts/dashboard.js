
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
        renderHoldingsTable(holdingsData)
    }

    if (transactionData.length > 0) {
        renderTransactionTable(transactionData)
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
 * Renders the holdings table
 * @param {JSON} data - holdings data
 */
let renderHoldingsTable = (data) => {

}


/**
 * Renders the transaction table
 * @param {JSON} data - transaction data
 */
let renderTransactionTable = (data) => {
    let table = $('#transactionTable')

    $.each(data, (index, row) => {
        let tr = $('<tr>')
        $.each(row, (key, value) => {
            tr.append($('<td>').text(value))
        })
        table.append(tr)
    })

    console.log(data)
}