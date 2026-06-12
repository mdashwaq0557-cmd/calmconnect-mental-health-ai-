import streamlit as st
import ollama
import time
import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CalmConnect – Mental Health Support",
    page_icon="🧠",
    layout="wide",
)

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

/* ---- Animated robot background ---- */
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

/* ---- Mascot ---- */
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

/* ---- Typing dots ---- */
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

/* ---- Message bubbles ---- */
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

/* ---- Response box ---- */
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

/* ---- Cards ---- */
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

/* ---- Sidebar Buttons Text Fix ---- */
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
.st
