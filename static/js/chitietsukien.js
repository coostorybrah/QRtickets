import { formatPrice } from "./modules/formatPrice.js";

const id = String(event_id);

const response = await fetch(`/api/events/${id}`);
const event = await response.json();

if (event && !event.error) {
    document.getElementById("tenSuKien").innerText = event.ten;
    document.getElementById("anhBanner").src = event.anh;
    document.getElementById("displayDate").innerText = event.displayDate + ": ";
    document.getElementById("startTime").innerText = event.startTime + " - ";
    document.getElementById("endTime").innerText = event.endTime;
    document.getElementById("diaChiTen").innerText = event.dcTen;
    document.getElementById("diaChiCuThe").innerText = event.dcCuThe;
    document.getElementById("giaVe").innerText = formatPrice(event.giaMin);
    document.getElementById("moTa").innerHTML = event.moTa;

    let ticketsHTML = "<tr><th align='left'>Loại vé</th><th align='right'>Giá vé</th></tr>";

    event.tickets.forEach(ticket => {
        ticketsHTML += `<tr>
            <td>${ticket.loai}</td>
            <td align="right">${formatPrice(ticket.gia)}</td>
        </tr>`;
    });

    document.getElementById("bangGiaVe").innerHTML = ticketsHTML;
    document.title = "QRticket | " + event.ten;
}

else {
    document.body.innerHTML = "<div align='center'>Sự kiện không tồn tại.</div>";
}