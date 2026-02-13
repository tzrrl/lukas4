import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURATION ---
MODEL_NAME = 'gemini-2.0-flash' 

if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key fehlt!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="Kita-Simulator: Lukas", page_icon="🧒")

# --- CSS FÜR GRÜNE AKZENTE ---
st.markdown("""
    <style>
    .stSuccess { background-color: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
    .sst-dots { font-size: 20px; color: #4caf50; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALISIERUNG ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Guck mal, was ich hier mache..."}]
if "sst_counter" not in st.session_state:
    st.session_state.sst_counter = 0
if "patience" not in st.session_state:
    st.session_state.patience = 6 
if "solved" not in st.session_state:
    st.session_state.solved = False

# --- 3. UI LAYOUT ---
st.title("Lukas (4 J.)")

# Fortschrittsanzeige (Scrollt normal mit)
display_dots = min(st.session_state.sst_counter, 5)
progress_dots = "🟢" * display_dots + "⚪" * (5 - display_dots)
st.markdown(f"<div class='sst-dots'>Dialog-Fortschritt: {progress_dots}</div>", unsafe_allow_html=True)

# Erfolgskasten
if st.session_state.sst_counter >= 5:
    st.session_state.solved = True
    st.success("""
    ### 🎉 Ziel erreicht! 
    **Dein Codewort für das Handout:** # GEMEINSAM-DENKEN
    """)
    if st.button("Simulation neu starten"):
        st.session_state.clear()
        st.rerun()

# HILFE-BOX
if st.session_state.patience <= 0 and not st.session_state.solved:
    st.info("**💡 Tipp:** Lukas braucht offene Impulse statt Fragen!")

# Chat-Verlauf
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. LOGIK ---
if not st.session_state.solved:
    if prompt := st.chat_input("Was sagst du zu Lukas?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        system_prompt = f"""
        Du bist Lukas (4 J.). Turm-Spiel.
        STAND: {st.session_state.sst_counter}/4. GEDULD: {st.session_state.patience}.
        REGELN:
        1. Bei geschlossenen Fragen: '[PATIENCE-DOWN]'.
        2. Bei SST-Impulsen: '[SST-UP]' & '[PATIENCE-RESET]'.
        3. Beende bei 4 Punkten das Gespräch nett.
        """

        with st.spinner("Lukas überlegt..."):
            try:
                response = model.generate_content(system_prompt + "\nUser: " + prompt)
                text = response.text
                
                if "[PATIENCE-DOWN]" in text:
                    st.session_state.patience -= 1
                    text = text.replace("[PATIENCE-DOWN]", "").strip()
                if "[PATIENCE-RESET]" in text:
                    st.session_state.patience = 6 
                    text = text.replace("[PATIENCE-RESET]", "").strip()
                if "[SST-UP]" in text:
                    st.session_state.sst_counter += 1
                    text = text.replace("[SST-UP]", "").strip()

                st.session_state.messages.append({"role": "assistant", "content": text})
                st.rerun()
            except Exception:
                st.warning("Kurze Pause...")

if st.sidebar.button("Hard Reset"):
    st.session_state.clear()
    st.rerun()

