# app.py — EmpathAI

import datetime
import time
import streamlit as st

st.set_page_config(
    page_title="EmpathAI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# SESSION STATE
# -----------------------------
MOOD_MAP = {
    1: ("😞", "Very low"),
    2: ("😟", "Low"),
    3: ("😐", "Okay"),
    4: ("🙂", "Good"),
    5: ("😊", "Great"),
}

TOPIC_KW = {
    "Anxiety": ["anxi", "nervous", "panic", "worry", "worried"],
    "Sadness": ["sad", "hopeless", "empty", "worthless", "down"],
    "Stress": ["stress", "overwhelm", "pressure", "burnout"],
    "Sleep": ["sleep", "insomnia", "tired", "exhausted"],
    "Loneliness": ["alone", "lonely", "isolated", "nobody", "no one"],
    "Self-esteem": ["not good enough", "hate myself", "useless", "failure"],
    "Relationships": ["relationship", "friend", "partner", "family", "breakup"],
    "Coping": ["cope", "coping", "manage", "help me"],
}

def detect_topics(msgs):
    found = set()
    for m in msgs:
        if m["role"] == "user":
            t = m["content"].lower()
            for topic, kws in TOPIC_KW.items():
                if any(k in t for k in kws):
                    found.add(topic)
    return sorted(found)

def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "<br>")
    )

if "chatbot" not in st.session_state:
    try:
        from chatbot import Chatbot
        st.session_state.chatbot = Chatbot()
        st.session_state.load_error = None
    except Exception as e:
        st.session_state.chatbot = None
        st.session_state.load_error = str(e)

if "messages" not in st.session_state:
    greeting = (
        st.session_state.chatbot.get_initial_greeting()
        if st.session_state.get("chatbot")
        else "Hello. I'm EmpathAI, a supportive assistant here to listen. I'm not a substitute for professional medical advice. In a crisis, please call or text 988 (US/Canada) or 111 (UK)."
    )
    st.session_state.messages = [{
        "role": "bot",
        "content": greeting,
        "time": datetime.datetime.now().strftime("%I:%M %p")
    }]

defaults = {
    "input_key": 0,
    "waiting": False,
    "pending_text": "",
    "mood": None,
    "mood_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_chat():
    greeting = (
        st.session_state.chatbot.get_initial_greeting()
        if st.session_state.get("chatbot")
        else "Hello. I'm EmpathAI, a supportive assistant here to listen. I'm not a substitute for professional medical advice."
    )
    st.session_state.messages = [{
        "role": "bot",
        "content": greeting,
        "time": datetime.datetime.now().strftime("%I:%M %p")
    }]
    st.session_state.mood = None
    st.session_state.mood_done = False
    st.session_state.waiting = False
    st.session_state.pending_text = ""
    if st.session_state.get("chatbot"):
        try:
            st.session_state.chatbot.history = []
        except Exception:
            pass
    st.session_state.input_key += 1


topics = detect_topics(st.session_state.messages)
user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

# -----------------------------
# STYLES
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root{
    --bg:#F4F6FB;
    --surface:#FFFFFF;
    --surface-2:#EEF1F8;
    --border:#DDE2EE;
    --accent:#4A7FE0;
    --accent-dim:rgba(74,127,224,0.10);
    --accent-glow:rgba(74,127,224,0.18);
    --user-bubble:#4A7FE0;
    --text-primary:#1A1D2E;
    --text-second:#6B7280;
    --text-muted:#9CA3AF;
    --danger:#D94F5C;
    --danger-dim:rgba(217,79,92,0.07);
    --shadow:0 2px 12px rgba(30,40,80,0.07);
}

html, body, [data-testid="stAppViewContainer"], .stApp{
    background:var(--bg)!important;
    font-family:'Inter',sans-serif;
    color:var(--text-primary);
}

#MainMenu, footer, header{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
[data-testid="stSidebar"]{display:none!important;}

.block-container{
    max-width: 1600px !important;
    padding-top: 1.05rem !important;
    padding-bottom: 0.8rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

[data-testid="stHorizontalBlock"]{
    align-items:flex-start !important;
}

/* LEFT */
.left-shell{
    position: sticky;
    top: 1rem;
}

.panel{
    background:#fff;
    border:1px solid var(--border);
    border-radius:22px;
    padding:1.2rem 1.2rem 1rem;
    box-shadow:var(--shadow);
}

.logo{
    font-family:'Sora',sans-serif;
    font-size:2.45rem;
    font-weight:700;
    color:var(--text-primary);
    letter-spacing:-1px;
    line-height:1;
    margin-bottom:0.18rem;
}
.logo span{color:var(--accent);}
.sub{
    font-size:0.94rem;
    color:#8C96AA;
    margin-bottom:1rem;
    font-weight:500;
}

.card{
    background:#F2F4FB;
    border:1px solid var(--border);
    border-radius:18px;
    padding:1rem 1.08rem;
    margin-bottom:0.85rem;
}

.card-title{
    font-family:'Sora',sans-serif;
    font-size:0.88rem;
    font-weight:700;
    color:var(--text-primary);
    letter-spacing:0.18em;
    text-transform:uppercase;
    margin-bottom:0.9rem;
}

.summary-line{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:10px;
    margin-bottom:0.65rem;
}
.summary-label{
    font-size:0.97rem;
    color:#8792A8;
    font-weight:600;
}
.summary-value{
    font-size:1rem;
    color:var(--text-primary);
    font-weight:800;
}
.summary-topic{
    font-size:0.96rem;
    color:#9BA4B5;
    font-weight:600;
    margin-top:0.15rem;
}

.breath-card{
    background:linear-gradient(90deg,#EEF3FB 0%, #EEF7F3 100%);
    text-align:center;
    min-height:235px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.breath-circle{
    width:112px;
    height:112px;
    border-radius:50%;
    margin:0 auto 0.9rem;
    background:radial-gradient(circle at 35% 30%, rgba(255,255,255,0.96), rgba(74,127,224,0.10));
    border:4px solid rgba(74,127,224,0.23);
    animation:breathe 12s ease-in-out infinite;
    box-shadow:0 0 0 8px rgba(74,127,224,0.03);
}

@keyframes breathe{
    0%   { transform:scale(0.82); opacity:0.72; }
    25%  { transform:scale(1.16); opacity:1; }
    50%  { transform:scale(1.16); opacity:1; }
    75%  { transform:scale(0.82); opacity:0.82; }
    100% { transform:scale(0.82); opacity:0.72; }
}

.breath-text{
    font-size:1.12rem;
    color:#67748C;
    font-weight:700;
    margin-bottom:0.25rem;
}
.breath-sub{
    font-size:0.96rem;
    color:#95A0B3;
    font-weight:600;
}

.crisis-card{
    background:rgba(217,79,92,0.05);
    border:1px solid rgba(217,79,92,0.20);
}
.crisis-card .card-title{
    color:#E25757;
}
.crisis-row{
    display:flex;
    justify-content:space-between;
    gap:14px;
    padding:0.5rem 0;
}
.crisis-left{
    color:#8D97AC;
    font-size:0.97rem;
    font-weight:600;
}
.crisis-right{
    color:#23283B;
    font-size:0.97rem;
    font-weight:800;
    text-align:right;
}

.about-text{
    font-size:0.97rem;
    color:#667286;
    line-height:1.72;
    font-weight:600;
}

.clear-wrap{
    margin-top:0.2rem;
}
.clear-wrap button{
    width:100%;
    min-height:52px;
    border-radius:18px !important;
    background:transparent !important;
    border:1.5px solid var(--border) !important;
    color:#31374B !important;
    font-size:0.97rem !important;
    font-weight:500 !important;
}

/* RIGHT */
.right-shell{
    padding-left:0.3rem;
}

.chat-header{
    padding:0.2rem 0 0.95rem;
    border-bottom:1px solid var(--border);
    margin-bottom:1rem;
}
.chat-header h1{
    font-family:'Sora',sans-serif;
    font-size:3rem;
    font-weight:700;
    color:var(--text-primary);
    letter-spacing:-1px;
    margin:0;
}
.chat-header h1 span{color:var(--accent);}
.chat-header p{
    font-size:1.05rem;
    color:var(--text-second);
    margin:0.35rem 0 0;
    font-weight:500;
}

.disclaimer{
    background:var(--danger-dim);
    border:1px solid rgba(217,79,92,0.18);
    border-left:5px solid var(--danger);
    border-radius:14px;
    padding:0.9rem 1rem;
    font-size:0.94rem;
    color:#B04A57;
    line-height:1.65;
    margin-bottom:1rem;
    font-weight:600;
}
.disclaimer strong{color:var(--danger);}

.mood-check-card{
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:22px;
    padding:2rem 1.6rem;
    text-align:center;
    margin-bottom:0.9rem;
    box-shadow:var(--shadow);
}
.mood-check-card h3{
    font-family:'Sora',sans-serif;
    font-size:1.8rem;
    font-weight:700;
    color:var(--text-primary);
    margin:0 0 0.5rem;
}
.mood-check-card p{
    font-size:1rem;
    color:var(--text-second);
    margin:0;
    font-weight:500;
}

[data-testid="stButton"] > button{
    background:#F4F6FB !important;
    color:var(--text-primary) !important;
    border:1.5px solid var(--border) !important;
    border-radius:16px !important;
    padding:0.65rem 0.4rem !important;
    font-size:0.94rem !important;
    box-shadow:none !important;
    width:100% !important;
    line-height:1.4 !important;
    transition:all 0.15s !important;
    font-weight:500 !important;
}
[data-testid="stButton"] > button:hover{
    border-color:var(--accent) !important;
    background:var(--accent-dim) !important;
    transform:translateY(-1px) !important;
}

/* keep active mood visually selected */
div[data-testid="stButton"] > button[kind="secondary"]{
    background:#F4F6FB !important;
}

.mood-pill{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:10px 14px;
    border:1.5px solid rgba(74,127,224,0.28);
    border-radius:16px;
    background:rgba(74,127,224,0.08);
    color:#2C4E95;
    font-weight:600;
    margin-bottom:0.2rem;
}            

/* CHAT POSITION LOWER */
.chatbox{
    margin-top: 0.9rem;
    min-height: 120px;
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
}

.msg-row{
    display:flex;
    gap:0.8rem;
    align-items:flex-end;
    margin-bottom:1rem;
}
.msg-row.user{
    flex-direction:row-reverse;
}
.av{
    width:38px;
    height:38px;
    border-radius:12px;
    flex-shrink:0;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family:'Sora',sans-serif;
    font-size:0.8rem;
    font-weight:700;
}
.av.bot{
    background:var(--accent-dim);
    border:1.5px solid rgba(74,127,224,0.22);
    color:var(--accent);
}
.av.usr{
    background:var(--user-bubble);
    color:#fff;
}

.bwrap{
    display:flex;
    flex-direction:column;
    max-width:74%;
}
.msg-row.user .bwrap{
    align-items:flex-end;
}
.bbl{
    padding:1rem 1.15rem;
    border-radius:18px;
    font-size:1rem;
    line-height:1.75;
    word-wrap:break-word;
    overflow-wrap:anywhere;
}
.bbl.bot{
    background:var(--surface);
    border:1px solid var(--border);
    border-bottom-left-radius:6px;
    box-shadow:var(--shadow);
    color:var(--text-primary);
}
.bbl.usr{
    background:var(--user-bubble);
    color:#fff;
    border-bottom-right-radius:6px;
    box-shadow:0 4px 12px rgba(74,127,224,0.20);
}
.btime{
    font-size:0.74rem;
    color:var(--text-muted);
    margin-top:0.25rem;
    padding:0 0.25rem;
}

.typing-row{
    display:flex;
    gap:0.8rem;
    align-items:flex-end;
    margin-bottom:1rem;
}
.typing-bbl{
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:18px;
    border-bottom-left-radius:6px;
    padding:0.85rem 1rem;
    display:flex;
    gap:6px;
    align-items:center;
    box-shadow:var(--shadow);
    min-width:70px;
}
.dot{
    width:7px;
    height:7px;
    background:var(--accent);
    border-radius:50%;
    opacity:0.45;
    animation:bce 1.2s infinite ease-in-out;
}
.dot:nth-child(2){animation-delay:.2s}
.dot:nth-child(3){animation-delay:.4s}

@keyframes bce{
    0%,80%,100%{transform:translateY(0)}
    40%{transform:translateY(-5px);opacity:1}
}

.input-shell{
    margin-top:0.7rem;
    padding-top:0.2rem;
}

.input-shell [data-testid="stTextInput"] > div > div{
    background:var(--surface) !important;
    border:1.5px solid var(--border) !important;
    border-radius:999px !important;
    box-shadow:var(--shadow) !important;
}
.input-shell [data-testid="stTextInput"] > div > div:focus-within{
    border-color:var(--accent) !important;
    box-shadow:0 0 0 3px var(--accent-glow) !important;
}
.input-shell [data-testid="stTextInput"] input{
    background:transparent !important;
    color:var(--text-primary) !important;
    font-size:1rem !important;
    padding:0.9rem 1.2rem !important;
    border:none !important;
    box-shadow:none !important;
}
.input-shell [data-testid="stTextInput"] label{
    display:none !important;
}

.send-btn button{
    background:var(--accent) !important;
    color:white !important;
    border:none !important;
    border-radius:999px !important;
    min-height:52px !important;
    font-family:'Sora',sans-serif !important;
    font-weight:600 !important;
    box-shadow:0 3px 12px rgba(74,127,224,0.28) !important;
}

@media (max-width: 1200px){
    .logo{font-size:2.2rem;}
    .chat-header h1{font-size:2.3rem;}
    .bwrap{max-width:85%;}
    .chatbox{min-height:220px;}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LAYOUT
# -----------------------------
left_col, right_col = st.columns([1.02, 2.2], gap="large")

# -----------------------------
# LEFT PANEL
# -----------------------------
with left_col:
    st.markdown("<div class='left-shell'>", unsafe_allow_html=True)
    # st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="logo">Empath<span>AI</span></div>
        <div class="sub">Mental Health Support Assistant</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Session Summary</div>
            <div class="summary-line">
                <div class="summary-label">Messages sent</div>
                <div class="summary-value">{user_count}</div>
            </div>
            <div class="summary-line" style="margin-bottom:0.2rem;">
                <div class="summary-label">Topics detected</div>
                <div class="summary-value"></div>
            </div>
            <div class="summary-topic">{", ".join(topics) if topics else "None yet"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card breath-card">
            <div class="card-title" style="text-align:center; margin-bottom:1.1rem;">Breathing Exercise</div>
            <div class="breath-circle"></div>
            <div class="breath-text">Hold...</div>
            <div class="breath-sub">4s in · 4s hold · 4s out</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card crisis-card">
            <div class="card-title">Crisis Support</div>
            <div class="crisis-row">
                <div class="crisis-left">US &amp; Canada</div>
                <div class="crisis-right">Call / Text 988</div>
            </div>
            <div class="crisis-row">
                <div class="crisis-left">United Kingdom</div>
                <div class="crisis-right">Call 111</div>
            </div>
            <div class="crisis-row">
                <div class="crisis-left">Resources</div>
                <div class="crisis-right"><a href="https://findtreatment.gov" target="_blank">FindTreatment.gov</a></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card">
            <div class="card-title">About</div>
            <div class="about-text">
                EmpathAI draws on real therapeutic conversation patterns to offer supportive responses.
                Not a replacement for a licensed mental health professional.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='clear-wrap'>", unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        reset_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# -----------------------------
# RIGHT PANEL
# -----------------------------
with right_col:
    st.markdown("<div class='right-shell'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class='chat-header'>
            <h1>Empath<span>AI</span></h1>
            <p>A private space to reflect, process, and feel supported</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("load_error"):
        st.warning(f"Demo mode — backend not loaded: `{st.session_state.load_error}`")

    st.markdown(
        """
        <div class='disclaimer'>
            <strong>Reminder:</strong> EmpathAI is an AI assistant, not a licensed therapist.
            It cannot provide diagnoses or emergency care. In a crisis, call <strong>988</strong>
            (US/Canada) or <strong>111</strong> (UK).
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.mood_done:
        st.markdown(
            """
            <div class='mood-check-card'>
                <h3>How are you feeling right now?</h3>
                <p>Take a moment to check in with yourself before we begin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        mcols = st.columns(5)
        for i, mc in enumerate(mcols, 1):
            icon, label = MOOD_MAP[i]
            with mc:
                if st.button(f"{icon} {label}", key=f"mood_{i}"):
                    st.session_state.mood = i
                    st.session_state.mood_done = True
                    st.rerun()

    else:
        icon, label = MOOD_MAP[st.session_state.mood]
        st.markdown(
            f"""
            <div style="
                display:inline-flex;
                align-items:center;
                gap:8px;
                padding:10px 14px;
                border:1.5px solid rgba(74,127,224,0.28);
                border-radius:16px;
                background:rgba(74,127,224,0.08);
                color:#2C4E95;
                font-weight:600;
                margin-bottom:0.5rem;">
                <span>{icon}</span>
                <span>Feeling {label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='chatbox'>", unsafe_allow_html=True)

    html = ""
    for msg in st.session_state.messages:
        content = esc(msg["content"])
        t = msg.get("time", "")
        if msg["role"] == "bot":
            html += (
                f"<div class='msg-row bot'>"
                f"<div class='av bot'>EA</div>"
                f"<div class='bwrap'>"
                f"<div class='bbl bot'>{content}</div>"
                f"<div class='btime'>{t}</div>"
                f"</div></div>"
            )
        else:
            html += (
                f"<div class='msg-row user'>"
                f"<div class='av usr'>You</div>"
                f"<div class='bwrap'>"
                f"<div class='bbl usr'>{content}</div>"
                f"<div class='btime'>{t}</div>"
                f"</div></div>"
            )

    if st.session_state.waiting:
        html += (
            "<div class='typing-row'>"
            "<div class='av bot'>EA</div>"
            "<div class='typing-bbl'><div class='dot'></div><div class='dot'></div><div class='dot'></div></div>"
            "</div>"
        )

    st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='input-shell'>", unsafe_allow_html=True)
    ic, sc = st.columns([11, 1.4])
    with ic:
        user_input = st.text_input(
            "msg",
            placeholder="Type a message...",
            key=f"input_{st.session_state.input_key}",
            label_visibility="collapsed",
            disabled=st.session_state.waiting,
        )
    with sc:
        st.markdown("<div class='send-btn'>", unsafe_allow_html=True)
        send = st.button("Send", disabled=st.session_state.waiting, key="send_btn")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# SEND
# -----------------------------
if send and user_input.strip():
    text = user_input.strip()
    st.session_state.messages.append({
        "role": "user",
        "content": text,
        "time": datetime.datetime.now().strftime("%I:%M %p")
    })
    st.session_state.input_key += 1
    st.session_state.waiting = True
    st.session_state.pending_text = text
    st.rerun()

# -----------------------------
# BOT REPLY AFTER PAGE RENDERS
# -----------------------------
if st.session_state.waiting and st.session_state.pending_text:
    time.sleep(0.45)

    text = st.session_state.pending_text
    try:
        reply = (
            st.session_state.chatbot.get_response(text)
            if st.session_state.chatbot
            else "Thank you for sharing. Your feelings are valid. Can you tell me a little more about what's been weighing on you?"
        )
    except Exception as e:
        reply = f"I'm sorry, something went wrong: {e}. Please try again."

    st.session_state.messages.append({
        "role": "bot",
        "content": reply or "I'm here with you — could you say a bit more?",
        "time": datetime.datetime.now().strftime("%I:%M %p")
    })
    st.session_state.waiting = False
    st.session_state.pending_text = ""
    st.rerun()