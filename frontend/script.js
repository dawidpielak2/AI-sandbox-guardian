const API_URL = "http://localhost:8000/api";
let currentChatId = null;

const chatList = document.getElementById("chatList");
const messagesArea = document.getElementById("messagesArea");
const newChatBtn = document.getElementById("newChatBtn");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");

async function fetchChats() {
    try {
        const res = await fetch(`${API_URL}/chats`);
        const chats = await res.json();
        chatList.innerHTML = "";

        chats.forEach(chat => {
            const div = document.createElement("div");
            div.className = "chat-item";
            if (chat.id === currentChatId) div.classList.add("active");

            const titleSpan = document.createElement("span");
            titleSpan.className = "chat-title";
            titleSpan.innerText = chat.title || `Chat #${chat.id}`;
            titleSpan.onclick = () => selectChat(chat.id, div);

            const actionsDiv = document.createElement("div");
            actionsDiv.className = "chat-actions";

            const renameBtn = document.createElement("button");
            renameBtn.innerText = "✏️";
            renameBtn.onclick = (e) => {
                e.stopPropagation();
                renameChat(chat.id, chat.title);
            };

            const deleteBtn = document.createElement("button");
            deleteBtn.innerText = "🗑️";
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteChat(chat.id);
            };

            actionsDiv.appendChild(renameBtn);
            actionsDiv.appendChild(deleteBtn);

            div.appendChild(titleSpan);
            div.appendChild(actionsDiv);

            chatList.appendChild(div);
        });
    } catch (err) {
        console.error(err);
    }
}

async function renameChat(id, currentTitle) {
    const newTitle = prompt("Enter new chat name:", currentTitle);
    if (!newTitle || newTitle.trim() === "" || newTitle === currentTitle) return;

    try {
        await fetch(`${API_URL}/chats/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: newTitle.trim() })
        });
        fetchChats();
    } catch (err) {
        console.error(err);
    }
}

async function deleteChat(id) {
    if (!confirm("Are you sure you want to delete this chat?")) return;

    try {
        await fetch(`${API_URL}/chats/${id}`, {
            method: "DELETE"
        });

        if (currentChatId === id) {
            currentChatId = null;
            messagesArea.innerHTML = "<div class='placeholder-text'>Select or create a chat to begin.</div>";
            messageInput.disabled = true;
            sendBtn.disabled = true;
            fileInput.disabled = true;
            uploadBtn.disabled = true;
        }

        fetchChats();
    } catch (err) {
        console.error(err);
    }
}

async function selectChat(id, element) {
    currentChatId = id;

    document.querySelectorAll(".chat-item").forEach(el => el.classList.remove("active"));
    if (element) element.classList.add("active");

    messageInput.disabled = false;
    sendBtn.disabled = false;
    fileInput.disabled = false;
    uploadBtn.disabled = false;

    messagesArea.innerHTML = "";

    try {
        const res = await fetch(`${API_URL}/chats/${id}/messages`);
        const messages = await res.json();

        if (messages.length === 0) {
            messagesArea.innerHTML = "<div class='placeholder-text'>No messages yet. Start the conversation!</div>";
        } else {
            messages.forEach(msg => {
                addMessageToScreen(msg.content, msg.role);
            });
        }
    } catch (err) {
        messagesArea.innerHTML = "<div class='system msg'>Error loading history.</div>";
    }
}

newChatBtn.onclick = async () => {
    const res = await fetch(`${API_URL}/chats`, { method: "POST" });
    const chat = await res.json();
    await fetchChats();
    const firstChat = chatList.firstChild;
    selectChat(chat.id, firstChat);
};

sendBtn.onclick = async () => {
    const text = messageInput.value.trim();
    if (!text || !currentChatId) return;

    addMessageToScreen(text, "user");
    messageInput.value = "";

    try {
        const res = await fetch(`${API_URL}/chats/${currentChatId}/messages`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: text })
        });
        const data = await res.json();
        addMessageToScreen(data.content, "assistant");
    } catch (err) {
        addMessageToScreen("Connection error.", "system");
    }
};

uploadBtn.onclick = async () => {
    const file = fileInput.files[0];
    if (!file || !currentChatId) return;

    const formData = new FormData();
    formData.append("file", file);

    addMessageToScreen(`Uploading file: ${file.name}...`, "system");

    try {
        const res = await fetch(`${API_URL}/chats/${currentChatId}/upload`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        addMessageToScreen(data.status, "system");
        fileInput.value = "";
    } catch (err) {
        addMessageToScreen("File upload error.", "system");
    }
};

function addMessageToScreen(text, role) {
    const div = document.createElement("div");
    div.className = `msg ${role}`;
    div.innerText = text;
    messagesArea.appendChild(div);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendBtn.click();
});

fetchChats();