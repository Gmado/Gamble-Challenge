import streamlit as st

st.set_page_config(page_title="Gaming Challenge - Wettbüro", page_icon="🎮", layout="centered")

# Punkte und Wetten im Hintergrund speichern
for key in ['p1', 'p2', 'p3']:
    if key not in st.session_state: st.session_state[key] = 7
for key in ['w1', 'w2', 'w3']:
    if key not in st.session_state: st.session_state[key] = None

st.title("🎮 Das ultimative Wettbüro")
st.write("Wette auf deinen Teampartner und sammle Punkte!")

# Seitenbereiche über Tabs regeln
tab1, tab2 = st.tabs(["🎲 Wett-Bereich für Gambler", "🔑 Admin-Panel (Spielleiter)"])

with tab1:
    team = st.selectbox("Wer bist du?", ["Bitte auswählen...", "Team 1", "Team 2", "Team 3"])
    
    if team != "Bitte auswählen...":
        t_idx = "1" if team == "Team 1" else "2" if team == "Team 2" else "3"
        current_pts = st.session_state[f'p{t_idx}']
        
        st.metric(label=f"Dein Kontostand ({team})", value=f"{current_pts} Punkte")
        
        if current_pts <= 0:
            st.error("Du hast 0 Punkte und bist leider pleite! Du kannst diese Runde nicht wetten.")
        else:
            if st.session_state[f'w{t_idx}'] is not None:
                st.info(f"Deine Wette für diese Runde steht: {st.session_state[f'w{t_idx}']['einsatz']} Punkte auf Platz {st.session_state[f'w{t_idx}']['tipp']}.")
            
            with st.form(f"wette_form_{t_idx}"):
                einsatz = st.number_input("Dein Wetteinsatz:", min_value=1, max_value=current_pts, step=1, key=f"e_{t_idx}")
                tipp = st.radio("Auf welchem Platz landet dein Partner?", [1, 2, 3], horizontal=True, key=f"t_{t_idx}")
                submit = st.form_submit_button("Wette abschicken! 🚀")
                
                if submit:
                    st.session_state[f'w{t_idx}'] = {"einsatz": einsatz, "tipp": tipp}
                    st.success(f"Erfolgreich eingetragen! Du setzt {einsatz} Punkte auf Platz {tipp}.")
                    st.rerun()

with tab2:
    st.subheader("Ergebnisse der Challenge eintragen")
    st.write("*(Nur für den Hoster/Spielleiter sichtbar – nicht den Gamblern zeigen!)*")
    
    # Anzeige, wer was gewettet hat
    st.write("**Aktuelle Wetten der Teams:**")
    for i in ["1", "2", "3"]:
        w = st.session_state[f'w{i}']
        if w:
            st.write(f"- Team {i}: setzt {w['einsatz']} Pkt. auf Platz {w['tipp']}")
        else:
            st.write(f"- Team {i}: Hat noch nicht gewettet")
            
    st.write("---")
    
    # Platzierungen auswerten
    res_t1 = st.selectbox("Platzierung für Team 1:", [1, 2, 3], index=0)
    res_t2 = st.selectbox("Platzierung für Team 2:", [1, 2, 3], index=1)
    res_t3 = st.selectbox("Platzierung für Team 3:", [1, 2, 3], index=2)
    
    if st.button("Runde auswerten & Punkte berechnen 📊"):
        results = {"1": res_t1, "2": res_t2, "3": res_t3}
        
        for i in ["1", "2", "3"]:
            w = st.session_state[f'w{i}']
            if w:
                if w['tipp'] == results[i]:
                    # Gewonnen: Einsatz wird verdoppelt gutgeschrieben
                    st.session_state[f'p{i}'] += w['einsatz']
                    st.toast(f"Team {i} hat richtig getippt! 🎉")
                else:
                    # Verloren: Einsatz wird abgezogen
                    st.session_state[f'p{i}'] -= w['einsatz']
                    st.toast(f"Team {i} lag falsch. ❌")
            # Wette für die nächste Runde zurücksetzen
            st.session_state[f'w{i}'] = None
            
        st.success("Punkte wurden aktualisiert und Wetten zurückgesetzt!")
        st.rerun()