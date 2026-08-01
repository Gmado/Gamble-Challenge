import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gaming Challenge - Live Wettbüro", page_icon="🎮", layout="centered")

# --- GLOBALER SPEICHER (SYNCHRONISIERT) ---
@st.cache_resource
def get_global_state():
    return {
        "lobby_active": True, 
        "points": {"Team 1": 7, "Team 2": 7, "Team 3": 7},
        "wetten": {"Team 1": None, "Team 2": None, "Team 3": None},
        "taken_teams": {"Team 1": None, "Team 2": None, "Team 3": None}
    }

global_state = get_global_state()

st.title("🎮 Das ultimative Live-Wettbüro")

# --- LOGIN / RE-ENTRY LOGIK ---
if "my_team" not in st.session_state and "is_admin" not in st.session_state:
    st.subheader("Lobby beitreten / Wiederverbinden")
    input_name = st.text_input("Dein Name:", placeholder="Gib deinen Namen oder Admin-Code ein...").strip()
    
    if st.button("Bestätigen 🚪"):
        if input_name == "Admin07":
            st.session_state["is_admin"] = True
            st.success("Erfolgreich als Admin angemeldet!")
            st.rerun()
        elif input_name == "":
            st.error("Bitte gib einen Namen ein!")
        else:
            # Check 1: Wiederverbindung
            found_team = None
            for team, name in global_state["taken_teams"].items():
                if name == input_name:
                    found_team = team
                    break
            
            if found_team:
                st.session_state["my_team"] = found_team
                st.session_state["my_name"] = input_name
                st.success(f"Willkommen zurück, {input_name}! Du bist in {found_team}.")
                st.rerun()
            else:
                # Check 2: Erst-Login
                verfuegbare_teams = [t for t, user in global_state["taken_teams"].items() if user is None]
                if not verfuegbare_teams:
                    st.error("Alle Teams sind bereits voll und dieser Name ist nicht für ein Re-Entry registriert!")
                else:
                    gewaehltes_team = verfuegbare_teams[0]
                    global_state["taken_teams"][gewaehltes_team] = input_name
                    st.session_state["my_team"] = gewaehltes_team
                    st.session_state["my_name"] = input_name
                    st.success(f"Erfolgreich beigetreten! Du spielst für {gewaehltes_team}.")
                    st.rerun()

# --- ADMIN ANSICHT ---
elif st.session_state.get("is_admin", False):
    st.subheader("🔑 Admin-Panel (Spielleiter)")
    
    st.write("**Aktueller Status der Teams:**")
    for team in ["Team 1", "Team 2", "Team 3"]:
        user = global_state["taken_teams"][team]
        wette = global_state["wetten"][team]
        user_text = f"👤 Gambler: **{user}**" if user else "❌ *Niemand*"
        
        # FEHLERBEHEBUNG: Sicheres Auslesen der Wette, falls das JS-Format abweicht
        if wette and isinstance(wette, dict) and 'einsatz' in wette and 'tipp' in wette:
            wette_text = f" | 🎲 Wette: {wette['einsatz']} Pkt. auf Platz {wette['tipp']}"
        elif wette:
            wette_text = f" | 🎲 Wette: Fehlerhaftes Format ({str(wette)})"
        else:
            wette_text = " | ⏳ *Keine Wette*"
            
        st.write(f"- **{team}** ({global_state['points'][team]} Pkt.): {user_text}{wette_text}")
        
    st.write("---")
    res_t1 = st.selectbox("Platzierung für Team 1:", [1, 2, 3], index=0)
    res_t2 = st.selectbox("Platzierung für Team 2:", [1, 2, 3], index=1)
    res_t3 = st.selectbox("Platzierung für Team 3:", [1, 2, 3], index=2)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Runde auswerten & Punkte berechnen 📊", use_container_width=True):
            results = {"Team 1": res_t1, "Team 2": res_t2, "Team 3": res_t3}
            for t in ["Team 1", "Team 2", "Team 3"]:
                w = global_state["wetten"][t]
                if w and isinstance(w, dict) and 'einsatz' in w and 'tipp' in w:
                    if w['tipp'] == results[t]:
                        global_state["points"][t] += w['einsatz']
                    else:
                        global_state["points"][t] -= w['einsatz']
                global_state["wetten"][t] = None 
            st.success("Auswertung abgeschlossen!")
            st.rerun()
    with col2:
        if st.button("Lobby komplett zurücksetzen 🛑", use_container_width=True):
            global_state["points"] = {"Team 1": 7, "Team 2": 7, "Team 3": 7}
            global_state["wetten"] = {"Team 1": None, "Team 2": None, "Team 3": None}
            global_state["taken_teams"] = {"Team 1": None, "Team 2": None, "Team 3": None}
            st.session_state.clear()
            st.rerun()

# --- GAMBLER ANSICHT (MIT DRAG & DROP) ---
else:
    mein_team = st.session_state["my_team"]
    mein_name = st.session_state["my_name"]
    aktuelle_punkte = global_state["points"][mein_team]
    
    st.subheader(f"Dashboard: {mein_name} ({mein_team})")
    
    # Sicherstellen, dass empfangene Daten ein valides Dictionary sind
    if f"submitted_wette_{mein_team}" in st.session_state:
        wette_data = st.session_state[f"submitted_wette_{mein_team}"]
        if wette_data and isinstance(wette_data, dict) and 'einsatz' in wette_data:
            global_state["wetten"][mein_team] = wette_data
        del st.session_state[f"submitted_wette_{mein_team}"]
        st.rerun()

    aktuelle_wette = global_state["wetten"][mein_team]
    
    if aktuelle_wette is not None and isinstance(aktuelle_wette, dict) and 'einsatz' in aktuelle_wette:
        st.info(f"Deine Wette steht: **{aktuelle_wette['einsatz']} Chips auf Platz {aktuelle_wette['tipp']}**. Warte auf die Auswertung...")
        if st.button("🔄 Ansicht aktualisieren"):
            st.rerun()
    elif aktuelle_punkte <= 0:
        st.error("Du bist pleite und hast 0 Chips übrig!")
    else:
        # --- INTERAKTIVES DRAG & DROP INTERFACE (HTML5 / JS) ---
        html_code = f"""
        <div style="display: flex; font-family: sans-serif; background: #1e1e1e; padding: 20px; border-radius: 10px; color: white;">
            <!-- Linke Seite: Platzierungen -->
            <div style="flex: 2; display: flex; flex-direction: column; gap: 15px;">
                <div id="drop-1" class="dropzone" data-platz="1" style="background: #2d2d2d; border: 2px dashed #4caf50; padding: 20px; border-radius: 8px; min-height: 60px;">
                    <b style="color: #4caf50;">🥇 1. PLATZ</b> <span style="font-size:12px;color:#aaa;">(Chips hierher ziehen)</span>
                    <div class="chip-container" style="display:flex; gap:5px; margin-top:10px;"></div>
                </div>
                <div id="drop-2" class="dropzone" data-platz="2" style="background: #2d2d2d; border: 2px dashed #2196f3; padding: 20px; border-radius: 8px; min-height: 60px;">
                    <b style="color: #2196f3;">🥈 2. PLATZ</b>
                    <div class="chip-container" style="display:flex; gap:5px; margin-top:10px;"></div>
                </div>
                <div id="drop-3" class="dropzone" data-platz="3" style="background: #2d2d2d; border: 2px dashed #ff9800; padding: 20px; border-radius: 8px; min-height: 60px;">
                    <b style="color: #ff9800;">🥉 3. PLATZ</b>
                    <div class="chip-container" style="display:flex; gap:5px; margin-top:10px;"></div>
                </div>
            </div>
            
            <!-- Rechte Seite: Dein Chip-Stack -->
            <div style="flex: 1; margin-left: 20px; background: #252525; padding: 15px; border-radius: 8px; text-align: center;">
                <h4>Deine Chips ({aktuelle_punkte})</h4>
                <div id="chip-bank" style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; min-height: 100px; border: 1px solid #444; padding: 10px; border-radius: 5px;">
                </div>
                <button id="submit-btn" style="margin-top: 20px; width: 100%; background: #4caf50; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold;">Wette bestätigen 🔒</button>
            </div>
        </div>

        <script>
            const maxChips = {aktuelle_punkte};
            const bank = document.getElementById('chip-bank');
            let gewetteterPlatz = null;

            for(let i=1; i<=maxChips; i++) {{
                const chip = document.createElement('div');
                chip.className = 'chip';
                chip.id = 'chip-' + i;
                chip.draggable = true;
                chip.style.cssText = "width: 35px; height: 35px; background: #e91e63; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px; cursor: grab; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); user-select: none;";
                chip.innerText = "1";
                
                chip.addEventListener('dragstart', (e) => {{
                    e.dataTransfer.setData('text/plain', chip.id);
                }});
                bank.appendChild(chip);
            }}

            const zones = document.querySelectorAll('.dropzone, #chip-bank');
            zones.forEach(zone => {{
                zone.addEventListener('dragover', (e) => e.preventDefault());
                zone.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    const id = e.dataTransfer.getData('text');
                    const chip = document.getElementById(id);
                    
                    if (zone.id === 'chip-bank') {{
                        bank.appendChild(chip);
                        let remaining = false;
                        document.querySelectorAll('.dropzone').forEach(dz => {{
                            if(dz.querySelector('.chip')) remaining = true;
                        }});
                        if(!remaining) gewetteterPlatz = null;
                    }} else {{
                        const targetPlatz = zone.getAttribute('data-platz');
                        
                        if (gewetteterPlatz && gewetteterPlatz !== targetPlatz) {{
                            if (confirm("Möchtest du die Platzierung deiner Wette für alle Chips auf Platz " + targetPlatz + " ändern?")) {{
                                document.querySelectorAll('.dropzone .chip').forEach(c => {{
                                    zone.querySelector('.chip-container').appendChild(c);
                                }});
                                gewetteterPlatz = targetPlatz;
                            }} else {{
                                return;
                            }}
                        }}
                        
                        gewetteterPlatz = targetPlatz;
                        zone.querySelector('.chip-container').appendChild(chip);
                    }}
                }});
            }});

            document.getElementById('submit-btn').addEventListener('click', () => {{
                let einsatz = 0;
                document.querySelectorAll('.dropzone').forEach(dz => {{
                    const count = dz.querySelectorAll('.chip').length;
                    if(count > 0) {{
                        einsatz = count;
                    }}
                }});

                if (einsatz === 0 || !gewetteterPlatz) {{
                    alert("Bitte ziehe mindestens einen Chip auf eine Platzierung!");
                    return;
                }}

                const state = {{einsatz: einsatz, tipp: parseInt(gewetteterPlatz)}};
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: state
                }}, '*');
            }});
        </script>
        """
        
        data = components.html(html_code, height=350)
        
        if data:
            st.session_state[f"submitted_wette_{mein_team}"] = data
            st.rerun()