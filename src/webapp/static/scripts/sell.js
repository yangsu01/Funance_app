/**
 * Validates that user can afford to buy stock
 */
let validateSell = () => {
    let numShares = Number(document.getElementById('shares').value)
    let maxShares = Number(document.getElementById('sellForm').getAttribute('data-max-shares'))
    let ticker = document.getElementById('ticker').value
    let price = Number(document.getElementById('price').value)

    if (numShares > maxShares) {
        flashMessage(`You do not own ${numShares} shares of ${ticker}!`, 'danger')
    } else if (numShares == 0) {
        flashMessage(`You must sell at least 1 share of ${ticker}!`, 'danger')
    } else {
        openConfirmPopup(numShares, ticker, price)
    }
}


/**
 * Opens the selling confirmation popup
 * 
 * @param {Integer} numShares - The number of shares user wants to buy
 * @param {String} ticker - The ticker symbol of the stock
 * @param {Float} price - The current price of the stock
 */
let openConfirmPopup = (numShares, ticker, price) => {
    let confirmPopup = new bootstrap.Modal(document.getElementById('confirmPopup'))
    let textElement = document.getElementById('confirmText')

    textElement.textContent = `Are you sure you want to sell ${numShares} shares of ${ticker} for $${(numShares*price).toFixed(2)}?`

    confirmPopup.show()
}
