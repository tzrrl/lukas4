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

# --- CSS FÜR GRÜNE FARBEN ---
st.markdown("""
    <style>
    .stSuccess { background-color: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
    .sst-dots { font-size: 24px; color: #4caf50; margin-bottom: 10px; }
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
st.title("Kita-Simulator: Lukas (4 J.)")

# DER "BOMBENSICHERE" CHECK: Wenn 4 Punkte erreicht sind, ist gelöst!
if st.session_state.sst_counter >= 4:
    st.session_state.solved = True

# Erfolgskasten anzeigen
if st.session_state.solved:
    st.success("""
    ### 🎉 Ziel erreicht! 
    Du hast Lukas erfolgreich in einen tiefen Dialog verwickelt. Durch deine offenen Impulse konntet ihr **gemeinsam nachdenken (SST)**. 
    
    **Dein Codewort für das Handout:** # GEMEINSAM-DENKEN
    """)
    if st.button("Nochmal spielen"):
        st.session_state.clear()
        st.rerun()
else:
    # Fortschrittsanzeige während des Spiels
    progress_dots = "🟢" * st.session_state.sst_counter + "⚪" * (4 - st.session_state.sst_counter)
    st.markdown(f"<div class='sst-dots'>Fortschritt: {progress_dots}</div>", unsafe_allow_html=True)

# HILFE-BOX
if st.session_state.patience <= 0 and not st.session_state.solved:
    st.info("**💡 Pädagogischer Tipp:** Lukas fühlt sich durch Fragen 'geprüft'. Versuche es mit einem Impuls wie: *'Ich frage mich, ob...' / 'Erzähl mal...'**")

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
        Du bist Lukas (4 Jahre). Du baust ein Turm-Haus.
        STAND: {st.session_state.sst_counter}/4 SST-Punkte. GEDULD: {st.session_state.patience}.
        REGELN:
        1. Sei ein 4-jähriges Kind. Wenn Geduld <= 0, sei genervt.
        2. Bei GESCHLOSSENEN FRAGEN (Wissensabfrage): Antworte kurz. Schreibe '[PATIENCE-DOWN]'.
        3. Bei OFFENEN SST-IMPULSEN (Mitdenken): Sei begeistert. Schreibe '[SST-UP]' und '[PATIENCE-RESET]'.
        4. Sobald der 4. Punkt erreicht ist (COUNTER=4), verabschiede dich nett, weil dein Turm fertig ist.
        """

        with st.spinner("Lukas spielt..."):
            try:
                response = model.generate_content(system_prompt + "\nUser: " + prompt)
                text = response.text
                
                # Logik-Tags auswerten
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
                st.warning("Lukas macht kurz Pause. Bitte gleich nochmal senden.")

if st.sidebar.button("Simulation zurücksetzen"):
    st.session_state.clear()
    st.rerun()
