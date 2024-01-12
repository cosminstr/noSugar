document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: true,
        selectable: true,
        select: function (info) {
            if (isAddingEvent) {
                var title = prompt('Introdu reminder:');
                if (title) {
                    var event = {
                        id: new Date().toISOString(),
                        title: title,
                        start: info.startStr,
                        end: info.endStr,
                        allDay: info.allDay,
                    };

                    calendar.addEvent(event);
                    saveEventToLocalStorage(event);
                }
                calendar.unselect();
            }
        },
        events: loadEventsFromLocalStorage(),
        eventClick: function (info) {
            if (!isAddingEvent) {
                var confirmDelete = confirm("Esti sigur ca vrei sa stergi acest reminder?");
                if (confirmDelete) {
                    info.event.remove();
                    removeEventFromLocalStorage(info.event);
                }
            }
        }
    });

    calendar.render();

    var isAddingEvent = true;

    document.getElementById('addButton').addEventListener('click', function () {
        isAddingEvent = true;
    });

    document.getElementById('deleteButton').addEventListener('click', function () {
        isAddingEvent = false;
    });

    function saveEventToLocalStorage(event) {
        var events = loadEventsFromLocalStorage();
        events.push(event);
        localStorage.setItem('calendarEvents', JSON.stringify(events));
    }

    function loadEventsFromLocalStorage() {
        var events = localStorage.getItem('calendarEvents');
        return events ? JSON.parse(events) : [];
    }

    function removeEventFromLocalStorage(event) {
        var events = loadEventsFromLocalStorage();
        events = events.filter(function (e) {
            return e.id !== event.id;
        });
        localStorage.setItem('calendarEvents', JSON.stringify(events));
    }
});

// localStorage.removeItem('calendarEvents');