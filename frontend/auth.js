/* ================= CONFIG ================= */

// CHANGE AFTER DEPLOY
const API_URL = "http://127.0.0.1:8000";

/* ================= SIGN UP ================= */

async function signup() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const msg = document.getElementById("msg");

  if (!email || !password) {
    msg.style.color = "red";
    msg.innerText = "❌ Please fill all fields";
    return;
  }

  msg.style.color = "#38bdf8";
  msg.innerText = "Creating account...";

  try {
    const res = await fetch(`${API_URL}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.message) {
      msg.style.color = "lightgreen";
      msg.innerText = "✅ Account created! Redirecting to login...";
      setTimeout(() => {
        window.location.href = "login.html";
      }, 1200);
    } else {
      msg.style.color = "red";
      msg.innerText = data.error || "❌ Signup failed";
    }
  } catch (err) {
    msg.style.color = "red";
    msg.innerText = "❌ Server not reachable";
  }
}

/* ================= LOGIN ================= */

async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const msg = document.getElementById("msg");

  if (!email || !password) {
    msg.style.color = "red";
    msg.innerText = "❌ Please fill all fields";
    return;
  }

  msg.style.color = "#38bdf8";
  msg.innerText = "Logging in...";

  try {
    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.token) {
      localStorage.setItem("token", data.token);
      msg.style.color = "lightgreen";
      msg.innerText = "✅ Login successful!";
      setTimeout(() => {
        window.location.href = "index.html";
      }, 1000);
    } else {
      msg.style.color = "red";
      msg.innerText = data.error || "❌ Invalid credentials";
    }
  } catch (err) {
    msg.style.color = "red";
    msg.innerText = "❌ Server not reachable";
  }
}

/* ================= LOGOUT ================= */

function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}
