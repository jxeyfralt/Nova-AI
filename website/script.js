let chats = JSON.parse(localStorage.getItem("chats")) || [];
let currentChat = null;

function saveChats() {
    localStorage.setItem("chats", JSON.stringify(chats));
}

function renderChats() {
    const list = document.getElementById("chat-list");
    list.innerHTML = "";

    chats.forEach((chat, index) => {
        const item = document.createElement("div");
        item.className = "chat-item";

        item.innerHTML = `
            <span class="chat-title">${chat.title}</span>
            <button class="delete">✕</button>
        `;

        item.querySelector(".chat-title").onclick = () => {
            openChat(index);
        };

        item.querySelector(".delete").onclick = (e) => {
            e.stopPropagation();
            deleteChat(index);
        };

        list.appendChild(item);
    });
}

function newChat() {
    chats.push({
        title: "New Chat",
        messages: [
            {
                role: "bot",
                text: "Hi, I'm Nova! How can I help you today?"
            }
        ]
    });

    currentChat = chats.length - 1;

    saveChats();
    renderChats();
    displayChat();
}

function openChat(index) {
    currentChat = index;
    renderChats();
    displayChat();
}

function deleteChat(index) {
    chats.splice(index, 1);

    if (currentChat === index) {
        currentChat = null;
    } else if (currentChat > index) {
        currentChat--;
    }

    saveChats();
    renderChats();
    displayChat();
}

function displayChat() {
    const box = document.getElementById("chat-box");
    box.innerHTML = "";

    if (currentChat === null) {
        box.innerHTML = `
            <div class="welcome">
                <h2>Hi, I'm Nova</h2>
                <p>Your personal chatbot assistant</p>
            </div>
        `;
        return;
    }

    chats[currentChat].messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = `message ${msg.role}`;
        div.textContent = msg.text;
        box.appendChild(div);
    });

    box.scrollTop = box.scrollHeight;
}

async function sendMessage() {

    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    if (currentChat === null) {
        chats.push({
            title: message.substring(0, 20),
            messages: []
        });

        currentChat = chats.length - 1;
    }

    chats[currentChat].messages.push({
        role: "user",
        text: message
    });

    if (chats[currentChat].title === "New Chat") {
        chats[currentChat].title = message.substring(0, 20);
    }

    input.value = "";

    saveChats();
    renderChats();
    displayChat();


    const box = document.getElementById("chat-box");


    const typing = document.createElement("div");
    typing.className = "message bot";
    typing.id = "typing";

    typing.innerHTML = `
        <div class="typing">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;

    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;


    try {

        const response = await fetch(
            "https://nova-ai-o27u.onrender.com/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            }
        );


        if (!response.ok) {
            throw new Error("Request failed");
        }


        const reader = response.body.getReader();
        const decoder = new TextDecoder();


        typing.remove();


        const botDiv = document.createElement("div");
        botDiv.className = "message bot";

        box.appendChild(botDiv);


        const botMessage = {
            role: "bot",
            text: ""
        };

        chats[currentChat].messages.push(botMessage);


        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, {
                stream: true
            });

            let i = 0;

            while (i < chunk.length) {
                botMessage.text += chunk.slice(i, i + 8);
                botDiv.textContent = botMessage.text;

                i += 3;

                await new Promise(resolve => setTimeout(resolve, 2));
            }
    


            box.scrollTop = box.scrollHeight;
        }


        saveChats();
        renderChats();


    } catch (error) {

        typing.remove();

        chats[currentChat].messages.push({
            role: "bot",
            text: "Sorry, Nova couldn't connect."
        });

        saveChats();
        renderChats();
        displayChat();

        console.error(error);
    }
}


document
    .getElementById("user-input")
    .addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });


function suggest(text) {
    document.getElementById("user-input").value = text;
}

function toggleSidebar() {

    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".overlay");

    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");

}

renderChats();