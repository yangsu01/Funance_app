// frontend message flashing
let flashMessage = (message, type='danger') => {
 
    // create a div element
    let alert = document.createElement('div')
 
    // add bootrap classes
    alert.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'fade', 'show')
 
    // add alert content
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `

    let alertDiv = document.getElementById('alertMessage')

    alertDiv.appendChild(alert)
    
    alert.style.diaplay = 'block'

    // remove the alert after 3 seconds
    setTimeout(() => {
        alert.remove()
    }, 3000)
}