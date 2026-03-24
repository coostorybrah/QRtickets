    export function initSignUp(){
        const form = document.getElementById("signUp-form");
        if (!form) return;

        form.addEventListener("submit", async (e)=>{

            e.preventDefault();

            const username = form.username.value.trim();
            const email = form.email.value.trim();
            const password = form.password.value;
            const confirm = form.password_confirm.value;

            if (password !== confirm){
                alert("Mật khẩu không khớp");
                return;
            }

            const data = await sendAuthRequest("/api/signup/",
            {
                username,
                email,
                password,
            });

            if (data.success){
                alert(data.message);
                location.reload();
            } else{
                alert(data.message || data.error);
            }

        });
    }

    export function initLogin(){
        const form = document.getElementById("login-form");
        if (!form) return;

        form.addEventListener("submit", async (e)=>{

            e.preventDefault();

            const username = form.username.value.trim();
            const password = form.password.value;

            const data = await sendAuthRequest("/api/login/",
            {
                username,
                password
            });

            if (data.success){
                location.reload();
            } else{
                alert(data.message || data.error);
            }
        });
    }

    function getCSRFToken(){
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

