import Alpine from 'alpinejs'
import '../styles/index.css'
 
window.Alpine = Alpine
 
Alpine.start()

window.htmx = require('htmx.org');

document.addEventListener('DOMContentLoaded', () => {
    console.log('I\'m working!');
    document.getElementById('page-title').textContent += ' My bundle is still running';
});