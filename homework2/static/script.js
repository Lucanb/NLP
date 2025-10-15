const chatWindow = document.getElementById("chat-window");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const saveBtn = document.getElementById("save-btn");
const historyBtn = document.getElementById("history-btn");
const historyList = document.getElementById("history-list");

function addMessage(sender, text) {
    chatWindow.innerHTML += `<div><b>${sender}:</b> ${text}</div>`;
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

sendBtn.onclick = () => {
    const msg = input.value.trim();
    if(!msg) return;
    addMessage("You", msg);
    input.value = "";
    fetch("/send", {
        method: "POST",
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: msg})
    })
    .then(res => res.json())
    .then(data => addMessage("GPT", data.response));
};

saveBtn.onclick = () => {
    fetch("/save", {method: "POST"})
    .then(res => res.json())
    .then(data => alert("Conversation saved to " + data.filename));
};

historyBtn.onclick = () => {
    fetch("/history")
    .then(res => res.json())
    .then(data => {
        historyList.innerHTML = "";
        data.files.forEach(file => {
            const btn = document.createElement("button");
            btn.textContent = file;
            btn.onclick = () => {
                fetch("/load/" + file)
                .then(res => res.json())
                .then(d => alert(d.content));
            };
            historyList.appendChild(btn);
        });
    });
};
