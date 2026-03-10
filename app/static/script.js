const promptInput = document.getElementById("promptInput");
const imageInput = document.getElementById("imageInput");
const selectedFileText = document.getElementById("selectedFileText");
const generateBtn = document.getElementById("generateBtn");
const clearBtn = document.getElementById("clearBtn");
const resultContainer = document.getElementById("resultContainer");
const historyContainer = document.getElementById("historyContainer");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
const statusMessage = document.getElementById("statusMessage");
const loadingSpinner = document.getElementById("loadingSpinner");
const historyModal = document.getElementById("historyModal");
const modalBackdrop = document.getElementById("modalBackdrop");
const closeModalBtn = document.getElementById("closeModalBtn");
const modalContent = document.getElementById("modalContent");
const startVoiceBtn = document.getElementById("startVoiceBtn");
const stopVoiceBtn = document.getElementById("stopVoiceBtn");
const voiceStatus = document.getElementById("voiceStatus");
const quickPromptButtons = document.querySelectorAll(".quick-prompt");

const startLiveBtn = document.getElementById("startLiveBtn");
const stopLiveBtn = document.getElementById("stopLiveBtn");
const sendLiveBtn = document.getElementById("sendLiveBtn");
const useLiveBriefBtn = document.getElementById("useLiveBriefBtn");
const startLiveMicBtn = document.getElementById("startLiveMicBtn");
const stopLiveMicBtn = document.getElementById("stopLiveMicBtn");
const liveInput = document.getElementById("liveInput");
const liveMessages = document.getElementById("liveMessages");
const liveStatus = document.getElementById("liveStatus");
const liveSessionBadge = document.getElementById("liveSessionBadge");
const liveMicBadge = document.getElementById("liveMicBadge");

let recognition = null;
let isListening = false;
let voiceBaseText = "";

let liveRecognition = null;
let isLiveListening = false;
let liveBaseText = "";

let liveSocket = null;
let liveClientId = `client_${crypto.randomUUID()}`;
let latestLiveBrief = null;

const API = {
  generate: "/api/generate-content-pack",
  history: "/api/history",
  historyItem: (documentId) => `/api/history/${encodeURIComponent(documentId)}`,
  exportJson: (documentId) => `/api/history/${encodeURIComponent(documentId)}/export/json`,
  exportTxt: (documentId) => `/api/history/${encodeURIComponent(documentId)}/export/txt`,
  exportPdf: (documentId) => `/api/history/${encodeURIComponent(documentId)}/export/pdf`,
  liveWs: () => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${window.location.host}/ws/live/${liveClientId}`;
  }
};

function setStatus(message, isError = false) {
  if (!statusMessage) return;
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
  statusMessage.classList.toggle("notice", !isError);
}

function setLiveStatus(message, isError = false) {
  if (!liveStatus) return;
  liveStatus.textContent = message;
  liveStatus.classList.toggle("error", isError);
  liveStatus.classList.toggle("notice", !isError);
}

function setBadgeState(element, label, isActive) {
  if (!element) return;
  element.textContent = label;
  element.classList.toggle("live-badge-active", isActive);
}

function setButtonActive(button, active) {
  if (!button) return;
  button.classList.toggle("is-active", active);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

function escapeForJs(text) {
  return String(text ?? "")
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "");
}

function shortenText(text, maxLength = 120) {
  if (!text || text.length <= maxLength) return text || "";
  return `${text.slice(0, maxLength)}...`;
}

function toggleLoading(isLoading) {
  if (loadingSpinner) loadingSpinner.classList.toggle("hidden", !isLoading);
  if (generateBtn) generateBtn.disabled = isLoading;
  if (clearBtn) clearBtn.disabled = isLoading;
  if (promptInput) promptInput.disabled = isLoading;
  if (imageInput) imageInput.disabled = isLoading;
  if (refreshHistoryBtn) refreshHistoryBtn.disabled = isLoading;
}

function closeModal() {
  if (historyModal) historyModal.classList.add("hidden");
}

function appendLiveMessage(role, text) {
  if (!liveMessages) return;

  const div = document.createElement("div");
  div.className = "result-card";
  div.innerHTML = `
    <h4>${escapeHtml(role)}</h4>
    <p>${escapeHtml(text)}</p>
  `;

  liveMessages.appendChild(div);
  liveMessages.scrollTop = liveMessages.scrollHeight;
}

function clearLiveMessages() {
  if (!liveMessages) return;
  liveMessages.innerHTML = "";
}

function downloadFileByUrl(url, filenameBase = "download") {
  if (!url) {
    setStatus("No file URL available.", true);
    return;
  }

  const a = document.createElement("a");
  a.href = url;
  a.download = filenameBase;
  a.target = "_blank";
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function downloadHistoryJson(documentId) {
  const a = document.createElement("a");
  a.href = API.exportJson(documentId);
  a.download = `nexus_export_${documentId}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function downloadHistoryTxt(documentId) {
  const a = document.createElement("a");
  a.href = API.exportTxt(documentId);
  a.download = `nexus_export_${documentId}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function downloadHistoryPdf(documentId) {
  const a = document.createElement("a");
  a.href = API.exportPdf(documentId);
  a.download = `nexus_export_${documentId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

// ---------------- Main prompt speech-to-text ----------------

function resetVoiceUI() {
  isListening = false;
  voiceBaseText = "";

  if (promptInput) promptInput.classList.remove("listening");

  if (voiceStatus) {
    voiceStatus.textContent = "Voice input ready.";
    voiceStatus.classList.remove("voice-live");
  }

  setButtonActive(startVoiceBtn, false);
  setButtonActive(stopVoiceBtn, false);

  if (startVoiceBtn) startVoiceBtn.disabled = !recognition;
  if (stopVoiceBtn) stopVoiceBtn.disabled = true;
}

function setupVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    recognition = null;

    if (voiceStatus) {
      voiceStatus.textContent = "Voice input is best supported in Chrome.";
    }

    if (startVoiceBtn) startVoiceBtn.disabled = true;
    if (stopVoiceBtn) stopVoiceBtn.disabled = true;
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = true;
  recognition.continuous = true;
  recognition.maxAlternatives = 1;

  if (startVoiceBtn) startVoiceBtn.disabled = false;
  if (stopVoiceBtn) stopVoiceBtn.disabled = true;

  recognition.onstart = () => {
    isListening = true;
    voiceBaseText = promptInput ? promptInput.value.trim() : "";

    if (promptInput) promptInput.classList.add("listening");

    if (voiceStatus) {
      voiceStatus.textContent = "Listening... speak now.";
      voiceStatus.classList.add("voice-live");
    }

    setButtonActive(startVoiceBtn, true);
    setButtonActive(stopVoiceBtn, false);

    if (startVoiceBtn) startVoiceBtn.disabled = true;
    if (stopVoiceBtn) stopVoiceBtn.disabled = false;

    setStatus("Voice input active.");
  };

  recognition.onresult = (event) => {
    let finalTranscript = "";
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += `${transcript} `;
      } else {
        interimTranscript += transcript;
      }
    }

    const base = voiceBaseText ? `${voiceBaseText} ` : "";
    if (promptInput) {
      promptInput.value = `${base}${finalTranscript}${interimTranscript}`.trim();
    }
  };

  recognition.onerror = () => {
    if (voiceStatus) {
      voiceStatus.textContent = "Voice recognition network issue. Chrome works best.";
      voiceStatus.classList.remove("voice-live");
    }
    setStatus("Voice recognition issue in this browser.", true);
  };

  recognition.onend = () => {
    resetVoiceUI();
  };
}

function startVoiceInput() {
  if (!recognition) {
    setStatus("Voice input is not supported in this browser.", true);
    return;
  }
  if (isListening) return;

  try {
    recognition.start();
  } catch (error) {
    setStatus(`Could not start voice input: ${error.message}`, true);
  }
}

function stopVoiceInput() {
  if (!recognition || !isListening) return;

  try {
    recognition.stop();
    setStatus("Stopped listening. Review and generate.");
    setButtonActive(stopVoiceBtn, true);
  } catch (error) {
    setStatus(`Could not stop voice input: ${error.message}`, true);
  }
}

// ---------------- Live input speech-to-text ----------------

function setupLiveVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    if (startLiveMicBtn) startLiveMicBtn.disabled = true;
    if (stopLiveMicBtn) stopLiveMicBtn.disabled = true;
    return;
  }

  liveRecognition = new SpeechRecognition();
  liveRecognition.lang = "en-US";
  liveRecognition.interimResults = true;
  liveRecognition.continuous = true;
  liveRecognition.maxAlternatives = 1;

  if (stopLiveMicBtn) stopLiveMicBtn.disabled = true;

  liveRecognition.onstart = () => {
    isLiveListening = true;
    liveBaseText = liveInput ? liveInput.value.trim() : "";

    setLiveStatus("Listening for live message...");
    setBadgeState(liveMicBadge, "Mic: Recording", true);

    setButtonActive(startLiveMicBtn, true);
    setButtonActive(stopLiveMicBtn, false);

    if (startLiveMicBtn) startLiveMicBtn.disabled = true;
    if (stopLiveMicBtn) stopLiveMicBtn.disabled = false;
  };

  liveRecognition.onresult = (event) => {
    let finalTranscript = "";
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += `${transcript} `;
      } else {
        interimTranscript += transcript;
      }
    }

    const base = liveBaseText ? `${liveBaseText} ` : "";
    if (liveInput) {
      liveInput.value = `${base}${finalTranscript}${interimTranscript}`.trim();
    }
  };

  liveRecognition.onerror = () => {
    setLiveStatus("Live voice recognition issue. Chrome works best.", true);
    setBadgeState(liveMicBadge, "Mic: Error", false);
  };

  liveRecognition.onend = () => {
    isLiveListening = false;
    setBadgeState(liveMicBadge, "Mic: Off", false);

    setButtonActive(startLiveMicBtn, false);
    setButtonActive(stopLiveMicBtn, false);

    if (startLiveMicBtn) startLiveMicBtn.disabled = false;
    if (stopLiveMicBtn) stopLiveMicBtn.disabled = true;
  };
}

function startLiveMic() {
  if (!liveSocket || liveSocket.readyState !== WebSocket.OPEN) {
    setLiveStatus("Start a live session first.", true);
    return;
  }

  if (!liveRecognition) {
    setLiveStatus("Live speech input is not supported in this browser.", true);
    return;
  }

  if (isLiveListening) return;

  try {
    liveRecognition.start();
  } catch (error) {
    setLiveStatus(`Could not start live speaking: ${error.message}`, true);
  }
}

function stopLiveMic() {
  if (!liveRecognition || !isLiveListening) return;

  try {
    liveRecognition.stop();
    setLiveStatus("Stopped listening. Review the message and click Send.");
    setButtonActive(stopLiveMicBtn, true);
  } catch (error) {
    setLiveStatus(`Could not stop live speaking: ${error.message}`, true);
  }
}

// ---------------- Live text session ----------------

function startLiveSession() {
  if (liveSocket && liveSocket.readyState === WebSocket.OPEN) {
    setLiveStatus("Live session already active.");
    return;
  }

  latestLiveBrief = null;
  clearLiveMessages();

  liveSocket = new WebSocket(API.liveWs());

  liveSocket.onopen = () => {
    setLiveStatus("Live text session connected.");
    appendLiveMessage("System", "Live text session connected.");
    setBadgeState(liveSessionBadge, "Session: Connected", true);

    setButtonActive(startLiveBtn, true);
    setButtonActive(stopLiveBtn, false);
  };

  liveSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "system") {
      appendLiveMessage("System", data.message);
    }

    if (data.type === "assistant_text") {
      appendLiveMessage("NEXUS AI Agent", data.message);

      if (data.final_brief) {
        latestLiveBrief = data.final_brief;
        setLiveStatus("Final brief available. You can now use it as the prompt.");
      } else {
        setLiveStatus("Agent replied.");
      }
    }

    if (data.type === "transcript" && data.final_brief) {
      latestLiveBrief = data.final_brief;
      setLiveStatus("Final brief available. You can now use it as the prompt.");
    }
  };

  liveSocket.onerror = () => {
    setLiveStatus("Live session error.", true);
    setBadgeState(liveSessionBadge, "Session: Error", false);

    setButtonActive(startLiveBtn, false);
    setButtonActive(stopLiveBtn, false);
  };

  liveSocket.onclose = () => {
    setLiveStatus("Live session closed.");
    setBadgeState(liveSessionBadge, "Session: Closed", false);

    setButtonActive(startLiveBtn, false);
    setButtonActive(stopLiveBtn, false);

    if (isLiveListening) {
      stopLiveMic();
    }
  };
}

function stopLiveSession() {
  if (isLiveListening) {
    stopLiveMic();
  }

  if (liveSocket) {
    liveSocket.close();
    liveSocket = null;
  }
}

function sendLiveMessage() {
  if (!liveSocket || liveSocket.readyState !== WebSocket.OPEN) {
    setLiveStatus("Start a live session first.", true);
    return;
  }

  const text = liveInput ? liveInput.value.trim() : "";
  if (!text) {
    setLiveStatus("Enter or speak a live message first.", true);
    return;
  }

  appendLiveMessage("You", text);

  liveSocket.send(JSON.stringify({
    type: "user_text",
    text
  }));

  if (liveInput) liveInput.value = "";
  setLiveStatus("Message sent. Waiting for agent response...");
  setButtonActive(sendLiveBtn, true);

  setTimeout(() => setButtonActive(sendLiveBtn, false), 900);
}

function useLiveBriefAsPrompt() {
  if (!latestLiveBrief) {
    setLiveStatus("No final brief available yet.", true);
    return;
  }

  if (promptInput) {
    promptInput.value = latestLiveBrief;
    promptInput.focus();
  }

  setStatus("Live brief inserted into the main prompt.");
  setButtonActive(useLiveBriefBtn, true);

  setTimeout(() => setButtonActive(useLiveBriefBtn, false), 900);
}

// ---------------- Generator ----------------

async function generateContent() {
  const prompt = promptInput ? promptInput.value.trim() : "";
  const imageFile = imageInput ? imageInput.files[0] : null;

  if (!prompt) {
    setStatus("Please enter a prompt first.", true);
    return;
  }

  toggleLoading(true);
  setStatus("Generating content pack... please wait.");
  setButtonActive(generateBtn, true);

  try {
    const formData = new FormData();
    formData.append("prompt", prompt);

    if (imageFile) {
      formData.append("image", imageFile);
    }

    const response = await fetch(API.generate, {
      method: "POST",
      body: formData
    });

    const rawText = await response.text();
    const data = rawText ? JSON.parse(rawText) : {};

    if (!response.ok) {
      throw new Error(data.detail || "Failed to generate content.");
    }

    renderResult(data);

    if (promptInput) promptInput.value = "";
    if (imageInput) imageInput.value = "";
    if (selectedFileText) selectedFileText.textContent = "No file selected.";

    if (data.warnings && data.warnings.length) {
      setStatus(`Generated with warnings: ${data.warnings.join(" | ")}`, true);
    } else {
      setStatus("Content pack generated successfully.");
    }

    await loadHistory();
  } catch (error) {
    console.error("Generate error:", error);
    setStatus(`Error: ${error.message}`, true);
  } finally {
    toggleLoading(false);
    setButtonActive(generateBtn, false);
  }
}

function renderResult(data) {
  const hashtagsHtml = (data.hashtags || [])
    .map((tag) => `<span class="hashtag">${escapeHtml(tag)}</span>`)
    .join("");

  const warningHtml =
    data.warnings && data.warnings.length
      ? `
        <div class="result-card">
          <h4>Warnings</h4>
          <ul>
            ${data.warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")}
          </ul>
        </div>
      `
      : "";

  const uploadedImageHtml = data.uploaded_image_url
    ? `
      <div class="result-card image-card">
        <div class="copy-row">
          <h4>Uploaded Reference Image</h4>
          <div class="history-actions">
            <button class="copy-btn" onclick="window.open('${escapeForJs(data.uploaded_image_url)}', '_blank')">Open</button>
            <button class="copy-btn" onclick="downloadFileByUrl('${escapeForJs(data.uploaded_image_url)}', 'nexus_uploaded_image')">Download Image</button>
          </div>
        </div>
        <img class="generated-image" src="${escapeHtml(data.uploaded_image_url)}" alt="Uploaded reference image" />
      </div>
    `
    : "";

  const generatedImageHtml = data.image_url
    ? `
      <div class="result-card image-card">
        <div class="copy-row">
          <h4>Generated Image</h4>
          <div class="history-actions">
            <button class="copy-btn" onclick="window.open('${escapeForJs(data.image_url)}', '_blank')">Open</button>
            <button class="copy-btn" onclick="downloadFileByUrl('${escapeForJs(data.image_url)}', 'nexus_generated_image')">Download Image</button>
          </div>
        </div>
        <img class="generated-image" src="${escapeHtml(data.image_url)}" alt="Generated content image" />
      </div>
    `
    : "";

  resultContainer.innerHTML = `
    ${warningHtml}

    <div class="result-card">
      <h4>Platform</h4>
      <p>${escapeHtml(data.platform || "")}</p>
    </div>

    <div class="result-card">
      <h4>Target Audience</h4>
      <p>${escapeHtml(data.target_audience || "")}</p>
    </div>

    <div class="result-card">
      <h4>Tone</h4>
      <p>${escapeHtml(data.tone || "")}</p>
    </div>

    <div class="result-card">
      <h4>Caption</h4>
      <p>${escapeHtml(data.caption || "")}</p>
    </div>

    <div class="result-card">
      <h4>Hashtags</h4>
      <div class="hashtag-list">${hashtagsHtml}</div>
    </div>

    ${uploadedImageHtml}
    ${generatedImageHtml}

    <div class="result-card">
      <h4>Image Prompt</h4>
      <p>${escapeHtml(data.image_prompt || "")}</p>
    </div>

    <div class="result-card">
      <h4>Notes</h4>
      <p>${escapeHtml(data.notes || "")}</p>
    </div>

    <div class="result-card">
      <h4>Downloads</h4>
      <div class="history-actions">
        ${data.firestore_document_id ? `<button class="copy-btn" onclick="downloadHistoryJson('${escapeForJs(data.firestore_document_id)}')">JSON</button>` : ""}
        ${data.firestore_document_id ? `<button class="copy-btn" onclick="downloadHistoryTxt('${escapeForJs(data.firestore_document_id)}')">TXT</button>` : ""}
        ${data.firestore_document_id ? `<button class="copy-btn" onclick="downloadHistoryPdf('${escapeForJs(data.firestore_document_id)}')">PDF</button>` : ""}
      </div>
    </div>

    <div class="result-card">
      <h4>Document ID</h4>
      <p>${escapeHtml(data.firestore_document_id || "Not saved")}</p>
    </div>
  `;
}

// ---------------- History ----------------

async function loadHistory() {
  if (!historyContainer) return;

  historyContainer.innerHTML = "<p class='small-text'>Loading history...</p>";

  try {
    const response = await fetch(API.history);
    const rawText = await response.text();
    const data = rawText ? JSON.parse(rawText) : [];

    if (!response.ok) {
      throw new Error(data.detail || "Failed to load history.");
    }

    if (!Array.isArray(data) || data.length === 0) {
      historyContainer.innerHTML = "<p class='small-text'>No history found.</p>";
      return;
    }

    historyContainer.innerHTML = data.map((item) => `
      <div class="history-item" onclick="openHistoryDetail('${escapeForJs(item.document_id || "")}')">
        <h4>${escapeHtml(item.platform || "Untitled")}</h4>
        <p>${escapeHtml(shortenText(item.caption || "", 120))}</p>
      </div>
    `).join("");
  } catch (error) {
    console.error("History error:", error);
    historyContainer.innerHTML = `<p class="error small-text">Error loading history.</p>`;
    setStatus(`History error: ${error.message}`, true);
  }
}

async function openHistoryDetail(documentId) {
  if (!documentId || !historyModal || !modalContent) return;

  historyModal.classList.remove("hidden");
  modalContent.innerHTML = "<p>Loading detail...</p>";

  try {
    const response = await fetch(API.historyItem(documentId));
    const rawText = await response.text();
    const data = rawText ? JSON.parse(rawText) : {};

    if (!response.ok) {
      throw new Error(data.detail || "Failed to load history detail.");
    }

    const hashtagsHtml = (data.hashtags || [])
      .map((tag) => `<span class="hashtag">${escapeHtml(tag)}</span>`)
      .join("");

    modalContent.innerHTML = `
      <div class="detail-card">
        <h4>Original Prompt</h4>
        <p>${escapeHtml(data.user_prompt || "")}</p>
      </div>

      <div class="detail-card">
        <h4>Caption</h4>
        <p>${escapeHtml(data.caption || "")}</p>
      </div>

      <div class="detail-card">
        <h4>Hashtags</h4>
        <div class="hashtag-list">${hashtagsHtml}</div>
      </div>

      ${
        data.uploaded_image_url
          ? `
          <div class="detail-card image-card">
            <div class="copy-row">
              <h4>Uploaded Reference Image</h4>
              <div class="history-actions">
                <button class="copy-btn" onclick="window.open('${escapeForJs(data.uploaded_image_url)}', '_blank')">Open</button>
                <button class="copy-btn" onclick="downloadFileByUrl('${escapeForJs(data.uploaded_image_url)}', 'nexus_uploaded_image')">Download Image</button>
              </div>
            </div>
            <img class="generated-image" src="${escapeHtml(data.uploaded_image_url)}" alt="Uploaded image" />
          </div>
          `
          : ""
      }

      ${
        data.image_url
          ? `
          <div class="detail-card image-card">
            <div class="copy-row">
              <h4>Generated Image</h4>
              <div class="history-actions">
                <button class="copy-btn" onclick="window.open('${escapeForJs(data.image_url)}', '_blank')">Open</button>
                <button class="copy-btn" onclick="downloadFileByUrl('${escapeForJs(data.image_url)}', 'nexus_generated_image')">Download Image</button>
              </div>
            </div>
            <img class="generated-image" src="${escapeHtml(data.image_url)}" alt="Generated image" />
          </div>
          `
          : ""
      }

      <div class="detail-card">
        <h4>Image Prompt</h4>
        <p>${escapeHtml(data.image_prompt || "")}</p>
      </div>

      <div class="detail-card">
        <h4>Notes</h4>
        <p>${escapeHtml(data.notes || "")}</p>
      </div>

      <div class="detail-card">
        <h4>Downloads</h4>
        <div class="history-actions">
          <button class="copy-btn" onclick="downloadHistoryJson('${escapeForJs(documentId)}')">JSON</button>
          <button class="copy-btn" onclick="downloadHistoryTxt('${escapeForJs(documentId)}')">TXT</button>
          <button class="copy-btn" onclick="downloadHistoryPdf('${escapeForJs(documentId)}')">PDF</button>
        </div>
      </div>
    `;
  } catch (error) {
    console.error("History detail error:", error);
    modalContent.innerHTML = `<p class="error">Error loading detail.</p>`;
  }
}

// ---------------- Event bindings ----------------

if (generateBtn) generateBtn.addEventListener("click", generateContent);

if (clearBtn) {
  clearBtn.addEventListener("click", () => {
    if (promptInput) promptInput.value = "";
    if (imageInput) imageInput.value = "";
    if (selectedFileText) selectedFileText.textContent = "No file selected.";
    setStatus("Inputs cleared.");
  });
}

if (refreshHistoryBtn) refreshHistoryBtn.addEventListener("click", loadHistory);
if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
if (modalBackdrop) modalBackdrop.addEventListener("click", closeModal);

if (imageInput) {
  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (selectedFileText) {
      selectedFileText.textContent = file ? `Selected: ${file.name}` : "No file selected.";
    }
  });
}

if (startVoiceBtn) startVoiceBtn.addEventListener("click", startVoiceInput);
if (stopVoiceBtn) {
  stopVoiceBtn.addEventListener("click", stopVoiceInput);
  stopVoiceBtn.disabled = true;
}

if (startLiveBtn) startLiveBtn.addEventListener("click", startLiveSession);
if (stopLiveBtn) stopLiveBtn.addEventListener("click", stopLiveSession);
if (sendLiveBtn) sendLiveBtn.addEventListener("click", sendLiveMessage);
if (useLiveBriefBtn) useLiveBriefBtn.addEventListener("click", useLiveBriefAsPrompt);
if (startLiveMicBtn) startLiveMicBtn.addEventListener("click", startLiveMic);
if (stopLiveMicBtn) {
  stopLiveMicBtn.addEventListener("click", stopLiveMic);
  stopLiveMicBtn.disabled = true;
}

quickPromptButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (promptInput) {
      promptInput.value = button.textContent.trim();
      promptInput.focus();
    }
    setStatus("Quick prompt inserted.");
  });
});

window.addEventListener("load", () => {
  setupVoiceRecognition();
  setupLiveVoiceRecognition();
  loadHistory();
  setLiveStatus("Live text mode is active. Start a session, then type or speak and click Send.");
  setBadgeState(liveSessionBadge, "Session: Idle", false);
  setBadgeState(liveMicBadge, "Mic: Off", false);
});

window.openHistoryDetail = openHistoryDetail;
window.downloadHistoryJson = downloadHistoryJson;
window.downloadHistoryTxt = downloadHistoryTxt;
window.downloadHistoryPdf = downloadHistoryPdf;
window.downloadFileByUrl = downloadFileByUrl;
