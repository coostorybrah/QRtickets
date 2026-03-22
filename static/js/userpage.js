// AVATAR UPLOAD
export function initAvatarUpload() {
    const form = document.getElementById("avatarForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fileInput = form.querySelector("input[name='avatar']");
        const file = fileInput.files[0];

        if (!file) {
            alert("Chọn ảnh trước");
            return;
        }

        const formData = new FormData();
        formData.append("avatar", file);

        const res = await fetch("/api/upload-avatar/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        });

        const data = await res.json();

        if (data.success) {
            document.getElementById("avatar").src = data.avatar + "?t=" + new Date().getTime();
            location.reload();
        } else {
            alert(data.error);
        }
    });
}



function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}