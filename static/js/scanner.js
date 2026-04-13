import { protectedFetch } from "./modules/generalApi.js";
import { requireAuth } from "./modules/authGuard.js";

let scanning = true;

document.addEventListener("DOMContentLoaded", async () => {
    const allowed = await requireAuth();
    if (!allowed) return;

    // 🔒 get real user from backend
    const user = await protectedFetch("/api/auth/me/");

    if (!user.is_organizer) {
        window.location.href = "/";
        return;
    }

    startScanner();
});

function startScanner() {
    const resultEl = document.getElementById("result");

    const scanner = new Html5Qrcode("video");

    const boxSize = 250;

    scanner.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: { width: boxSize, height: boxSize }
        },
        async (decodedText) => {
            if (!scanning) return;

            scanning = false;

            const ticketId = decodedText.split(":")[1];

            if (!ticketId) {
                setResult(resultEl, "QR không hợp lệ", "error");
                return resetScanner(resultEl);
            }

            try {
                const data = await protectedFetch("/api/orders/check-in/", {
                    method: "POST",
                    body: JSON.stringify({ ticket_id: ticketId })
                });

                if (data.status === "success") {
                    setResult(resultEl, "Vé hợp lệ", "success");
                } else if (data.error) {
                    setResult(resultEl, data.error, "error");
                } else {
                    setResult(resultEl, "Vé không hợp lệ", "error");
                }

            }
            catch (err) {
                console.error(err);
                const message = err?.error || err?.message || "Lỗi kiểm tra vé";
                setResult(resultEl, message, "error");
            }

            setTimeout(() => {
                resetScanner(resultEl);
            }, 2500);
        },
    );
}

function setResult(el, text, type) {
    el.innerText = text;
    el.className = type;
}

function resetScanner(resultEl) {
    resultEl.innerText = "";
    resultEl.className = "";
    scanning = true;
}