import { requireAuth } from "./modules/authGuard.js";
import { apiFetch } from "./modules/generalApi.js";

document.addEventListener("DOMContentLoaded", async () => {
    const allowed = await requireAuth();
    
    if (!allowed) {
        document.querySelector(".checkout").style.display = "none";
        throw new Error("Not authenticated");
    }
});


async function loadTickets() {
    const data = await apiFetch("/api/orders/my-tickets/");

    const container = document.getElementById("tickets");

    container.innerHTML = data.map(t => `
        <div class="ticket-card">
            <h3>${t.event}</h3>
            <p>${t.ticket_type}</p>
            <p>${t.date} ${t.time || ""}</p>
            <img src="${t.qr_code}" width="150">
        </div>
    `).join("");
}

loadTickets();