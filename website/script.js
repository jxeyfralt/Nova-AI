let chats = JSON.parse(localStorage.getItem("chats")) || [];

let currentChat = null;


// Save chats
function saveChats() {
    localStorage.setItem("chats", JSON.stringify(chats));
}


// Create sidebar list
function renderChats() {

    const list = document.getElementById("chat-list");

    list.innerHTML = "";


    chats.forEach((chat, index) => {

        const item = document.createElement("div");

        item.className = "chat-item";


        if (index === currentChat) {
            item.classList.add("active");
        }


        item.innerHTML = `

            <span class="chat-title">
                ${chat.title}
            </span>

            <button class="delete">
                ✕
            </button>

        `;


        // Click chat
        item.querySelector(".chat-title").onclick = () => {

            openChat(index);

        };


        // Delete chat
        item.querySelector(".delete").onclick = (event) => {

            event.stopPropagation();

            deleteChat(index);

        };


        list.appendChild(item);

    });

}



// New chat
function newChat() {


    const chat = {

        title: "New Chat",

        messages: [

            {
                role: "bot",
                text: "Hi, I'm Nova, your personal chatbot! How can I help you today?"
            }

        ]

    };


    chats.push(chat);


    currentChat = chats.length - 1;


    saveChats();

    renderChats();

    displayChat();

}



// Open old chat
function openChat(index) {


    currentChat = index;


    saveChats();

    renderChats();

    displayChat();

}



// Delete chat
function deleteChat(index) {


    chats.splice(index, 1);


    if (currentChat === index) {

        currentChat = null;

    }


    saveChats();

    renderChats();

    displayChat();

}




// Show messages
function displayChat() {


    const box = document.getElementById("chat-box");


    box.innerHTML = "";


    if (currentChat === null) {

        box.innerHTML = `

        <div class="welcome">

            <h1></h1>

            <h2>Hi, I'm Nova</h2>

            <p>Your personal chatbot assistant</p>

        </div>

        `;

        return;

    }



    chats[currentChat].messages.forEach(msg => {


        box.innerHTML += `

        <div class="message ${msg.role}">

            ${msg.text}

        </div>

        `;


    });


    box.scrollTop = box.scrollHeight;

}





// Send message
async function sendMessage() {


    const input = document.getElementById("user-input");


    const message = input.value.trim();



    if (message === "") return;



    // Make chat if none exists
    if (currentChat === null) {


        chats.push({

            title: message.substring(0,20),

            messages: []

        });


        currentChat = chats.length - 1;

    }




    chats[currentChat].messages.push({

        role:"user",

        text:message

    });



    if (chats[currentChat].title === "New Chat") {

        chats[currentChat].title = message.substring(0,20);

    }



    input.value = "";


    saveChats();

    renderChats();

    displayChat();





    // Typing dots
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

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    message:message

                })

            }

        );



        const data = await response.json();



        typing.remove();



        chats[currentChat].messages.push({

            role:"bot",

            text:data.reply

        });



        saveChats();

        renderChats();

        displayChat();



    }


    catch(error){


        typing.remove();


        chats[currentChat].messages.push({

            role:"bot",

            text:"Sorry, Nova couldn't connect."

        });


        saveChats();

        displayChat();


    }

}




// Enter key
document
.getElementById("user-input")
.addEventListener("keydown", function(event){


    if(event.key === "Enter"){

        sendMessage();

    }


});



// Load sidebar
renderChats();
function suggest(text){

    document.getElementById("user-input").value = text;

}