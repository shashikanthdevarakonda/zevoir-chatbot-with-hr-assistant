console.log("chatbot.js loaded");

async function sendMessage() {

    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    // FIX #1: stop null crash
    if (!input || !chatBox) {
        console.log("Missing chat elements");
        return;
    }

    const message = input.value.trim();
    if (!message) return;

    // show user
    chatBox.innerHTML += `<div><b>You:</b> ${message}</div>`;
    input.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });

        const data = await res.json();

        // bot reply
        chatBox.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (err) {
        chatBox.innerHTML += `<div style="color:red;">Error</div>`;
    }
}