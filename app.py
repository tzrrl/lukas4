import streamlit as st
import google.generativeai as genai
import time

# --- 1. KONFIGURATION ---
# Wir nutzen ein stabiles Modell aus deiner Liste
MODEL_NAME = 'gemini-2.0-flash' 

if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key fehlt in den Secrets!")
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
    st.session_state.patience = 3 # Lukas verliert bei 0 die Geduld
if "solved" not in st.session_state:
    st.session_state.solved = False

# --- 3. UI ---
st.title("Lukas (4 J.)")
# Die Trainer-Übersicht wurde entfernt für maximale Immersion.

# Chat-Verlauf
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. LOGIK ---
if prompt := st.chat_input("Was sagst du zu Lukas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # System-Anweisungen inklusive Frust-Logik
    system_prompt = f"""
    Du bist Lukas (4). Du baust ein Turm-Haus.
    STATUS: Geduld={st.session_state.patience}, SST-Punkte={st.session_state.sst_counter}
    
    REGELN:
    1. Wenn Geduld <= 0: Antworte extrem bockig ("Lass mich!", "Ich spiel jetzt alleine."), bis der User einen echten SST-Impuls gibt.
    2. Geschlossene Fragen: Antworte kurz ("Ja", "Nein") -> Signalisiere das dem System mit '[PATIENCE-DOWN]'.
    3. SST-Impulse ("Ich frage mich..."): Sei begeistert -> Signalisiere '[SST-UP]' und '[PATIENCE-RESET]'.
    4. Bei 4 SST-Punkten gib das Codewort: GEMEINSAM-DENKEN.
    """

    if not st.session_state.solved:
        with st.spinner("Lukas spielt..."):
            try:
                response = model.generate_content(system_prompt + "\nUser: " + prompt)
                text = response.text

                # Logik-Auswertung
                if "[PATIENCE-DOWN]" in text:
                    st.session_state.patience -= 1
                    text = text.replace("[PATIENCE-DOWN]", "")
                if "[PATIENCE-RESET]" in text:
                    st.session_state.patience = 3
                    text = text.replace("[PATIENCE-RESET]", "")
                if "[SST-UP]" in text:
                    st.session_state.sst_counter += 1
                    text = text.replace("[SST-UP]", "")

                if "GEMEINSAM-DENKEN" in text:
                    st.session_state.solved = True

                st.session_state.messages.append({"role": "assistant", "content": text})
                st.rerun()

            except Exception as e:
                if "429" in str(e):
                    st.warning("Lukas braucht eine kurze Denkpause (API Limit). Bitte versuche es in 30 Sekunden nochmal.")
                else:
                    st.error(f"Lukas ist gerade abgelenkt: {e}")

# Reset-Funktion (versteckt ganz unten)
if st.sidebar.button("Simulation Neustarten"):
    st.session_state.clear()

    st.rerun()
