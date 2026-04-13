import { protectedFetch } from "./modules/generalApi.js";
import { requireAuth } from "./modules/authGuard.js";

document.addEventListener("DOMContentLoaded", async () => {
    const allowed = await requireAuth();
    
    if (!allowed) {
        document.querySelector(".checkout").style.display = "none";
        throw new Error("Not authenticated");
    }
});

// AVATAR UPLOAD
export function initAvatarUpload() {
    const avatarImg = document.getElementById("avatar");
    const fileInput = document.getElementById("avatarInput");

    if (!avatarImg || !fileInput) return;

    const wrapper = avatarImg.parentElement;
    let isUploading = false;

    // click avatar → open file picker
    wrapper.addEventListener("click", () => {
        if (!isUploading) fileInput.click();
    });

    // handle file selection
    fileInput.addEventListener("change", async () => {
        const file = fileInput.files[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            alert("Chỉ được chọn file ảnh");
            fileInput.value = "";
            return;
        }

        if (file.size > 2 * 1024 * 1024) {
            alert("Ảnh tối đa 2MB");
            fileInput.value = "";
            return;
        }

        if (isUploading) return;
        isUploading = true;

        const formData = new FormData();
        formData.append("avatar", file);

        wrapper.classList.add("uploading");

        try {
            const data = await protectedFetch("/api/user/avatar/", {
                method: "POST",
                body: formData,
            });

            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "Upload thất bại");
            }

        } catch (err) {
            console.error(err);
            alert("Lỗi kết nối server");
        }

        wrapper.classList.remove("uploading");
        fileInput.value = "";
        isUploading = false;
    });
}


// USERNAME UPDATE
export function initUsernameUpdate() {
    const form = document.getElementById("userInfoForm");
    if (!form) return;

    const btn = form.querySelector("button");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = form.username.value.trim();

        if (!username) {
            return alert("Username không được để trống");
        }

        btn.disabled = true;

        try {
            const data = await protectedFetch("/api/user/username/", {
                method: "PATCH",
                body: JSON.stringify({ username })
            });

            if (data.success) {
                alert("Cập nhật thành công");
            } else {
                alert(data.error);
            }

        } catch (err) {
            console.error(err);
            alert("Lỗi server");
        }

        btn.disabled = false;
    });
}

// SHOW USER INFO
export async function initUserInfo() {
    try {
        const data = await protectedFetch("/api/auth/me/");

        if (!data.loggedIn) return;

        document.getElementById("usernameInput").value = data.username || "";
        document.getElementById("emailInput").value = data.email || "";

        const avatar = document.getElementById("avatar");
        if (avatar && data.avatar) {
            avatar.src = data.avatar || "/static/images/avatars/default-avatar.png";
        }

    } catch (err) {
        console.error("Failed to load user info", err);
    }
}

// PASSWORD CHANGE
export function initPasswordChange() {
    const form = document.getElementById("passwordForm");
    if (!form) return;

    const btn = form.querySelector("button");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const current = form.current_password.value;
        const newPass = form.new_password.value;
        const confirm = form.confirm_password.value;

        if (newPass !== confirm) {
            return alert("Mật khẩu xác nhận không khớp");
        }

        if (newPass.length < 6) {
            return alert("Mật khẩu phải >= 6 ký tự");
        }

        btn.disabled = true;

        try {
            const data = await protectedFetch("/api/user/password/", {
                method: "POST",
                body: JSON.stringify({
                    current_password: current,
                    new_password: newPass,
                    confirm_password: confirm
                })
            });

            if (data.success) {
                alert("Đổi mật khẩu thành công");
                form.reset();
            } else {
                alert(data.error);
            }

        } catch (err) {
            console.error(err);
            alert("Lỗi server");
        }

        btn.disabled = false;
    });
}