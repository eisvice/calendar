import Alpine from 'alpinejs'
import morph from '@alpinejs/morph'
import { Calendar } from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import 'bootstrap/dist/css/bootstrap.min.css';
import Offcanvas from 'bootstrap/js/dist/offcanvas.js'
import '../styles/index.css'
import './htmx_file.js'
import 'htmx.org/dist/ext/response-targets.js'
var moment = require('moment');
window.moment = moment; // This makes it accessible globally

window.Alpine = Alpine

Alpine.start()

const csrftoken = getCookie('csrftoken');

if (window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('htmx:beforeSwap', (e) => {
          console.log('before swap', e.detail.elt);
          if (e.detail.xhr.status === 422) {
            (console.log(e.detail));
            // allow 422 responses to swap as we are using this as a signal that
            // a form was submitted with bad data and want to rerender with the
            // errors
            //
            // set isError to false to avoid error logging in console
            e.detail.shouldSwap = true;
            e.detail.isError = false;
            (console.log(e.detail));
    
          } else if (e.detail.elt.id === 'settings-content' || e.detail.elt.classList.contains('event-group-row') ) {
            callCalendar();
          }
        });
        
        htmx.on('htmx:afterRequest', (e) => {
          console.log('after request', e.detail.elt);
          if (e.detail.elt.id === 'offcanvasBody') {
            callCalendar();
          }
        });
    
        callCalendar();

    });
    
    var sidebarOffcanvas = document.getElementById('offcanvasSidebar');
    sidebarOffcanvas.addEventListener('hidden.bs.offcanvas', function() {
        const canvasHeader = document.getElementById('offcanvasSidebarLabel');
        const canvasDescription = document.querySelector('#offcanvasDescription');
        const canvasBody = document.getElementById('offcanvasBody');

        canvasHeader.innerHTML = '';
        canvasDescription.innerHTML = '';
        canvasBody.innerHTML = '';
    })

}


function callCalendar() {
var calendarEl = document.getElementById('calendar');
var calendar = new Calendar(calendarEl, {
    nowIndicator: true,
    weekNumberCalculation: "ISO",
    views: {
        timeGridWeek: {
            dayHeaderFormat: { weekday: 'short', day: 'numeric', month: 'numeric'}
        }
    },
    slotMinTime: '08:00:00',
    contentHeight:"auto",
    plugins: [dayGridPlugin,timeGridPlugin,listPlugin],
    initialView: 'timeGridWeek',
    headerToolbar: {
        left: 'dayGridMonth,timeGridWeek,listWeek',
        center: 'title',
        right: 'prev,today,next'
    },
    events: datesUrl,
    eventClick: function(info) {
    console.log(moment().format());
    console.log(info.event)
    // Get the offcanvas element
    var offcanvasEl = document.getElementById('offcanvasSidebar');
    offcanvasEl.querySelector('#offcanvasSidebarLabel').innerHTML = `${info.event.title}`;
    if (info.event.extendedProps.description) {
        offcanvasEl.querySelector('#offcanvasDescription').innerHTML = `Description:<br/>${info.event.extendedProps.description}`;
    }
    // Set the event details as the content of the offcanvas
    offcanvasEl.querySelector('#offcanvasBody').innerHTML = `
        <form hx-post="${editThemeUrl}" hx-target="#offcanvasBody" hx-headers='{"X-CSRFToken": "${csrftoken}"}'>
        <input id="event-id" name="event-id" class="form-control" type="number" value="${info.event.id}" hidden/>
        <div class="mb-3">
            <label for="old-start-time" class="form-label">Current Appointment:</label>
            <input id="old-start-time" name="old-start-time" class="form-control" type="datetime-local" value="${moment(info.event.start).format('YYYY-MM-DDTHH:mm:ss')}" disabled readonly/>
        </div>
        <div class="mb-3">
            <label for="old-duration" class="form-label">Current Duration:</label>
            <input id="old-duration" name="old-duration" class="form-control" type="time" value="${info.event.extendedProps.hours}" disabled readonly/>
        </div>
        <div class="mb-3">
            <label for="new-start-time" class="form-label">New Appointment:</label>
            <input id="new-start-time" name="new-start-time" class="form-control" type="datetime-local" value="${moment(info.event.start).format('YYYY-MM-DDTHH:mm:ss')}"/>
        </div>
        <div class="mb-3">
            <label for="new-duration" class="form-label">Duration:</label>
            <input id="new-duration" name="new-duration" class="form-control" type="time" value="${info.event.extendedProps.hours}"/>
        </div>
        <div class="d-grid gap-2 col-11 mx-auto" style="margin-top: 30px;">
            <button type="submit" class="btn btn-primary" data-bs-dismiss="offcanvas">Save</button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="offcanvas" aria-label="Close">Close</button>
        </div>
        </form>
        `;
        
    // Trigger the offcanvas
    var offcanvas = new Offcanvas(offcanvasEl);
    offcanvas.show();
    htmx.process(document.getElementById('offcanvasBody'));
    }
});
calendar.render();
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

