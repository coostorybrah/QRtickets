// OPEN MODAL
document.querySelectorAll("[data-open]").forEach(btn => {
    btn.addEventListener("click", () => {

        const target = btn.dataset.open;

        document.querySelectorAll(".modal").forEach(m => {
            m.classList.remove("active");
        });

        document.getElementById(target).classList.add("active");

    });
});

// CLOSE MODAL
document.querySelectorAll("[data-close]").forEach(btn => {
    btn.addEventListener("click", () => {

        const target = btn.dataset.close;

        document.getElementById(target).classList.remove("active");
    });
});