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
