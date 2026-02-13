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

# --- 2. INITIALISIERUNG ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Guck mal, was ich hier mache..."}]
if "sst_counter" not in st.session_state:
    st.session_state.sst_counter = 0
if "patience" not in st.session_state:
    st.session_state.patience = 6 # Erhöht auf 6 Fehlversuche
if "solved" not in st.session_state:
    st.session_state.solved = False

# --- 3. UI LAYOUT ---
st.title("Kita-Simulator: Lukas (4 J.)")

# Fortschrittsanzeige
if not st.session_state.solved:
    progress_dots = "🔵" * st.session_state.sst_counter + "⚪" * (4 - st.session_state.sst_counter)
    st.markdown(f"**Dein Dialog-Fortschritt:** {progress_dots}")
else:
    st.success("🎉 Ziel erreicht! Das Codewort wurde gefunden.")

# HILFE-BOX: Erscheint erst nach 6 Fehlversuchen
if st.session_state.patience <= 0 and not st.session_state.solved:
    st.info("""
    **💡 Pädagogischer Tipp:** Lukas blockt ab. Er fühlt sich durch zu viele Fragen "geprüft".
    Versuche es mit **Sustained Shared Thinking (SST)**. Nutze offene Impulse statt Fragen: 
    * *"Ich frage mich, ob dein Turm auch einen Geheimgang hat..."* * *"Erzähl mal, wie du das gebaut hast..."*
    """)

# Chat-Verlauf
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. LOGIK ---
if prompt := st.chat_input("Was sagst du zu Lukas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = f"""
    Du bist Lukas (4 Jahre). Du baust ein Turm-Haus aus Holzklötzen.
    STAND: {st.session_state.sst_counter}/4 SST-Punkte.
    GEDULD: {st.session_state.patience}.

    REGELN:
    1. Reagiere wie ein Kind. Wenn Geduld <= 0, sei genervt und einsilbig.
    2. Wenn der User GESCHLOSSENE FRAGEN stellt (Abfragen): Antworte kurz. Schreibe '[PATIENCE-DOWN]'.
    3. Wenn der User OFFENE SST-IMPULSE gibt (Mitdenken): Sei begeistert. Schreibe '[SST-UP]' und '[PATIENCE-RESET]'.
    4. Bei 4 SST-Punkten gib das Codewort: GEMEINSAM-DENKEN.
    """

    if not st.session_state.solved:
        with st.spinner("Lukas spielt..."):
            try:
                response = model.generate_content(system_prompt + "\nUser: " + prompt)
                text = response.text

                if "[PATIENCE-DOWN]" in text:
                    st.session_state.patience -= 1
                    text = text.replace("[PATIENCE-DOWN]", "").strip()
                if "[PATIENCE-RESET]" in text:
                    st.session_state.patience = 6 # Reset auf den neuen Startwert
                    text = text.replace("[PATIENCE-RESET]", "").strip()
                if "[SST-UP]" in text:
                    st.session_state.sst_counter += 1
                    text = text.replace("[SST-UP]", "").strip()

                if "GEMEINSAM-DENKEN" in text:
                    st.session_state.solved = True

                st.session_state.messages.append({"role": "assistant", "content": text})
                st.rerun()
            except Exception:
                st.warning("Kurze Pause nötig. Gleich nochmal versuchen!")

if st.sidebar.button("Simulation neu starten"):
    st.session_state.clear()
    st.rerun()
