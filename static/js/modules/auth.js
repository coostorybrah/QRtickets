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

        const data = await sendAuthRequest("/api/signup",
        {
            username,
            email,
            password,
            password_confirm: confirm
        });

        if (data.success){
            alert(data.message);
            location.reload();
        } else{
            alert(data.message);
        }

    });
}

export function initLogin(){

    checkLogin();

    const form = document.getElementById("login-form");
    if (!form) return;

    form.addEventListener("submit", async (e)=>{

        e.preventDefault();

        const username = form.username.value.trim();
        const password = form.password.value;

        const data = await sendAuthRequest("/api/login",
        {
            username,
            password
        });

        if (data.success){
            location.reload();
        } else{
            alert(data.message);
        }
    });
}

async function sendAuthRequest(url, payload){

    const result = await fetch(url,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    });

    return await result.json();
}

export function showUserUI(avatarPath){

    const guest = document.getElementById("guestUI");
    const userMenu = document.getElementById("userMenu");

    if (guest){
        guest.style.display = "none";
    } 
        
    if (userMenu){
        userMenu.classList.add("active");
    } 

    const avatar = document.getElementById("avatar");
    if (avatar) {
        avatar.src = avatarPath;
    }
}

async function checkLogin(){
    const res = await fetch("/api/me");
    const data = await res.json();

    if (data.loggedIn){
        showUserUI(data.avatar);
    }
}

