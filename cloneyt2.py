# 1️⃣ Imports (TOP OF FILE)
import streamlit as st
import time
import tempfile
import os
import whisper
import requests

# --- 1. Page Configuration (must be first) ---
st.set_page_config(
    page_title="CODEGEN AI",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded",  # ensure sidebar starts open
)

# --- 2. Theme State ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # "dark" or "light"

# --- 3. CSS for Dark & Light Themes ---
DARK_CSS = """
<style>
/* Overall Dark Theme */
.stApp {
    background-color: #101015;
    color: #FFFFFF;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Keep header visible so sidebar toggle is accessible */
header[data-testid="stHeader"] {
    background: transparent;
    box-shadow: none;
}

/* You can still hide footer if you want */
footer {
    visibility: hidden;
}

/* Main Container */
div.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Centered Title */
div.block-container h1 {
    text-align: center;
    margin-top: 3vh;
    margin-bottom: 1rem;
    font-size: 2.6rem;
    letter-spacing: 0.08em;
}

/* Sidebar Styling + Hover Expand */
div[data-testid="stSidebar"] {
    width: 72px !important;        /* collapsed width */
    background: linear-gradient(180deg, #050506, #111118);
    padding-top: 1.5rem;
    border-right: 1px solid #22222A;
    transition: width 0.2s ease-in-out;
    overflow-x: hidden;
}

/* On hover: expand sidebar */
div[data-testid="stSidebar"]:hover {
    width: 260px !important;
}

/* Sidebar headers */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1rem;
    margin-bottom: 0.6rem;
}

/* Small section labels */
.sidebar-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8C8CA0;
    margin-bottom: 0.3rem;
}

/* Sidebar Buttons (chat items + new chat) */
.stButton > button {
    background-color: #1E1E26;
    color: #FFFFFF;
    border: 1px solid #2C2C38;
    text-align: left;
    padding: 0.45rem 0.6rem 0.45rem 0.75rem;
    margin-bottom: 0.25rem;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    transition: background-color 0.15s ease, transform 0.05s ease, border-color 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stButton > button:hover {
    background-color: #272736;
    border-color: #3C3C4A;
    transform: translateY(-1px);
}

/* Active Chat Button */
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"] {
    background: linear-gradient(135deg, #10A37F, #0F8A6B);
    border-color: #10A37F;
    color: #FFFFFF;
    font-weight: 500;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid*="primary"]:hover {
    background: linear-gradient(135deg, #10A37F, #10A37F);
}

/* Chat Messages Container */
div[data-testid="stChatMessage"] {
    background-color: #181820;
    border-radius: 14px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.5rem;
    border: 1px solid #262636;
}

/* Slightly different background every other message */
div[data-testid="stChatMessage"]:nth-of-type(even) {
    background-color: #14141C;
}

/* Markdown inside messages */
div[data-testid="stChatMessage"] p {
    margin-bottom: 0.2rem;
    font-size: 0.95rem;
    line-height: 1.4;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    border-top: 1px solid #252533;
    padding-top: 0.5rem;
}
div[data-testid="stChatInput"] textarea {
    border-radius: 10px;
    border: 1px solid #2F2F3A;
    background-color: #12121A;
    color: #FFFFFF;
    font-size: 0.95rem;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #10A37F;
    box-shadow: 0 0 0 1px #10A37F33;
}

/* Small helper text under title */
.codeGEN AI-subtitle {
    text-align: center;
    font-size: 0.9rem;
    color: #AAAAAA;
    margin-bottom: 1.5rem;
}

/* Sidebar text input styling (search, rename) */
div[data-testid="stSidebar"] input[type="text"] {
    background-color: #12121A;
    border-radius: 8px;
    border: 1px solid #2F2F3A;
    color: #FFFFFF;
    font-size: 0.85rem;
}
div[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: #10A37F;
    box-shadow: 0 0 0 1px #10A37F33;
}

/* File & Voice input container styling */
.file-voice-container {
    border-radius: 10px;
    border: 1px solid #262636;
    background-color: #14141C;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.8rem;
}
.file-voice-title {
    font-size: 0.85rem;
    color: #CCCCCC;
    margin-bottom: 0.3rem;
}
.file-pill {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    border: 1px solid #2C2C38;
    font-size: 0.75rem;
    margin-right: 0.3rem;
    margin-bottom: 0.2rem;
    background-color: #1E1E26;
}
</style>
"""

LIGHT_CSS = """
<style>
/* Overall Light Theme */
.stApp {
    background-color: #F5F5F8;
    color: #111111;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Keep header visible so sidebar toggle is accessible */
header[data-testid="stHeader"] {
    background: transparent;
    box-shadow: none;
}

/* Hide footer if desired */
footer {
    visibility: hidden;
}

/* Main Container */
div.block-container {
    padding-top: 1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Centered Title */
div.block-container h1 {
    text-align: center;
    margin-top: 3vh;
    margin-bottom: 1rem;
    font-size: 2.6rem;
    letter-spacing: 0.08em;
}

/* Sidebar Styling + Hover Expand */
div[data-testid="stSidebar"] {
    width: 72px !important;        /* collapsed width */
    background: linear-gradient(180deg, #FFFFFF, #ECECF2);
    padding-top: 1.5rem;
    border-right: 1px solid #D2D2E0;
    transition: width 0.2s ease-in-out;
    overflow-x: hidden;
}

/* On hover: expand sidebar */
div[data-testid="stSidebar"]:hover {
    width: 260px !important;
}

/* Sidebar headers */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1rem;
    margin-bottom: 0.6rem;
}

/* Small section labels */
.sidebar-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6B6B80;
    margin-bottom: 0.3rem;
}

/* Sidebar Buttons (chat items + new chat) */
.stButton > button {
    background-color: #FFFFFF;
    color: #111111;
    border: 1px solid #D4D4E0;
    text-align: left;
    padding: 0.45rem 0.6rem 0.45rem 0.75rem;
    margin-bottom: 0.25rem;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    transition: background-color 0.15s ease, transform 0.05s ease, border-color 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stButton > button:hover {
    background-color: #F0F0FA;
    border-color: #C0C0D8;
    transform: translateY(-1px);
}

/* Active Chat Button */
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"] {
    background: linear-gradient(135deg, #10A37F, #0F8A6B);
    border-color: #10A37F;
    color: #FFFFFF;
    font-weight: 500;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid*="primary"]:hover {
    background: linear-gradient(135deg, #10A37F, #10A37F);
}

/* Chat Messages Container */
div[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.5rem;
    border: 1px solid #E0E0EC;
}

/* Slightly different background every other message */
div[data-testid="stChatMessage"]:nth-of-type(even) {
    background-color: #F8F8FF;
}

/* Markdown inside messages */
div[data-testid="stChatMessage"] p {
    margin-bottom: 0.2rem;
    font-size: 0.95rem;
    line-height: 1.4;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    border-top: 1px solid #D8D8E5;
    padding-top: 0.5rem;
}
div[data-testid="stChatInput"] textarea {
    border-radius: 10px;
    border: 1px solid #D0D0E0;
    background-color: #FFFFFF;
    color: #111111;
    font-size: 0.95rem;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #10A37F;
    box-shadow: 0 0 0 1px #10A37F33;
}

/* Small helper text under title */
.codeGEN AI-subtitle {
    text-align: center;
    font-size: 0.9rem;
    color: #555577;
    margin-bottom: 1.5rem;
}

/* Sidebar text input styling (search, rename) */
div[data-testid="stSidebar"] input[type="text"] {
    background-color: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #D0D0E0;
    color: #111111;
    font-size: 0.85rem;
}
div[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: #10A37F;
    box-shadow: 0 0 0 1px #10A37F33;
}

/* File & Voice input container styling */
.file-voice-container {
    border-radius: 10px;
    border: 1px solid #D8D8E5;
    background-color: #FFFFFF;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.8rem;
}
.file-voice-title {
    font-size: 0.85rem;
    color: #444466;
    margin-bottom: 0.3rem;
}
.file-pill {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    border: 1px solid #D0D0E0;
    font-size: 0.75rem;
    margin-right: 0.3rem;
    margin-bottom: 0.2rem;
    background-color: #F5F5FF;
}
</style>
"""

# Inject theme CSS
st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# --- 4. Title & Subtitle ---
st.title("CODEGEN AI")
st.markdown(
    '<div class="codeGEN AI-subtitle">CODEGEN AI.</div>'
,
    unsafe_allow_html=True
)

# --- 5. Core Session State ---
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "chat_0"

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "history" not in st.session_state:
    st.session_state.history = [{"id": "chat_0", "title": "New Chat"}]

if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "OpenAI"

if "selected_model_ui" not in st.session_state:
    st.session_state.selected_model_ui = "gpt-4.1-mini"

if "chat_search" not in st.session_state:
    st.session_state.chat_search = ""

if "chat_files" not in st.session_state:
    st.session_state.chat_files = {}

if "chat_audio_name" not in st.session_state:
    st.session_state.chat_audio_name = {}

# Ensure current chat exists
if st.session_state.current_chat_id not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat_id] = [
        {
            "role": "assistant",
            "content": "Welcome to **CODEGEN AI**."

        }
    ]

# --- 6. Helper Functions ---
def set_chat(chat_id: str) -> None:
    st.session_state.current_chat_id = chat_id

def new_chat() -> None:
    new_id = f"chat_{int(time.time() * 1000)}"
    st.session_state.chats[new_id] = [
        {"role": "assistant", "content": "Starting a new conversation UI."}
    ]
    st.session_state.history.insert(0, {"id": new_id, "title": "New Chat"})
    st.session_state.current_chat_id = new_id

def delete_chat(chat_id: str) -> None:
    st.session_state.chats.pop(chat_id, None)
    st.session_state.chat_files.pop(chat_id, None)
    st.session_state.chat_audio_name.pop(chat_id, None)

    st.session_state.history = [
        c for c in st.session_state.history if c["id"] != chat_id
    ]

    if not st.session_state.history:
        st.session_state.current_chat_id = "chat_0"
        st.session_state.chats["chat_0"] = [
            {
                "role": "assistant",
                "content": "Welcome to **CODEGEN AI**. Fresh start!"
            }
        ]
        st.session_state.history = [{"id": "chat_0", "title": "New Chat"}]
    else:
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = st.session_state.history[0]["id"]

def fake_model_response(prompt: str) -> str:
    provider = st.session_state.selected_provider
    model = st.session_state.selected_model_ui

    return (
        f"**Provider:** `{provider}`\n"
        f"**Model:** `{model}`\n\n"
        f"{prompt}"
    )


def get_current_chat_metadata():
    return next(
        (item for item in st.session_state.history
         if item["id"] == st.session_state.current_chat_id),
        None,
    )

def filter_history_by_search():
    query = st.session_state.chat_search.strip().lower()
    if not query:
        return st.session_state.history

    filtered = []
    for chat_meta in st.session_state.history:
        cid = chat_meta["id"]
        title = chat_meta["title"]
        title_match = query in title.lower()

        content_match = False
        for msg in st.session_state.chats.get(cid, []):
            if query in msg["content"].lower():
                content_match = True
                break

        if title_match or content_match:
            filtered.append(chat_meta)
    return filtered

# --- 7. Sidebar (Settings, Models, Search, History, Rename/Delete current) ---
with st.sidebar:
    # Settings (theme toggle)
    st.markdown('<div class="sidebar-label">THEME</div>', unsafe_allow_html=True)
    theme_choice = st.radio(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.theme = "dark" if theme_choice == "Dark" else "light"

    st.markdown("---")

    # Model provider + model (UI-only)
    st.markdown('<div class="sidebar-label">Provider</div>', unsafe_allow_html=True)
    st.session_state.selected_provider = st.radio(
        "",
        ["OpenAI", "Gemini", "Local"],
        index=["OpenAI", "Gemini", "Local"].index(st.session_state.selected_provider),
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-label" style="margin-top:0.6rem;">Model</div>', unsafe_allow_html=True)

    provider = st.session_state.selected_provider
    if provider == "OpenAI":
        model_options = ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-4o"]
    elif provider == "Gemini":
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
    else:
        model_options = ["llama-3-8B", "mistral-7B", "custom-local-model"]

    if st.session_state.selected_model_ui not in model_options:
        st.session_state.selected_model_ui = model_options[0]

    st.session_state.selected_model_ui = st.selectbox(
        "",
        model_options,
        index=model_options.index(st.session_state.selected_model_ui),
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Search bar
    st.markdown('<div class="sidebar-label">Search chats</div>', unsafe_allow_html=True)
    st.session_state.chat_search = st.text_input(
        "",
        value=st.session_state.chat_search,
        placeholder="Search by title or content...",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-label" style="margin-top:0.6rem;">Chats</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown("")

    # Filtered chat list with delete icons
    filtered_history = filter_history_by_search()
    if not filtered_history:
        st.caption("No chats found.")
    else:
        for chat in filtered_history:
            chat_id = chat["id"]
            chat_title = chat["title"]
            is_active = (chat_id == st.session_state.current_chat_id)

            row = st.columns([5, 1])
            with row[0]:
                if st.button(
                    chat_title,
                    key=f"hist_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    help=chat_title,
                ):
                    set_chat(chat_id)
                    st.rerun()
            with row[1]:
                if st.button(
                    "🗑",
                    key=f"del_hist_{chat_id}",
                    use_container_width=True,
                    help="Delete this chat",
                ):
                    delete_chat(chat_id)
                    st.rerun()

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Current chat</div>', unsafe_allow_html=True)

    current_meta = get_current_chat_metadata()
    if current_meta:
        new_title = st.text_input(
            "Rename",
            value=current_meta["title"],
            key=f"rename_input_{st.session_state.current_chat_id}",
            label_visibility="collapsed",
        )

        cols = st.columns([2, 1])
        with cols[0]:
            if st.button("💾 Save title", use_container_width=True):
                current_meta["title"] = new_title.strip() or current_meta["title"]
                st.rerun()
        with cols[1]:
            if st.button("🗑 Delete", use_container_width=True):
                delete_chat(current_meta["id"])
                st.rerun()

# --- 8. File Upload & Voice Input (UI only, above messages) ---
st.markdown('<div class="file-voice-container">', unsafe_allow_html=True)
cols_top = st.columns([2, 2])

current_chat_id = st.session_state.current_chat_id


@st.cache_resource
def load_whisper():
    return whisper.load_model("base")  # or "tiny" for faster

def transcribe_audio(audio_bytes):
    model = load_whisper()

    fd, path = tempfile.mkstemp(suffix=".wav")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes.getvalue())

        result = model.transcribe(path)
        return result["text"].strip()

    finally:
        try:
            os.remove(path)
        except Exception:
            pass


with cols_top[0]:
    st.markdown('<div class="file-voice-title">📎 Attach files</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
    "Attach files",
    type=["txt", "md", "csv"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key=f"file_upload_{current_chat_id}",
)

    if uploaded_files:
        st.session_state.chat_files[current_chat_id] = [f.name for f in uploaded_files]

    files_for_chat = st.session_state.chat_files.get(current_chat_id, [])
    if files_for_chat:
        for name in files_for_chat:
            st.markdown(f'<span class="file-pill">{name}</span>', unsafe_allow_html=True)

with cols_top[1]:
    st.markdown('<div class="file-voice-title">🎙 Speak</div>', unsafe_allow_html=True)

    # 🎙 REAL microphone input
    audio_bytes = st.audio_input(
        "Speak now",
        key=f"mic_input_{current_chat_id}"
    )

    if audio_bytes is not None:
        # Optional: playback
        st.audio(audio_bytes)

        # 📝 Transcribe speech
        transcript = transcribe_audio(audio_bytes)

        # 👤 Add transcript as user message
        st.session_state.chats[current_chat_id].append(
            {"role": "user", "content": transcript}
        )

        # Flag to trigger model response (NO rerun here)
        st.session_state.pending_audio_prompt = True

def extract_text_from_files(files):
    text = ""
    for file in files:
        try:
            content = file.read().decode("utf-8")
            text += f"\n\n[File: {file.name}]\n{content}"
        except:
            text += f"\n\n[File: {file.name} - could not read as text]"
    return text

# --- 9. Main Chat Display ---
messages = st.session_state.chats[current_chat_id]

for message in messages:
    with st.chat_message(
        message["role"],
        avatar="🤖" if message["role"] == "assistant" else "🧑"
    ):
        st.markdown(message["content"])

# --- 10. Chat Input + Frontend Streaming Effect ---
if prompt := st.chat_input("Message..."):
    st.session_state.chats[current_chat_id].append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    files = st.session_state.get("chat_files", {}).get(current_chat_id, [])
file_context = ""

if uploaded_files:
    file_context = extract_text_from_files(uploaded_files)
def generate_ollama_response(chat_id, model="phi3", extra_context=""):
    messages = []

    if extra_context:
        messages.append({
            "role": "system",
            "content": f"Use the following uploaded files as context:\n{extra_context}"
        })

    for msg in st.session_state.chats[chat_id]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=120
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        return f"⚠️ Backend error: {e}"


assistant_response = generate_ollama_response(
    current_chat_id,
    model="phi3",
    extra_context=file_context
)


with st.chat_message("assistant", avatar="🤖"):
    message_placeholder = st.empty()
    full_response = ""

    for chunk in assistant_response.split():
        full_response += chunk + " "
        time.sleep(0.03)
        message_placeholder.markdown(full_response + "▌")

    message_placeholder.markdown(full_response)

st.session_state.chats[current_chat_id].append(
    {"role": "assistant", "content": full_response}
)

current_chat_metadata = get_current_chat_metadata()
if current_chat_metadata and current_chat_metadata["title"] == "New Chat":
    current_chat_metadata["title"] = (
        prompt[:40] + "..." if len(prompt) > 40 else prompt
    )
    st.rerun()
    

