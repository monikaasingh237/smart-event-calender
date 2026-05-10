// ================= STATE =================
let selectedDate = null;
let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();
let events = [];

const calendar = document.getElementById("calendar");

if (calendar) {
    loadEvents().then(() => renderCalendar(currentMonth, currentYear));
}

// ================= CALENDAR =================
function renderCalendar(month, year) {
    calendar.innerHTML = "";

    const firstDay = new Date(year, month).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Empty spaces
    for (let i = 0; i < firstDay; i++) {
        calendar.appendChild(document.createElement("div"));
    }

    for (let i = 1; i <= daysInMonth; i++) {
        let day = document.createElement("div");
        day.classList.add("day");

        let monthStr = String(month + 1).padStart(2, '0');
        let dayStr = String(i).padStart(2, '0');
        let dateStr = `${year}-${monthStr}-${dayStr}`;

        day.innerHTML = `<strong>${i}</strong>`;

        let dayEvents = events.filter(e => e.date === dateStr);

        dayEvents.forEach(e => {
            let ev = document.createElement("div");
            ev.classList.add("event");

            ev.innerText = `${e.title} (${e.start_time})`;

            if (e.status === "pending") ev.style.background = "gray";
            else if (e.status === "pending_cancel") ev.style.background = "orange";
            else if (e.status === "cancelled") ev.style.background = "red";
            else ev.style.background = "green";

            if (getUserRole() === "user" && e.status === "scheduled") {
                let btn = document.createElement("button");
                btn.innerText = "Cancel";
                btn.onclick = () => requestCancel(e.id);
                ev.appendChild(btn);
            }

            day.appendChild(ev);
        });

        day.onclick = () => {
            selectedDate = dateStr;
            document.getElementById("eventModal").style.display = "block";
        };

        calendar.appendChild(day);
    }
}

// ================= EVENTS =================
async function loadEvents() {
    let res = await fetch("http://127.0.0.1:8000/events");
    events = await res.json();
}

async function saveEvent() {
    let title = document.getElementById("eventTitle").value;
    let start = document.getElementById("startTime").value;
    let end = document.getElementById("endTime").value;

    let newEvent = {
        id: Date.now(),
        title,
        date: selectedDate,
        start_time: start,
        end_time: end,
        user_id: getUserId(),
        status: "pending"
    };

    await fetch("http://127.0.0.1:8000/create-event", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(newEvent)
    });

    closeModal();
    loadEvents().then(() => renderCalendar(currentMonth, currentYear));
}

async function requestCancel(id) {
    await fetch(`http://127.0.0.1:8000/request-cancel/${id}`, {
        method: "PUT"
    });

    loadEvents().then(() => renderCalendar(currentMonth, currentYear));
}

function closeModal() {
    document.getElementById("eventModal").style.display = "none";
}

// ================= USER =================
function getUserId() {
    return localStorage.getItem("user_id");
}

function getUserRole() {
    return localStorage.getItem("role");
}