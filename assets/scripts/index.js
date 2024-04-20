import Alpine from 'alpinejs'
import '../styles/index.css'
var moment = require('moment');
 
window.Alpine = Alpine

Alpine.start()

window.htmx = require('htmx.org');

document.addEventListener('DOMContentLoaded', () => {
    console.log(new Date().toISOString());
    document.getElementById('page-title').textContent += ' My bundle is still running ' + moment().format();
    var update = function() {
        document.getElementById('datetime').innerHTML = moment().format('MMMM Do YYYY, h:mm:ss a');
    };
    setInterval(update, 1000);
});



