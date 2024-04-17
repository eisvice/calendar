import Alpine from 'alpinejs'
import '../styles/index.css'
var moment = require('moment');
 
window.Alpine = Alpine

Alpine.start()

window.htmx = require('htmx.org');

document.addEventListener('DOMContentLoaded', () => {
    console.log('I\'m working!');
    document.getElementById('page-title').textContent += ' My bundle is still running ' + moment().format(); 
});



