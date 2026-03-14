import { formatPrice } from "./modules/formatPrice.js";

export function renderSearchResults(results){

    const container = document.getElementById("search");
    container.innerHTML = "";

    if (Object.keys(results).length === 0){
        container.innerHTML = "<p>Không tìm thấy sự kiện nào.</p>";
        return;
    }

    let cards = "";

    Object.entries(results).forEach(([id, item]) => {
        cards += `
        <div class="card">

            <div class="card__image">
                <a href="/chitietsukien/${id}">
                    <img src="${item.anh}">
                </a>
            </div>

            <div class="card__description">

                <a href="/chitietsukien/${id}" class="card__description__name">
                    ${item.ten}
                </a>

                <span class="card__description__price">
                    Từ ${formatPrice(item.giaMin)}
                </span>

                <span class="card__description__date">
                    Ngày ${item.displayDate} |
                    <span class="card__description__time">
                        ${item.startTime} - ${item.endTime}
                    </span>
                </span>

            </div>

        </div>
        `;
    });

    container.innerHTML = cards;
}

// DOUBLE PRICE SLIDER (cấm đụng)
export function initPriceSlider(){

    const minSlider = document.getElementById("priceMin");
    const maxSlider = document.getElementById("priceMax");

    if (!minSlider || !maxSlider) return;

    const minDisplay = document.getElementById("priceMinValue");
    const maxDisplay = document.getElementById("priceMaxValue");
    const track = document.querySelector(".slider-track");

    const min = Number(minSlider.min);
    const max = Number(minSlider.max);

    function updateDisplay(){
        minDisplay.textContent = formatPrice(Number(minSlider.value));
        maxDisplay.textContent = formatPrice(Number(maxSlider.value));
    }

    function updateTrack(){

        const percentMin = ((Number(minSlider.value) - min) / (max - min)) * 100;
        const percentMax = ((Number(maxSlider.value) - min) / (max - min)) * 100;

        const track_background_color = "#ddd";
        const track_highlight_color = "rgb(61,176,119)";

        track.style.background = `linear-gradient(
            to right,
            ${track_background_color} ${percentMin}%,
            ${track_highlight_color} ${percentMin}%,
            ${track_highlight_color} ${percentMax}%,
            ${track_background_color} ${percentMax}%
        )`;
    }

    minSlider.addEventListener("input", () => {

        if(Number(minSlider.value) > Number(maxSlider.value)){
            minSlider.value = maxSlider.value;
        }

        updateDisplay();
        updateTrack();
    });

    maxSlider.addEventListener("input", () => {

        if(Number(maxSlider.value) < Number(minSlider.value)){
            maxSlider.value = minSlider.value;
        }

        updateDisplay();
        updateTrack();
    });

    updateDisplay();
    updateTrack();
}