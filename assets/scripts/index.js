import Alpine from 'alpinejs'
import '../styles/index.css'
import { off } from 'htmx.org';
var moment = require('moment');

window.Alpine = Alpine


window.htmx = require('htmx.org');
Alpine.start()


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

// fill start filed value with current time and select checkbox on change
const startField = document.getElementById('id_start');
startField.value = moment().format('yyyy-MM-DDTHH:mm');

// create a new mutation observer
const observer = new MutationObserver((mutationsList, observer) => {
    for(let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            let dayTimeFieldId = `time-${moment(startField.value).isoWeekday() - 1}`;
            let timeField = document.getElementById(dayTimeFieldId);
            if(timeField) {
                timeField.value = moment(startField.value).format('HH:mm');
                observer.disconnect(); // disconnect observer when done
            }
        }
    }
});

// start observing the document with the configured parameters
observer.observe(document.body, { childList: true, subtree: true });

startField.onchange = () => {
    let startTimeDay = startField.value;
    // let startTime = moment(startField.value).format('HH:mm');
    console.log(startTimeDay);
    console.log(moment(startTimeDay).format('dddd'));
    console.log(moment(startTimeDay).isoWeekday() - 1);
    let checkBoxId = `checkbox-${moment(startTimeDay).format('dddd').toLowerCase()}`;
    // let dayTimeFieldId = `time-${moment(startTimeDay).isoWeekday() - 1}`;
    // console.log(`checkbox id: ${checkBoxId}, day time id: ${dayTimeFieldId}`);
    document.getElementById(checkBoxId).checked = true;
}


