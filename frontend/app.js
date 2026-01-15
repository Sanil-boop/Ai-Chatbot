/* ================= CONFIG ================= */

// CHANGE THIS AFTER DEPLOY
const API_URL = "http://127.0.0.1:8000";

/* ================= DRAWER ================= */

function toggleDrawer() {
  const drawer = document.getElementById("drawer");
  drawer.style.right = drawer.style.right === "0px" ? "-260px" : "0px";
}

/* ================= AUTH HELPERS ================= */

function isLoggedIn() {
  return !!localStorage.getItem("token");
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

/* ================= NAVBAR STATE ================= */

function updateNavbar() {
  const loginLink = document.getElementById("nav-login");
  const signupLink = document.getElementById("nav-signup");
  const logoutLink = document.getElementById("nav-logout");

  if (!loginLink || !signupLink || !logoutLink) return;

  if (isLoggedIn()) {
    loginLink.style.display = "none";
    signupLink.style.display = "none";
    logoutLink.style.display = "inline-block";
  } else {
    loginLink.style.display = "inline-block";
    signupLink.style.display = "inline-block";
    logoutLink.style.display = "none";
  }
}

/* ================= CHAT ================= */

async function sendMessage() {
  const input = document.getElementById("msg");
  const message = input.value.trim();
  if (!message) return;

  // OPTIONAL: protect chat
  if (!isLoggedIn()) {
    alert("Please login to chat");
    window.location.href = "login.html";
    return;
  }

  const chat = document.getElementById("chat");

  // User message
  chat.innerHTML += `<div class="user">You: ${message}</div>`;
  input.value = "";
  chat.scrollTop = chat.scrollHeight;

  // Typing indicator
  const typingId = `typing-${Date.now()}`;
  chat.innerHTML += `<div class="bot" id="${typingId}">AI is typing...</div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token") || ""}`
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    document.getElementById(typingId).innerHTML =
      `AI: ${data.reply || "No response"}`;
  } catch (error) {
    document.getElementById(typingId).innerHTML =
      "❌ Unable to connect to server";
  }

  chat.scrollTop = chat.scrollHeight;
}

/* ================= ENTER KEY ================= */

document.addEventListener("DOMContentLoaded", () => {
  updateNavbar();

  const input = document.getElementById("msg");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }
});
