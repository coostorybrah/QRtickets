export function initSignUp(){

    const form = document.getElementById("signUp-form");
    if (!form) return;

    form.addEventListener("submit", async (e)=>{

        e.preventDefault();

        const email = form.email.value.trim();
        const password = form.password.value;
        const confirm = form.password_confirm.value;

        if (password !== confirm){
            alert("Mật khẩu không khớp");
            return;
        }

        const data = await sendAuthRequest("/api/signup/",
        {
            email,
            password,
        });

        if (data.success && data.requires_activation){
            alert(data.message || "Đăng ký thành công. Vui lòng kiểm tra email để kích hoạt tài khoản.");
            form.reset();
            return;
        }

        if (data.success){
            const checkoutRedirect = sessionStorage.getItem("checkoutRedirect");
            if (checkoutRedirect) {
                sessionStorage.removeItem("checkoutRedirect");
                window.location.href = checkoutRedirect;
            } else {
                location.reload();
            }
        } else{
            alert(data.message || "Đăng ký thất bại.");
        }

    });
}

export function initLogin(){

    const form = document.getElementById("login-form");
    if (!form) return;

    form.addEventListener("submit", async (e)=>{

        e.preventDefault();

        const email = form.email.value.trim();
        const password = form.password.value;

        const data = await sendAuthRequest("/api/login/",
        {
            email,
            password
        });

        if (data.success){
            const checkoutRedirect = sessionStorage.getItem("checkoutRedirect");
            if (checkoutRedirect) {
                sessionStorage.removeItem("checkoutRedirect");
                window.location.href = checkoutRedirect;
            } else {
                location.reload();
            }
        } else{
            alert(data.message || "Đăng nhập thất bại.");
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

async function sendAuthRequest(url, payload){

    const result = await fetch(url,{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body:JSON.stringify(payload)
    });

    return await result.json();
}

