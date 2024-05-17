import Alpine from 'alpinejs'
import morph from '@alpinejs/morph'
import '../styles/index.css'
import './htmx_file.js'
import './htmx-alpine-morph.js'
var moment = require('moment');

window.Alpine = Alpine
Alpine.plugin(morph)


Alpine.start()

if (window.location.pathname === '/') {

    document.addEventListener('DOMContentLoaded', () => {
        console.log(new Date().toISOString());
        document.getElementById('page-title').textContent += ' My bundle is still running ' + moment().format();
        var update = function() {
            document.getElementById('datetime').innerHTML = moment().format('MMMM Do YYYY, h:mm:ss a');
        };
        setInterval(update, 1000);
    });

    var sidebarOffcanvas = document.getElementById('offcanvasSidebar');
    sidebarOffcanvas.addEventListener('hidden.bs.offcanvas', function() {
        const canvasHeader = document.getElementById('offcanvasSidebarLabel');
        const canvasBody = document.getElementById('offcanvasBody');

        canvasHeader.innerHTML = '';
        canvasBody.innerHTML = '';
    })


}