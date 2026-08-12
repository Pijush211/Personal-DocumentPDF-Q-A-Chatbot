//const BACKEND_URL = "http://127.0.0.1:8000";
const BACKEND_URL = "https://pdf-qa-rag-backend.onrender.com";

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const apiKeyInput = document.getElementById("apiKey");
const modelSelect = document.getElementById("modelSelect");
const uploadStatus = document.getElementById("uploadStatus");
const docBanner = document.getElementById("docBanner");

const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatMessages = document.getElementById("chatMessages");

// Upload Document Handler
uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
        setStatus("Please select a file to upload.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadBtn.disabled = true;
    setStatus("Uploading & indexing document...", "");

    try {
        const response = await fetch(`${BACKEND_URL}/api/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            setStatus(`✅ Indexed: ${data.filename} (${data.total_chunks} chunks)`, "success");
            docBanner.textContent = `📄 Active Document: ${data.filename}`;
            docBanner.classList.remove("hidden");
            userInput.disabled = false;
            sendBtn.disabled = false;
        } else {
            setStatus(`Error: ${data.detail}`, "error");
        }
    } catch (err) {
        setStatus(`Server error: ${err.message}. Make sure backend is running on ${BACKEND_URL}`, "error");
    } finally {
        uploadBtn.disabled = false;
    }
});

function setStatus(msg, type) {
    uploadStatus.textContent = msg;
    uploadStatus.className = `status-msg ${type}`;
}

// Send Question Handler
async function handleSend() {
    const question = userInput.value.trim();
    if (!question) return;

    const apiKey = apiKeyInput.value.trim();
    const model = modelSelect.value;

    appendMessage(question, "user");
    userInput.value = "";

    const loadingMsg = appendMessage("Thinking...", "assistant");

    try {
        const response = await fetch(`${BACKEND_URL}/api/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                groq_api_key: apiKey,
                model_name: model
            })
        });

        const data = await response.json();

        if (response.ok) {
            loadingMsg.innerHTML = formatAnswer(data.answer, data.sources);
        } else {
            loadingMsg.innerHTML = `<span style="color: #f44336;">Error: ${data.detail}</span>`;
        }
    } catch (err) {
        loadingMsg.innerHTML = `<span style="color: #f44336;">Failed to connect to backend: ${err.message}</span>`;
    }
}

sendBtn.addEventListener("click", handleSend);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSend();
});

function appendMessage(text, role) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}-msg`;
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
}

function formatAnswer(answer, sources) {
    let html = `<div>${answer}</div>`;
    if (sources && sources.length > 0) {
        html += `<div class="sources-box">
            <details>
                <summary>🔍 View ${sources.length} Source Chunks</summary>
                <ul>`;
        sources.forEach((s, idx) => {
            html += `<li style="margin-top: 6px;"><strong>Chunk ${idx + 1}</strong> (Page ${s.page}): <br><em>"${s.content}"</em></li>`;
        });
        html += `</ul></details></div>`;
    }
    return html;
}
