import { apiFetch } from "./modules/generalApi.js";
import { requireAuth } from "./modules/authGuard.js";

document.addEventListener("DOMContentLoaded", async () => {
    const allowed = await requireAuth();
    if (!allowed) return;

    loadTickets();
});

async function loadTickets() {
    try {
        const data = await apiFetch("/api/orders/my-tickets/");
        const container = document.getElementById("tickets");

        if (!data.length) {
            container.innerHTML = "<p>Bạn chưa có vé nào.</p>";
            return;
        }

        container.innerHTML = data.map(ticket => `
            <div class="ticket-card">
                <h3>${ticket.event}</h3>
                <p>${ticket.ticket_type}</p>
                <p>${ticket.date || ""}</p>
                <img src="${ticket.qr_code}" alt="QR Code">

                <p class="${ticket.is_used ? 'used' : 'unused'}">
                    ${ticket.is_used ? "Đã sử dụng" : "Chưa sử dụng"}
                </p>
            </div>
        `).join("");

    } catch (err) {
        console.error(err);
        document.getElementById("tickets").innerHTML =
            "<p>Lỗi khi tải vé</p>";
    }
}