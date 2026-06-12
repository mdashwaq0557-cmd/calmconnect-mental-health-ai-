
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
    "dark_mode": True,
    "theme": "neon",
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

# ---------------- THEMES ----------------
THEMES = {
    "neon": {
        "bg": "linear-gradient(-45deg,#0f0c29,#302b63,#24243e,#0f0c29)",
        "accent": "#00f5ff",
        "accent2": "#7b2ff7",
        "card": "rgba(255,255,255,0.07)",
        "user_bubble": "linear-gradient(135deg,#00f5ff,#7b2ff7)",
        "ai_bubble": "rgba(123,47,247,0.25)",
        "text": "#e0e0ff",
        "glow": "0 0 20px rgba(0,245,255,0.4)",
    },
    "calm_blue": {
        "bg": "linear-gradient(-45deg,#0a1628,#1a3a5c,#0d2137,#0a1628)",
        "accent": "#4fc3f7",
        "accent2": "#81d4fa",
        "card": "rgba(79,195,247,0.08)",
        "user_bubble": "linear-gradient(135deg,#4fc3f7,#0288d1)",
        "ai_bubble": "rgba(79,195,247,0.15)",
        "text": "#e1f5fe",
        "glow": "0 0 20px rgba(79,195,247,0.3)",
    },
    "light": {
        "bg": "linear-gradient(-45deg,#e8f4fd,#f0f7ff,#e3f2fd,#f5f9ff)",
        "accent": "#1976d2",
        "accent2": "#42a5f5",
        "card": "rgba(25,118,210,0.06)",
        "user_bubble": "linear-gradient(135deg,#1976d2,#42a5f5)",
        "ai_bubble": "rgba(25,118,210,0.1)",
        "text": "#1a237e",
        "glow": "0 4px 15px rgba(25,118,210,0.2)",
    },
}

T = THEMES[st.session_state.theme]

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings & Tools")
st.session_state.user_name = st.sidebar.text_input("Your name", value=st.session_state.user_name)

st.sidebar.markdown("### 🎨 Theme")
theme_choice = st.sidebar.radio("", ["neon", "calm_blue", "light"],
    format_func=lambda x: {"neon":"🌌 Neon Dark","calm_blue":"🌊 Calm Blue","light":"☀️ Light"}[x],
    index=["neon","calm_blue","light"].index(st.session_state.theme))
if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.conversation_history = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧘 Wellness Tools")
if st.sidebar.button("📋 Mental Health Check-In"):
    st.session_state.show_questionnaire = not st.session_state.show_questionnaire
    st.session_state.show_wellness = False
    st.rerun()
if st.sidebar.button("🌿 Wellness & Exercises"):
    st.session_state.show_wellness = not st.session_state.show_wellness
    st.session_state.show_questionnaire = False
    st.rerun()

st.sidebar.markdown("---")
aff_idx = st.session_state.affirmation_index % len(AFFIRMATIONS)
st.sidebar.markdown(f"### 💬 Daily Affirmation")
st.sidebar.info(AFFIRMATIONS[aff_idx])
if st.sidebar.button("🔄 Next Affirmation"):
    st.session_state.affirmation_index += 1
    st.rerun()

# ---------------- CSS ----------------
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600&family=Space+Grotesk:wght=400;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

.block-container {{ padding-top: 1.5rem !important; max-width: 1400px; }}

.stApp {{
    background: {T['bg']} !important;
    background-size: 400% 400% !important;
    animation: gradientMove 18s ease infinite !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif;
}}

@keyframes gradientMove {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* ---- Animated robot background ---- */
.robot-bg {{
    position: fixed;
    bottom: -20px;
    right: -20px;
    width: 320px;
    height: 320px;
    opacity: 0.06;
    z-index: 0;
    pointer-events: none;
    animation: robotFloat 6s ease-in-out infinite;
}}
@keyframes robotFloat {{
    0%, 100% {{ transform: translateY(0px) rotate(-3deg); }}
    50%       {{ transform: translateY(-18px) rotate(3deg); }}
}}

/* ---- Mascot ---- */
.mascot-wrap {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
}}
.mascot-svg {{
    width: 64px;
    height: 64px;
    animation: mascotBob 3s ease-in-out infinite;
    filter: drop-shadow({T['glow']});
}}
@keyframes mascotBob {{
    0%, 100% {{ transform: translateY(0); }}
    50%       {{ transform: translateY(-6px); }}
}}

/* ---- Typing dots ---- */
.typing-dots {{ display: inline-flex; gap: 5px; align-items: center; padding: 12px 18px; }}
.typing-dots span {{
    width: 9px; height: 9px;
    background: {T['accent']};
    border-radius: 50%;
    display: inline-block;
    animation: dotBounce 1.2s infinite ease-in-out;
}}
.typing-dots span:nth-child(1) {{ animation-delay: 0s; }}
.typing-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
.typing-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes dotBounce {{
    0%, 80%, 100% {{ transform: scale(0.7); opacity: 0.4; }}
    40%            {{ transform: scale(1.2); opacity: 1; }}
}}

/* ---- Message bubbles ---- */
.msg-row {{ display: flex; align-items: flex-end; gap: 10px; margin-bottom: 14px; animation: msgSlide 0.35s ease; }}
.msg-row.user {{ flex-direction: row-reverse; }}
@keyframes msgSlide {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.avatar {{
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}}
.avatar.user-av {{ background: {T['user_bubble']}; }}
.avatar.ai-av   {{ background: {T['ai_bubble']}; border: 1px solid {T['accent']}44; }}

.bubble-wrap {{ max-width: 74%; }}
.timestamp {{
    font-size: 10px;
    opacity: 0.5;
    margin-top: 3px;
    padding: 0 6px;
    font-family: 'Inter', sans-serif;
}}
.msg-row.user .timestamp {{ text-align: right; }}

.user-msg {{
    background: {T['user_bubble']};
    color: white;
    padding: 11px 16px;
    border-radius: 18px 18px 4px 18px;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: {T['glow']};
    word-break: break-word;
}}
.ai-msg {{
    background: {T['ai_bubble']};
    border: 1px solid {T['accent']}33;
    padding: 11px 16px;
    border-radius: 18px 18px 18px 4px;
    font-size: 14px;
    line-height: 1.5;
    backdrop-filter: blur(8px);
    word-break: break-word;
    color: {T['text']};
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}}

/* ---- Response box ---- */
.response-box {{
    height: 62vh;
    overflow-y: auto;
    padding: 14px;
    border-radius: 16px;
    background: {T['card']};
    backdrop-filter: blur(10px);
    border: 1px solid {T['accent']}22;
    box-shadow: inset 0 0 30px rgba(0,0,0,0.1);
}}
.response-box::-webkit-scrollbar {{ width: 5px; }}
.response-box::-webkit-scrollbar-thumb {{ background: {T['accent']}55; border-radius: 10px; }}

/* ---- Cards ---- */
.card {{
    background: {T['card']};
    border: 1px solid {T['accent']}33;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(8px);
    transition: transform 0.2s, box-shadow 0.2s;
}}
.card:hover {{ transform: translateY(-2px); box-shadow: {T['glow']}; }}

.section-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: {T['accent']};
    margin-bottom: 12px;
    text-shadow: 0 0 12px {T['accent']}66;
}}

/* ---- Send button ---- */
.stButton > button {{
    border-radius: 50% !important;
    height: 52px !important;
    width: 52px !important;
    font-size: 20px !important;
    background: linear-gradient(45deg, {T['accent']}, {T['accent2']}) !important;
    color: white !important;
    border: none !important;
    box-shadow: {T['glow']} !important;
    transition: 0.25s !important;
}}
.stButton > button:hover {{
    transform: scale(1.12) !important;
    box-shadow: 0 0 28px {T['accent']} !important;
}}

/* ---- Progress / sliders ---- */
.stSlider > div > div {{ accent-color: {T['accent']}; }}

/* ---- Score badges ---- */
.score-badge {{
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 13px;
    margin: 4px;
}}
.score-low  {{ background: rgba(0,200,100,0.2); color: #00c864; border: 1px solid #00c864; }}
.score-mid  {{ background: rgba(255,193,7,0.2);  color: #ffc107; border: 1px solid #ffc107; }}
.score-high {{ background: rgba(255,75,75,0.2);  color: #ff4b4b; border: 1px solid #ff4b4b; }}

/* ---- Meditation ring ---- */
.med-ring {{
    width: 140px; height: 140px;
    border-radius: 50%;
    background: conic-gradient({T['accent']} calc(var(--pct) * 3.6deg), {T['card']} 0deg);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px;
    box-shadow: {T['glow']};
    animation: ringPulse 2s ease-in-out infinite;
    position: relative;
}}
.med-ring-inner {{
    width: 110px; height: 110px;
    border-radius: 50%;
    background: {T['bg']};
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    font-weight: 700;
    color: {T['accent']};
    font-family: 'Space Grotesk', sans-serif;
}}
@keyframes ringPulse {{
    0%, 100% {{ box-shadow: {T['glow']}; }}
    50%       {{ box-shadow: 0 0 40px {T['accent']}88; }}
}}

/* ---- Breathing circle ---- */
.breath-circle {{
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, {T['accent']}44, {T['accent2']}22);
    border: 3px solid {T['accent']};
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto;
    animation: breathe 8s ease-in-out infinite;
    color: {T['text']};
    font-size: 13px;
    font-weight: 500;
    text-align: center;
    padding: 10px;
}}
@keyframes breathe {{
    0%,  100% {{ transform: scale(1);   opacity: 0.7; }}
    37.5%     {{ transform: scale(1.4); opacity: 1;   }}
    62.5%     {{ transform: scale(1.4); opacity: 1;   }}
}}

/* Misc */
footer {{ visibility: hidden; }}
h1, h2, h3 {{ color: {T['text']} !important; }}
.stTextArea textarea {{ background: {T['card']} !important; color: {T['text']} !important; border: 1px solid {T['accent']}44 !important; border-radius: 12px !important; }}
.stTextArea textarea:focus {{ border-color: {T['accent']} !important; box-shadow: {T['glow']} !important; }}
label {{ color: {T['text']} !important; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---- Animated background robot ----
st.markdown("""
<svg class="robot-bg" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="60" y="70" width="80" height="70" rx="14" fill="white"/>
  <rect x="75" y="50" width="50" height="28" rx="10" fill="white"/>
  <line x1="100" y1="50" x2="100" y2="40" stroke="white" stroke-width="4"/>
  <circle cx="100" cy="34" r="6" fill="white"/>
  <circle cx="86" cy="62" r="7" fill="#aaa"/>
  <circle cx="114" cy="62" r="7" fill="#aaa"/>
  <circle cx="86" cy="62" r="4" fill="white" opacity="0.8"/>
  <circle cx="114" cy="62" r="4" fill="white" opacity="0.8"/>
  <rect x="80" y="88" width="40" height="6" rx="3" fill="#aaa"/>
  <rect x="85" y="100" width="30" height="6" rx="3" fill="#aaa"/>
  <rect x="44" y="80" width="16" height="40" rx="8" fill="white"/>
  <rect x="140" y="80" width="16" height="40" rx="8" fill="white"/>
  <rect x="72" y="140" width="18" height="35" rx="9" fill="white"/>
  <rect x="110" y="140" width="18" height="35" rx="9" fill="white"/>
</svg>
""", unsafe_allow_html=True)

# ---- Mascot + header ----
mascot_color = T['accent']
mascot_color2 = T['accent2']
st.markdown(f"""
<div class="mascot-wrap">
  <svg class="mascot-svg" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="40" r="38" fill="{mascot_color2}33"/>
    <rect x="20" y="28" width="40" height="32" rx="10" fill="{mascot_color}"/>
    <rect x="27" y="18" width="26" height="16" rx="8" fill="{mascot_color}"/>
    <line x1="40" y1="18" x2="40" y2="11" stroke="{mascot_color}" stroke-width="3"/>
    <circle cx="40" cy="8" r="4" fill="{mascot_color2}"/>
    <circle cx="32" cy="25" r="5" fill="white" opacity="0.9"/>
    <circle cx="48" cy="25" r="5" fill="white" opacity="0.9"/>
    <circle cx="33" cy="25" r="2.5" fill="{mascot_color2}"/>
    <circle cx="49" cy="25" r="2.5" fill="{mascot_color2}"/>
    <rect x="29" y="38" width="22" height="4" rx="2" fill="white" opacity="0.7"/>
    <rect x="33" y="44" width="14" height="4" rx="2" fill="white" opacity="0.5"/>
    <rect x="10" y="34" width="10" height="20" rx="5" fill="{mascot_color}"/>
    <rect x="60" y="34" width="10" height="20" rx="5" fill="{mascot_color}"/>
    <rect x="25" y="60" width="10" height="16" rx="5" fill="{mascot_color}"/>
    <rect x="45" y="60" width="10" height="16" rx="5" fill="{mascot_color}"/>
  </svg>
  <div>
    <h1 style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:28px; background:linear-gradient(90deg,{mascot_color},{mascot_color2}); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">CalmConnect</h1>
    <p style="margin:0; opacity:0.7; font-size:14px;">Hello <b>{st.session_state.user_name}</b> 👋 — you are not alone. I'm here for you.</p>
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
          <div><b>Stress</b><br>{badge(stress)}</div>
          <div><b>Anxiety</b><br>{badge(anxiety)}</div>
          <div><b>Sleep</b><br>{badge(sleep, invert=True)}</div>
        </div>
        """, unsafe_allow_html=True)

        tips = []
        if stress >= 7: tips.append("🔴 High stress detected — try the breathing exercise below.")
        elif stress >= 4: tips.append("🟡 Moderate stress — regular breaks and movement help.")
        else: tips.append("🟢 Stress levels look manageable. Keep it up!")

        if anxiety >= 7: tips.append("🔴 Significant anxiety — grounding exercises and talking to someone can help.")
        elif anxiety >= 4: tips.append("🟡 Some anxiety present — mindful breathing is a great start.")
        else: tips.append("🟢 Anxiety seems low. Great!")

        if sleep <= 4: tips.append("🔴 Poor sleep can amplify everything. Try the meditation timer tonight.")
        elif sleep <= 6: tips.append("🟡 Sleep could improve — avoid screens 1hr before bed.")
        else: tips.append("🟢 Good sleep quality. Sleep is the foundation of wellbeing!")

        for tip in tips:
            st.markdown(f"<div style='margin-top:6px; font-size:13px;'>{tip}</div>", unsafe_allow_html=True)

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
          <p style="margin-top:20px; opacity:0.7; font-size:13px;">
            4 sec inhale → 4 sec hold → 4 sec exhale → 4 sec hold<br>
            <b>Box Breathing</b> — used by Navy SEALs to reduce stress instantly.
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
                <p style="text-align:center; opacity:0.7; font-size:13px;">Focus on your breath. Let thoughts pass like clouds. 🌤️</p>
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
                    background:{T['card']}; border:1px solid {T['accent']}44;
                    text-decoration:none; color:{T['text']};
                    text-align:center; margin-bottom:10px;
                    transition:0.2s; font-size:15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                " onmouseover="this.style.boxShadow='{T['glow']}'" onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">{name}</a>
                """, unsafe_allow_html=True)

    with wtab4:
        st.markdown("#### ✨ Positive Affirmations")
        all_affs = AFFIRMATIONS
        for i, a in enumerate(all_affs):
            st.markdown(f"""
            <div style="
                padding:14px 18px; border-radius:12px;
                background:{T['card']}; border-left: 3px solid {T['accent']};
                margin-bottom:10px; font-size:14px; line-height:1.6;
                animation: msgSlide 0.3s ease {i*0.05}s both;
            ">{a}</div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- AI RESPONSE FUNCTION ----
def generate_response(user_input, response_placeholder):
    now = datetime.datetime.now().strftime("%H:%M")
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input,
        "_ts": now
    })

    # Show typing dots
    response_placeholder.markdown(f"""
    <div class="msg-row">
      <div class="avatar ai-av">🤖</div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
    """, unsafe_allow_html=True)

    # Prepare messages without internal metadata
    messages = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.conversation_history]
    
    try:
        response = ollama.chat(model="llama3.1:8b", messages=messages)
        ai_response = response['message']['content']
    except Exception as e:
        ai_response = f"⚠️ Could not connect to Ollama. Please ensure it's running with `ollama serve`. Error: {str(e)}"

    ai_ts = datetime.datetime.now().strftime("%H:%M")
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": ai_response,
        "_ts": ai_ts
    })

    # Animated word-by-word reveal
    displayed = ""
    for word in ai_response.split():
        displayed += word + " "
        response_placeholder.markdown(f"""
        <div class="msg-row">
          <div class="avatar ai-av">🤖</div>
          <div class="bubble-wrap">
            <div class="ai-msg">{displayed}</div>
            <div class="timestamp">{ai_ts}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.04)

# ---- MAIN CHAT LAYOUT ----
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown(f'<div class="section-title">📝 Your Message</div>', unsafe_allow_html=True)
    user_input = st.text_area("", height=320,
        placeholder="Share what's on your mind... I'm here to listen. 💬",
        key="chat_input")

    btn_col, _ = st.columns([1, 5])
    with btn_col:
        send = st.button("➤")

with col2:
    st.markdown(f'<div class="section-title">🤖 CalmConnect AI</div>', unsafe_allow_html=True)

    # Build full conversation HTML
    chat_html = ""
    for msg in st.session_state.conversation_history:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("_ts", "")
        if role == "user":
            chat_html += f"""
            <div class="msg-row user">
              <div class="avatar user-av">👤</div>
              <div class="bubble-wrap">
                <div class="user-msg">{content}</div>
                <div class="timestamp">{ts}</div>
              </div>
            </div>"""
        elif role == "assistant":
            chat_html += f"""
            <div class="msg-row">
              <div class="avatar ai-av">🤖</div>
              <div class="bubble-wrap">
                <div class="ai-msg">{content}</div>
                <div class="timestamp">{ts}</div>
              </div>
            </div>"""

    if not st.session_state.conversation_history:
        chat_html = f"""
        <div style="text-align:center; opacity:0.4; padding: 60px 20px; font-size:14px;">
          <div style="font-size:48px; margin-bottom:12px;">🧠</div>
          Start the conversation — I'm here for you.
        </div>"""

    response_slot = st.empty()

    st.markdown(f'<div class="response-box" id="chat-box">{chat_html}</div>', unsafe_allow_html=True)

    # Auto-scroll JS
    st.markdown("""
    <script>
    (function scroll() {
        var el = window.parent.document.getElementById('chat-box');
        if (el) el.scrollTop = el.scrollHeight;
        setTimeout(scroll, 800);
    })();
    </script>
    """, unsafe_allow_html=True)

# ---- SEND HANDLER ----
if send and user_input.strip():
    with st.spinner(""):
        # Temporary typing indicator in response slot
        response_slot.markdown(f"""
        <div class="msg-row">
          <div class="avatar ai-av">🤖</div>
          <div class="typing-dots"><span></span><span></span><span></span></div>
        </div>
        """, unsafe_allow_html=True)
        generate_response(user_input, response_slot)
    st.rerun()
