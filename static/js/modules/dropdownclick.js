document.addEventListener("DOMContentLoaded", () => {
    const trigger = document.querySelector(".dropdown-trigger-click");
    const dropdown = document.getElementById(trigger.dataset.dropdown);
    
    if (trigger && dropdown) {
    
        trigger.addEventListener("click", (e) => {
    
            e.stopPropagation();
    
            dropdown.classList.toggle("open");
            trigger.classList.toggle("active");
    
        });
    
        document.addEventListener("click", (e) => {
    
            if (!e.target.closest(".dropdown") && !e.target.closest(".dropdown-trigger-click")) {
                dropdown.classList.remove("open");
                trigger.classList.remove("active");
            }
    
        });
    }
})