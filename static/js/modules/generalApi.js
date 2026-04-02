import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./token.js";

// PUBLIC REQUEST (no JWT)
export async function publicFetch(url, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    const res = await fetch(url, {
        ...options,
        headers,
    });

    return res.json();
}

// PROTECTED REQUEST (JWT)
export async function apiFetch(url, options = {}) {
    let token = getAccessToken();

    const makeRequest = async (tokenToUse) => {
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        };

        if (tokenToUse) {
            headers["Authorization"] = `Bearer ${tokenToUse}`;
        }

        return fetch(url, {
            ...options,
            headers,
        });
    };

    let res = await makeRequest(token);

    // 🔄 TOKEN EXPIRED → TRY REFRESH
    if (res.status === 401) {
        const newToken = await refreshAccessToken();

        if (!newToken) {
            clearTokens();
            throw new Error("Unauthorized");
        }

        // 🔁 retry request
        res = await makeRequest(newToken);
    }

    if (!res.ok) {
        const text = await res.text();
        console.error("API ERROR:", res.status, text);
        throw new Error("Request failed");
    }

    return res.json();
}

// REFRESH TOKEN
let refreshPromise = null;

async function refreshAccessToken() {
    if (refreshPromise) {
        return refreshPromise;
    }

    refreshPromise = (async () => {
        try {
            const refresh = getRefreshToken();
            if (!refresh) return null;

            const res = await fetch("/api/token/refresh/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh }),
            });

            if (!res.ok) return null;

            const data = await res.json();

            setTokens({
                access: data.access,
                refresh,
            });

            return data.access;
        } catch (err) {
            console.error("Refresh failed", err);
            return null;
        } finally {
            refreshPromise = null;
        }
    })();

    return refreshPromise;
}