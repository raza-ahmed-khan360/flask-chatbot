document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");
    const input = document.getElementById("message");

    // Load history from LocalStorage
    let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];

    // Render loaded history
    chatHistory.forEach(msg => {
        appendMessageToUI(msg.role, msg.content, false); // false = don't scroll yet
    });
    // Scroll to bottom after loading all
    if (chatHistory.length > 0) {
        scrollToBottom();
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendMessageToUI(role, text, shouldScroll = true) {
        const div = document.createElement("div");
        div.className = `message ${role}`; // 'user' or 'bot'
        div.innerHTML = `<div class="content">${text}</div>`;
        chatBox.appendChild(div);
        if (shouldScroll) scrollToBottom();
        return div;
    }

    function saveHistory() {
        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userMessage = input.value.trim();
        if (!userMessage) return;

        input.value = "";

        // 1. Add User Message to UI and History
        appendMessageToUI("user", userMessage);
        chatHistory.push({ role: "user", content: userMessage });
        saveHistory();

        // 2. Add Loading Spinner
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message bot";
        loadingDiv.innerHTML = `<div class="loading-spinner"></div>`;
        chatBox.appendChild(loadingDiv);
        scrollToBottom();

        try {
            // Prepare payload with history
            const payload = new URLSearchParams();
            payload.append("message", userMessage);
            payload.append("history", JSON.stringify(chatHistory));

            const response = await fetch("/chat", {
                method: "POST",
                body: payload,
                headers: { "Content-Type": "application/x-www-form-urlencoded" }
            });

            // Remove loader
            chatBox.removeChild(loadingDiv);

            if (!response.ok) {
                appendMessageToUI("bot", "Error: Could not reach the server.");
                return;
            }

            // 3. Prepare Bot Message Container for Streaming
            // We use the same helper but we need reference to the content div to append chunks
            // So we manually create it or return it from helper? Helper returns div.
            // But helper fills innerHTML. We want to start empty or incrementally add.
            // Let's manually create the bot div for streaming to have full control.

            const botDiv = document.createElement("div");
            botDiv.className = "message bot";
            const botContent = document.createElement("div");
            botContent.className = "content";
            botDiv.appendChild(botContent);
            chatBox.appendChild(botDiv);
            scrollToBottom();

            let botResponseText = "";
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                botResponseText += chunk;
                botContent.textContent += chunk;
                scrollToBottom();
            }

            // 4. Save Bot Response to History
            chatHistory.push({ role: "bot", content: botResponseText });
            saveHistory();

        } catch (err) {
            if (loadingDiv.parentNode) chatBox.removeChild(loadingDiv);
            appendMessageToUI("bot", `Error: ${err.message}`);
        }
    });

    // Optional: Focus input on load
    input.focus();

    // Expose clear function globally for the button (we will add logic for button later)
    window.clearChat = () => {
        if (confirm("Are you sure you want to clear the chat history?")) {
            localStorage.removeItem("chatHistory");
            chatHistory = [];
            chatBox.innerHTML = "";
        }
    };
});
