import { formatPrice } from "./modules/formatPrice.js";

const id = event_id;

const response = await fetch(`/api/events/${id}/`);
if (!response.ok) {
    document.body.innerHTML = "<div align='center'>Sự kiện không tồn tại.</div>";
    throw new Error("Event not found");
}

const event = await response.json();

if (event && !event.error) {
    const normalizedTickets = [...event.tickets].sort((a, b) => a.gia - b.gia);

    document.getElementById("tenSuKien").innerText = event.ten;
    document.getElementById("anhBanner").src = event.anh;
    document.getElementById("displayDate").innerText = event.displayDate + ": ";
    document.getElementById("startTime").innerText = event.startTime + " - ";
    document.getElementById("endTime").innerText = event.endTime;
    document.getElementById("diaChiTen").innerText = event.dcTen;
    document.getElementById("diaChiCuThe").innerText = event.dcCuThe;
    document.getElementById("moTa").innerHTML = event.moTa;

    const quantitySelect = document.getElementById("soLuongVe");
    const totalPriceEl = document.getElementById("tongTien");

    let selectedTicket = null;

    const syncPriceSummary = () => {
        if (!selectedTicket) {
            totalPriceEl.innerText = "—";
            return;
        }

        const quantity = Number(quantitySelect.value);
        const totalPrice = selectedTicket.gia * quantity;

        totalPriceEl.innerText = formatPrice(totalPrice);
        
        // Update the global amount variable for PayPal
        window.amount = totalPrice.toFixed(2);
    };

    let ticketsHTML =
        `<tr>
            <th align='left'>Loại vé</th>
            <th align='right'>Giá vé</th>
        </tr>`;

    normalizedTickets.forEach(ticket => {
        ticketsHTML +=
        `<tr class="ticket-row" data-loai="${ticket.loai}" data-gia="${ticket.gia}">
            <td>${ticket.loai}</td>
            <td align="right">${formatPrice(ticket.gia)}</td>
        </tr>`;
    });

    document.getElementById("bangGiaVe").innerHTML = ticketsHTML;

    document.querySelectorAll(".ticket-row").forEach(row => {
        row.addEventListener("click", () => {
            document.querySelectorAll(".ticket-row").forEach(r => r.classList.remove("selected"));
            row.classList.add("selected");
            selectedTicket = { loai: row.dataset.loai, gia: Number(row.dataset.gia) };
            syncPriceSummary();
        });
    });

    quantitySelect.addEventListener("change", () => {
        syncPriceSummary();
    });

    const firstTicketRow = document.querySelector(".ticket-row");
    if (firstTicketRow) {
        firstTicketRow.classList.add("selected");
        selectedTicket = {
            loai: firstTicketRow.dataset.loai,
            gia: Number(firstTicketRow.dataset.gia)
        };
        syncPriceSummary();
    }

    document.title = "QRticket | " + event.ten;
}