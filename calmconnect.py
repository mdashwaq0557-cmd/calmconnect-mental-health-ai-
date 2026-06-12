import streamlit as st
from google import genai
from google.genai import types
import time
import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CalmConnect – Mental Health Support",
    page_icon="🧠",
    layout="wide",
)

# ---------------- GEMINI CLIENT INITIALIZATION ----------------
# Securely pulls the API key from your Streamlit App Secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    client = None

# ---------------- SESSION STATE ----------------
defaults = {
    "conversation_history": [],
    "user_name": "User",
    "show_questionnaire": False,
    "show_wellness": False,
    "meditation_running": False,
    "meditation_seconds": 0,
    "meditation_total": 60,
    "affirmation_index": 0,
    "stress_score": None,
    "anxiety_level": None,
    "sleep_quality": None,
    "show_results": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- AFFIRMATIONS ----------------
AFFIRMATIONS = [
    "You are stronger than you think. 💪",
    "Every day is a fresh start. 🌅",
    "You are worthy of love and belonging. 💛",
    "It's okay to ask for help. 🤝",
    "You have survived 100% of your bad days so far. ✨",
    "Your feelings are valid. Take it one breath at a time. 🌬️",
    "Healing is not linear, and that's perfectly fine. 🌱",
    "You are not alone in this journey. 🌍",
    "Small steps still move you forward. 👣",
    "Be gentle with yourself today. 🌸",
]

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings & Tools")
st.session_state.user_name = st.sidebar.text_input("Your name", value=st.session_state.user_name)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.conversation_history = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧘 Wellness Tools")
if st.sidebar.button("📋 Mental Health Check-In", use_container_width=True):
    st.session_state.show_questionnaire = not st.session_state.show_questionnaire
    st.session_state.show_wellness = False
    st.rerun()
if st.sidebar.button("🌿 Wellness & Exercises", use_container_width=True):
    st.session_state.show_wellness = not st.session_state.show_wellness
    st.session_state.show_questionnaire = False
    st.rerun()

st.sidebar.markdown("---")
aff_idx = st.session_state.affirmation_index % len(AFFIRMATIONS)
st.sidebar.markdown(f"### 💬 Daily Affirmation")
st.sidebar.info(AFFIRMATIONS[aff_idx])
if st.sidebar.button("🔄 Next Affirmation", use_container_width=True):
    st.session_state.affirmation_index += 1
    st.rerun()

# ---------------- CSS STYLING ----------------
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600&family=Space+Grotesk:wght=400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.block-container { padding-top: 1.5rem !important; max-width: 1400px; }

.stApp {
    background: linear-gradient(-45deg, #f4f7f6, #eef2f3, #e8ebea, #f4f7f6) !important;
    background-size: 400% 400% !important;
    animation: gradientMove 18s ease infinite !important;
    color: #1e293b !important;
    font-family: 'Inter', sans-serif;
}

@keyframes gradientMove {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.robot-bg {
    position: fixed;
    bottom: -20px;
    right: -20px;
    width: 320px;
    height: 320px;
    opacity: 0.04;
    z-index: 0;
    pointer-events: none;
    animation: robotFloat 6s ease-in-out infinite;
}
@keyframes robotFloat {
    0%, 100% { transform: translateY(0px) rotate(-3deg); }
    50%       { transform: translateY(-18px) rotate(3deg); }
}

.mascot-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
}
.mascot-svg {
    width: 64px;
    height: 64px;
    animation: mascotBob 3s ease-in-out infinite;
    filter: drop-shadow(0 4px 15px rgba(25, 118, 210, 0.15));
}
@keyframes mascotBob {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-6px); }
}

.typing-dots { display: inline-flex; gap: 5px; align-items: center; padding: 12px 18px; }
.typing-dots span {
    width: 9px; height: 9px;
    background: #1976d2;
    border-radius: 50%;
    display: inline-block;
    animation: dotBounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
    0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
    40%            { transform: scale(1.2); opacity: 1; }
}

.msg-row { display: flex; align-items: flex-end; gap: 10px; margin-bottom: 14px; animation: msgSlide 0.35s ease; }
.msg-row.user { flex-direction: row-reverse; }
@keyframes msgSlide {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.avatar.user-av { background: linear-gradient(135deg, #1976d2, #42a5f5); }
.avatar.ai-av   { background: #ffffff; border: 1px solid #e2e8f0; }

.bubble-wrap { max-width: 74%; }
.timestamp {
    font-size: 10px;
    opacity: 0.5;
    margin-top: 3px;
    padding: 0 6px;
    font-family: 'Inter', sans-serif;
}
.msg-row.user .timestamp { text-align: right; }

.user-msg {
    background: linear-gradient(135deg, #1976d2, #42a5f5);
    color: white;
    padding: 11px 16px;
    border-radius: 18px 18px 4px 18px;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: 0 4px 10px rgba(25, 118, 210, 0.15);
    word-break: break-word;
}
.ai-msg {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 11px 16px;
    border-radius: 18px 18px 18px 4px;
    font-size: 14px;
    line-height: 1.5;
    word-break: break-word;
    color: #1e293b;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.response-box {
    height: 62vh;
    overflow-y: auto;
    padding: 14px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.response-box::-webkit-scrollbar { width: 5px; }
.response-box::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 12px;
}

.stSidebar .stButton > button {
    border-radius: 10px !important;
    height: auto !important;
    width: 100% !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: none !important;
}
.stSidebar .stButton > button:hover {
    border-color: #1976d2 !important;
    color: #1976d2 !important;
    background: rgba(25, 118, 210, 0.05) !important;
}

.send-btn-container {
    display: flex;
    justify-content: flex-start;
    margin-top: 10px;
}
.send-btn-container .stButton > button {
    border-radius: 50% !important;
    height: 52px !important;
    width: 52px !important;
    font-size: 20px !important;
    background: linear-gradient(45deg, #1976d2, #42a5f5) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.15) !important;
    transition: 0.25s !important;
}
.send-btn-container .stButton > button:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 6px 20px rgba(25, 118, 210, 0.3) !important;
}

.stSlider > div > div { accent-color: #1976d2; }

.score-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 13px;
    margin: 4px;
}
.score-low  { background: rgba(34, 197, 94, 0.1); color: #16a34a; border: 1px solid #bbf7d0; }
.score-mid  { background: rgba(234, 179, 8, 0.1);  color: #ca8a04; border: 1px solid #fef08a; }
.score-high { background: rgba(239, 68, 68, 0.1);  color: #dc2626; border: 1px solid #fecaca; }

.med-ring {
    width: 140px; height: 140px;
    border-radius: 50%;
    background: conic-gradient(#1976d2 calc(var(--pct) * 3.6deg), #f1f5f9 0deg);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    animation: ringPulse 2s ease-in-out infinite;
    position: relative;
}
.med-ring-inner {
    width: 110px; height: 110px;
    border-radius: 50%;
    background: #ffffff;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    font-weight: 700;
    color: #1976d2;
    font-family: 'Space Grotesk', sans-serif;
}
@keyframes ringPulse {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.02); }
}

.breath-circle {
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(25, 118, 210, 0.15), rgba(66, 165, 245, 0.05));
    border: 3px solid #1976d2;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto;
    animation: breathe 8s ease-in-out infinite;
    color: #0f172a;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
    padding: 10px;
}
@keyframes breathe {
    0%,  100% { transform: scale(1);   opacity: 0.8; }
    37.5%     { transform: scale(1.3); opacity: 1;   }
    62.5%     { transform: scale(1.3); opacity: 1;   }
}

footer { visibility: hidden; }
h1, h2, h3 { color: #0f172a !important; }
.stTextArea textarea { background: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; border-radius: 12px !important; }
.stTextArea textarea:focus { border-color: #1976d2 !important; box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.2) !important; }
label { color: #334155 !important; font-weight: 500; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0; padding: 8px 16px; color: #64748b; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #1976d2 !important; border-bottom: 2px solid #1976d2 !important; font-weight: 600; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---- Background Animated Grid SVG ----
st.markdown("""
<svg class="robot-bg" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="60" y="70" width="80" height="70" rx="14" fill="#64748b"/>
  <rect x="75" y="50" width="50" height="28" rx="10" fill="#64748b"/>
  <line x1="100" y1="50" x2="100" y2="40" stroke="#64748b" stroke-width="4"/>
  <circle cx="100" cy="34" r="6" fill="#64748b"/>
  <circle cx="86" cy="62" r="7" fill="#e2e8f0"/>
  <circle cx="114" cy="62" r="7" fill="#e2e8f0"/>
  <circle cx="86" cy="62" r="4" fill="#64748b"/>
  <circle cx="114" cy="62" r="4" fill="#64748b"/>
  <rect x="80" y="88" width="40" height="6" rx="3" fill="#e2e8f0"/>
  <rect x="85" y="100" width="30" height="6" rx="3" fill="#e2e8f0"/>
  <rect x="44" y="80" width="16" height="40" rx="8" fill="#64748b"/>
  <rect x="140" y="80" width="16" height="40" rx="8" fill="#64748b"/>
  <rect x="72" y="140" width="18" height="35" rx="9" fill="#64748b"/>
  <rect x="110" y="140" width="18" height="35" rx="9" fill="#64748b"/>
</svg>
""", unsafe_allow_html=True)

# ---- Mascot Header ----
st.markdown("""
<div class="mascot-wrap">
  <svg class="mascot-svg" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="40" r="38" fill="rgba(25, 118, 210, 0.1)"/>
    <rect x="20" y="28" width="40" height="32" rx="10" fill="#1976d2"/>
    <rect x="27" y="18" width="26" height="16" rx="8" fill="#1976d2"/>
    <line x1="40" y1="18" x2="40" y2="11" stroke="#1976d2" stroke-width="3"/>
    <circle cx="40" cy="8" r="4" fill="#42a5f5"/>
    <circle cx="32" cy="25" r="5" fill="white" opacity="0.9"/>
    <circle cx="48" cy="25" r="5" fill="white" opacity="0.9"/>
    <circle cx="33" cy="25" r="2.5" fill="#42a5f5"/>
    <circle cx="49" cy="25" r="2.5" fill="#42a5f5"/>
    <rect x="29" y="38" width="22" height="4" rx="2" fill="white" opacity="0.7"/>
    <rect x="33" y="44" width="14" height="4" rx="2" fill="white" opacity="0.5"/>
    <rect x="10" y="34" width="10" height="20" rx="5" fill="#1976d2"/>
    <rect x="60" y="34" width="10" height="20" rx="5" fill="#1976d2"/>
    <rect x="25" y="60" width="10" height="16" rx="5" fill="#1976d2"/>
    <rect x="45" y="60" width="10" height="16" rx="5" fill="#1976d2"/>
  </svg>
  <div>
    <h1 style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:28px; color:#0f172a;">CalmConnect</h1>
    <p style="margin:0; opacity:0.8; font-size:14px; color:#475569;">Hello <b>""" + st.session_state.user_name + """</b> 👋 — you are not alone. I'm here for you.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- QUESTIONNAIRE ----
if st.session_state.show_questionnaire:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Mental Health Check-In</div>', unsafe_allow_html=True)

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        st.markdown("**😰 Stress Level** (0 = none, 10 = extreme)")
        stress = st.slider("Stress", 0, 10, 5, key="stress_slider")
    with col_q2:
        st.markdown("**😟 Anxiety Level** (0 = calm, 10 = severe)")
        anxiety = st.slider("Anxiety", 0, 10, 5, key="anxiety_slider")
    with col_q3:
        st.markdown("**😴 Sleep Quality** (0 = awful, 10 = great)")
        sleep = st.slider("Sleep", 0, 10, 7, key="sleep_slider")

    if st.button("📊 See My Results"):
        st.session_state.stress_score = stress
        st.session_state.anxiety_level = anxiety
        st.session_state.sleep_quality = sleep
        st.session_state.show_results = True

    if st.session_state.show_results:
        st.markdown("---")
        def badge(val, low=3, high=6, invert=False):
            if invert:
                cls = "score-high" if val<=low else "score-mid" if val<=high else "score-low"
            else:
                cls = "score-low" if val<=low else "score-mid" if val<=high else "score-high"
            return f'<span class="score-badge {cls}">{val}/10</span>'

        st.markdown(f"""
        <div style="display:flex; gap:20px; flex-wrap:wrap; margin-top:8px;">
          <div><b>Stress</b><br>{badge(st.session_state.stress_score)}</div>
          <div><b>Anxiety</b><br>{badge(st.session_state.anxiety_level)}</div>
          <div><b>Sleep</b><br>{badge(st.session_state.sleep_quality, invert=True)}</div>
        </div>
        """, unsafe_allow_html=True)

        tips = []
        if st.session_state.stress_score >= 7: tips.append("🔴 High stress detected — try the breathing exercise below.")
        elif st.session_state.stress_score >= 4: tips.append("🟡 Moderate stress — regular breaks and movement help.")
        else: tips.append("🟢 Stress levels look manageable. Keep it up!")

        if st.session_state.anxiety_level >= 7: tips.append("🔴 Significant anxiety — grounding exercises help.")
        elif st.session_state.anxiety_level >= 4: tips.append("🟡 Some anxiety present — mindful breathing is a great start.")
        else: tips.append("🟢 Anxiety seems low. Great!")

        if st.session_state.sleep_quality <= 4: tips.append("🔴 Poor sleep can amplify stress. Try the meditation timer tonight.")
        elif st.session_state.sleep_quality <= 6: tips.append("🟡 Sleep could improve — avoid screens 1hr before bed.")
        else: tips.append("🟢 Good sleep quality. Keep prioritizing rest!")

        for tip in tips:
            st.markdown(f"<div style='margin-top:6px; font-size:13px; color:#334155;'>{tip}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- WELLNESS PANEL ----
if st.session_state.show_wellness:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌿 Wellness Tools</div>', unsafe_allow_html=True)

    wtab1, wtab2, wtab3, wtab4 = st.tabs(["🌬️ Breathing", "🧘 Meditation", "🎵 Calm Music", "✨ Affirmations"])

    with wtab1:
        st.markdown("""
        <div style="text-align:center; padding: 20px 0;">
          <div class="breath-circle">Breathe in...<br>hold...<br>breathe out</div>
          <p style="margin-top:20px; opacity:0.8; font-size:13px; color:#334155;">
            4 sec inhale → 4 sec hold → 4 sec exhale → 4 sec hold<br>
            <b>Box Breathing</b> — used to reduce stress instantly.
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 Tip: Follow the circle. Inhale as it expands, exhale as it contracts. Repeat for 2–5 minutes.")

    with wtab2:
        med_options = {"1 min": 60, "3 min": 180, "5 min": 300, "10 min": 600}
        chosen = st.radio("Session length", list(med_options.keys()), horizontal=True)
        total = med_options[chosen]

        col_m1, col_m2, col_m3 = st.columns([1,2,1])
        with col_m2:
            if not st.session_state.meditation_running:
                if st.button("▶ Start Meditation"):
                    st.session_state.meditation_running = True
                    st.session_state.meditation_seconds = 0
                    st.session_state.meditation_total = total
                    st.rerun()
            else:
                pct = int((st.session_state.meditation_seconds / st.session_state.meditation_total) * 100)
                remaining = st.session_state.meditation_total - st.session_state.meditation_seconds
                mins, secs = divmod(remaining, 60)
                st.markdown(f"""
                <div class="med-ring" style="--pct:{pct}">
                  <div class="med-ring-inner">{mins:02d}:{secs:02d}</div>
                </div>
                <p style="text-align:center; opacity:0.8; font-size:13px; color:#334155;">Focus on your breath. Let thoughts pass like clouds. 🌤️</p>
                """, unsafe_allow_html=True)

                if st.button("⏹ Stop"):
                    st.session_state.meditation_running = False
                    st.rerun()

                if st.session_state.meditation_seconds < st.session_state.meditation_total:
                    time.sleep(1)
                    st.session_state.meditation_seconds += 1
                    st.rerun()
                else:
                    st.session_state.meditation_running = False
                    st.success("🎉 Session complete! Well done.")

    with wtab3:
        st.markdown("#### 🎵 Calm Music Playlists")
        music = [
            ("🌊 Ocean Waves", "https://www.youtube.com/results?search_query=ocean+waves+relaxing+music"),
            ("🌧️ Rain Sounds", "https://www.youtube.com/results?search_query=rain+sounds+sleep"),
            ("🎹 Piano Calm", "https://www.youtube.com/results?search_query=calm+piano+meditation+music"),
            ("🔔 Tibetan Bowls", "https://www.youtube.com/results?search_query=tibetan+singing+bowls+meditation"),
            ("🌿 Nature Sounds", "https://www.youtube.com/results?search_query=nature+sounds+relaxation"),
            ("🎶 Lo-fi Chill", "https://www.youtube.com/results?search_query=lofi+chill+study+beats"),
        ]
        cols_m = st.columns(3)
        for i, (name, url) in enumerate(music):
            with cols_m[i % 3]:
                st.markdown(f"""
                <a href="{url}" target="_blank" style="
                    display:block; padding:14px; border-radius:12px;
                    background:#ffffff; border:1px solid #e2e8f0;
                    text-decoration:none; color:#334155;
                    text-align:center; margin-bottom:10px;
                    transition:0.2s; font-size:15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                " onmouseover="this.style.borderColor='#1976d2'" onmouseout="this.style.borderColor='#e2e8f0'">{name}</a>
                """, unsafe_allow_html=True)

    with wtab4:
        st.markdown("#### ✨ Positive Affirmations")
        for i, a in enumerate(AFFIRMATIONS):
            st.markdown(f"""
            <div style="
                padding:14px 18px; border-radius:12px;
                background:#ffffff; border:1px solid #e2e8f0;
                border-left: 4px solid #1976d2;
                margin-bottom:10px; font-size:14px; line-height:1.6;
                color:#334155;
                animation: msgSlide 0.3s ease {i*0.05}s both;
            ">{a}</div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- CONVERSATION RENDERING GENERATOR ----
def get_chat_html(history):
    html = ""
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("_ts", "")
        if role == "user":
            html += f"""
            <div class="msg-row user">
              <div class="avatar user-av">👤</div>
              <div class="bubble-wrap">
                <div class="user-msg">{content}</div>
                <div class="timestamp">{ts}</div>
              </div>
            </div>"""
        elif role == "assistant":
            html += f"""
            <div class="msg-row">
              <div class="avatar ai-av">🤖</div>
              <div class="bubble-wrap">
                <div class="ai-msg">{content}</div>
                <div class="timestamp">{ts}</div>
              </div>
            </div>"""
    if not html:
        html = """
        <div style="text-align:center; opacity:0.4; padding: 60px 20px; font-size:14px; color:#64748b;">
          <div style="font-size:48px; margin-bottom:12px;">🧠</div>
          Start the conversation — I'm here to listen.
        </div>"""
    return html

# ---- RESPONSE MANAGER (UPDATED FOR GOOGLE GEMINI API) ----
def generate_response(user_input, chat_container):
    now = datetime.datetime.now().strftime("%H:%M")
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input,
        "_ts": now
    })

    past_html = get_chat_html(st.session_state.conversation_history)
    typing_dots = """
    <div class="msg-row">
      <div class="avatar ai-av">🤖</div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
    """
    chat_container.markdown(f'<div class="response-box" id="chat-box">{past_html + typing_dots}</div>', unsafe_allow_html=True)

    if client is None:
        ai_response = "⚠️ Gemini client is missing. Please map `GEMINI_API_KEY` inside your Streamlit secrets setup."
    else:
        try:
            # Map history into Gemini SDK structured Content format
            gemini_contents = []
            for m in st.session_state.conversation_history:
                # Convert 'assistant' naming convention to Gemini standard 'model'
                gemini_role = "model" if m["role"] == "assistant" else "user"
                gemini_contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                )

            # Generate response via the native Google genai SDK wrapper
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction="You are CalmConnect AI, a compassionate, supportive, and active-listening mental health companion. Provide concise, warm, and highly empathetic responses."
                )
            )
            ai_response = response.text
        except Exception as e:
            ai_response = f"⚠️ Could not connect to Gemini Cloud API. Error details: {str(e)}"

    ai_ts = datetime.datetime.now().strftime("%H:%M")
    
    # Word-by-word streaming rendering interface simulation
    displayed = ""
    for word in ai_response.split():
        displayed += word + " "
        live_ai_msg = f"""
        <div class="msg-row">
          <div class="avatar ai-av">🤖</div>
          <div class="bubble-wrap">
            <div class="ai-msg">{displayed}</div>
            <div class="timestamp">{ai_ts}</div>
          </div>
        </div>
        """
        chat_container.markdown(f'<div class="response-box" id="chat-box">{past_html + live_ai_msg}</div>', unsafe_allow_html=True)
        time.sleep(0.02)

    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": ai_response,
        "_ts": ai_ts
    })

# ---------------- APPLICATION LAYOUT ----------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-title">📝 Your Message</div>', unsafe_allow_html=True)
    user_input = st.text_area("", height=320,
        placeholder="Share what's on your mind... I'm here to listen. 💬",
        key="chat_input")

    st.markdown('<div class="send-btn-container">', unsafe_allow_html=True)
    send = st.button("➤")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">🤖 CalmConnect AI</div>', unsafe_allow_html=True)
    
    chat_box_slot = st.empty()
    initial_html = get_chat_html(st.session_state.conversation_history)
    chat_box_slot.markdown(f'<div class="response-box" id="chat-box">{initial_html}</div>', unsafe_allow_html=True)

    # Persistent dynamic autoscroll script
    st.markdown("""
    <script>
    (function scroll() {
        var el = window.parent.document.getElementById('chat-box');
        if (el) el.scrollTop = el.scrollHeight;
        setTimeout(scroll, 800);
    })();
    </script>
    """, unsafe_allow_html=True)

# ---- HANDLER FOR TRANSMISSION ----
if send and user_input.strip():
    generate_response(user_input, chat_box_slot)
    st.rerun()
