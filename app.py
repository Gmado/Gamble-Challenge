import streamlit as st

st.set_page_config(page_title="Gaming Challenge - Live Wettbüro", page_icon="🎮", layout="centered")

# --- GLOBALER SPEICHER (FÜR ALLE NUTZER SYNCHRONISIERT) ---
@st.cache_resource
def get_global_state():
    return {
        "lobby_active": False,
        "points": {"Team 1": 7, "Team 2": 7, "Team 3": 7},
        "wetten": {"Team 1": None, "Team 2": None, "Team 3": None},
        "taken_teams": {"Team 1": None, "Team 2": None, "Team 3": None}
    }

global_state = get_global_state()

# --- LOBBY LOGIK ---
st.title("🎮 Das ultimative Live-Wettbüro")

# Fall 1: Keine Lobby aktiv
if not global_state["lobby_active"]:
    st.info("Aktuell ist keine Lobby aktiv. Warte darauf, dass der Host die Runde startet.")
    
    with st.expander("🔑 Admin: Lobby erstellen"):
        pw = st.text_input("Admin-Passwort:", type="password")
        if st.button("Lobby starten 🚀"):
            if pw == "Gamba07":
                global_state["lobby_active"] = True
                st.session_state["is_admin"] = True
                st.success("Lobby erfolgreich erstellt!")
                st.rerun()
            else:
                st.error("Falsches Passwort!")

# Fall 2: Lobby ist aktiv
else:
    # Admin-Ansicht erzwingen, falls man der Ersteller ist
    if st.session_state.get("is_admin", False):
        st.subheader("🔑 Admin-Panel (Spielleiter)")
        st.write("Du bist der Host dieser Lobby.")
        
        # Übersicht der verbundenen Gambler und Wetten
        st.write("---")
        st.write("**Aktueller Status der Teams:**")
        for team in ["Team 1", "Team 2", "Team 3"]:
            user = global_state["taken_teams"][team]
            wette = global_state["wetten"][team]
            
            user_text = f"👤 Spieler: **{user}**" if user else "❌ *Noch nicht beigetreten*"
            wette_text = f" | 🎲 Wette: {wette['einsatz']} Pkt. auf Platz {wette['tipp']}" if wette else " | ⏳ *Wartet auf Wette*"
            
            st.write(f"- **{team}** ({global_state['points'][team]} Pkt.): {user_text}{wette_text}")
            
        st.write("---")
        st.write("**Ergebnisse für diese Runde eintragen:**")
        res_t1 = st.selectbox("Platzierung für Team 1:", [1, 2, 3], index=0)
        res_t2 = st.selectbox("Platzierung für Team 2:", [1, 2, 3], index=1)
        res_t3 = st.selectbox("Platzierung für Team 3:", [1, 2, 3], index=2)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Runde auswerten & Punkte berechnen 📊", use_container_width=True):
                results = {"Team 1": res_t1, "Team 2": res_t2, "Team 3": res_t3}
                for t in ["Team 1", "Team 2", "Team 3"]:
                    w = global_state["wetten"][t]
                    if w:
                        if w['tipp'] == results[t]:
                            global_state["points"][t] += w['einsatz']
                        else:
                            global_state["points"][t] -= w['einsatz']
                    # Wette zurücksetzen für die nächste Runde
                    global_state["wetten"][t] = None
                st.success("Punkte wurden aktualisiert!")
                st.rerun()
                
        with col2:
            if st.button("Lobby komplett schließen 🛑", use_container_width=True):
                # Alles auf Anfang setzen
                global_state["lobby_active"] = False
                global_state["points"] = {"Team 1": 7, "Team 2": 7, "Team 3": 7}
                global_state["wetten"] = {"Team 1": None, "Team 2": None, "Team 3": None}
                global_state["taken_teams"] = {"Team 1": None, "Team 2": None, "Team 3": None}
                st.session_state["is_admin"] = False
                st.rerun()

    # Spieler-Ansicht (Gambler)
    else:
        # Prüfen, ob dieser Browser sich schon eingeloggt hat
        if "my_team" not in st.session_state:
            st.subheader("Tritt der Lobby bei")
            name = st.text_input("Dein Name:")
            
            # Nur verfügbare Teams anzeigen
            verfuegbare_teams = [t for t, user in global_state["taken_teams"].items() if user is None]
            
            if not verfuegbare_teams:
                st.warning("Alle Teams sind bereits besetzt!")
            else:
                team_wahl = st.selectbox("Wähle dein Team:", verfuegbare_teams)
                
                if st.button("Lobby beitreten 🚪"):
                    if name.strip() == "":
                        st.error("Bitte gib einen Namen ein!")
                    else:
                        # Team im globalen Speicher reservieren
                        global_state["taken_teams"][team_wahl] = name
                        # Im Browser des Users merken, wer er ist
                        st.session_state["my_team"] = team_wahl
                        st.session_state["my_name"] = name
                        st.rerun()
        else:
            # Der Gambler ist eingeloggt und sieht sein Dashboard
            mein_team = st.session_state["my_team"]
            mein_name = st.session_state["my_name"]
            aktuelle_punkte = global_state["points"][mein_team]
            
            st.subheader(f"Dashboard von {mein_name} ({mein_team})")
            st.metric(label="Dein Kontostand", value=f"{aktuelle_punkte} Punkte")
            
            if aktuelle_punkte <= 0:
                st.error("Du bist leider pleite und kannst diese Runde nicht wetten!")
            else:
                aktuelle_wette = global_state["wetten"][mein_team]
                
                if aktuelle_wette is not None:
                    st.info(f"Deine Wette steht: Du hast {aktuelle_wette['einsatz']} Punkte auf Platz {aktuelle_wette['tipp']} gesetzt. Warte auf die Auswertung durch den Host...")
                else:
                    with st.form("wette_abgeben"):
                        einsatz = st.number_input("Dein Wetteinsatz:", min_value=1, max_value=aktuelle_punkte, step=1)
                        tipp = st.radio("Auf welchem Platz landet dein Partner?", [1, 2, 3], horizontal=True)
                        submit = st.form_submit_button("Wette einloggen 🔒")
                        
                        if submit:
                            global_state["wetten"][mein_team] = {"einsatz": einsatz, "tipp": tipp}
                            st.success("Wette erfolgreich abgegeben!")
                            st.rerun()
            
            # Kleiner Button zum manuellen Aktualisieren für die Spieler
            if st.button("🔄 Seite aktualisieren (Punkte prüfen)"):
                st.rerun()