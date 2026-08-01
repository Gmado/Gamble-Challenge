import streamlit as st
import streamlit.components.v1 as components

# Seite im Wide-Mode laden, damit das Drag-and-Drop viel Platz hat
st.set_page_config(page_title="Gaming Challenge - Live Wettbüro", page_icon="🎮", layout="wide")

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
        # In-App Abfrage für das Löschen via nativem Streamlit Popover
        with st.popover("🛑 Lobby löschen", use_container_width=True):
            st.warning("Möchtest du die aktuelle Lobby wirklich komplett löschen? Alle Punkte und Anmeldungen gehen verloren.")
            if st.button("Ja, Lobby unwiderruflich löschen", type="primary", use_container_width=True):
                global_state["points"] = {"Team 1": 7, "Team 2": 7, "Team 3": 7}
                global_state["wetten"] = {"Team 1": None, "Team 2": None, "Team 3": None}
                global_state["taken_teams"] = {"Team 1": None, "Team 2": None, "Team 3": None}
                st.session_state.clear()
                st.success("Lobby wurde gelöscht!")
                st.rerun()

# --- GAMBLER ANSICHT (FULLSCREEN DRAG & DROP) ---
else:
    mein_team = st.session_state["my_team"]
    mein_name = st.session_state["my_name"]
    aktuelle_punkte = global_state["points"][mein_team]
    
    st.subheader(f"Dashboard: {mein_name} ({mein_team})")
    
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
        # --- HTML5 / JS FULLSCREEN INTERFACE MIT CUSTOM OVERLAY DIALOG ---
        html_code = f"""
        <div id="app-container" style="display: flex; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; padding: 20px; border-radius: 12px; color: white; box-sizing: border-box; width: 95vw; height: 78vh; gap: 20px; position: relative;">
            
            <!-- Linke Seite: Platzierungen (Nimmt den Hauptplatz ein) -->
            <div style="flex: 3; display: flex; flex-direction: column; gap: 15px; height: 100%;">
                <div id="drop-1" class="dropzone" data-platz="1" style="flex: 1; background: #242424; border: 3px dashed #4caf50; padding: 15px; border-radius: 10px; display: flex; flex-direction: column; min-height: 0;">
                    <b style="color: #4caf50; font-size: 1.3rem;">🥇 1. PLATZ</b>
                    <div class="chip-container" style="display:flex; flex-wrap: wrap; gap:10px; margin-top:15px; flex: 1; min-height: 0; overflow-y: auto;"></div>
                </div>
                <div id="drop-2" class="dropzone" data-platz="2" style="flex: 1; background: #242424; border: 3px dashed #2196f3; padding: 15px; border-radius: 10px; display: flex; flex-direction: column; min-height: 0;">
                    <b style="color: #2196f3; font-size: 1.3rem;">🥈 2. PLATZ</b>
                    <div class="chip-container" style="display:flex; flex-wrap: wrap; gap:10px; margin-top:15px; flex: 1; min-height: 0; overflow-y: auto;"></div>
                </div>
                <div id="drop-3" class="dropzone" data-platz="3" style="flex: 1; background: #242424; border: 3px dashed #ff9800; padding: 15px; border-radius: 10px; display: flex; flex-direction: column; min-height: 0;">
                    <b style="color: #ff9800; font-size: 1.3rem;">🥉 3. PLATZ</b>
                    <div class="chip-container" style="display:flex; flex-wrap: wrap; gap:10px; margin-top:15px; flex: 1; min-height: 0; overflow-y: auto;"></div>
                </div>
            </div>
            
            <!-- Rechte Seite: Fester Chip-Stack & Button -->
            <div style="flex: 1; background: #222222; padding: 20px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-sizing: border-box; border: 1px solid #333;">
                <div style="text-align: center;">
                    <h3 style="margin-top: 0; font-size: 1.4rem;">Deine Bank</h3>
                    <p style="color: #aaa; margin-bottom: 15px;">Chips ({aktuelle_punkte}) nach links ziehen</p>
                    <div id="chip-bank" style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; border: 2px solid #444; padding: 15px; border-radius: 8px; background: #151515; overflow-y: auto; max-height: 45vh;">
                    </div>
                </div>
                <button id="submit-btn" style="width: 100%; background: #4caf50; color: white; border: none; padding: 15px; border-radius: 8px; cursor: pointer; font-size: 1.2rem; font-weight: bold; transition: background 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">Wette bestätigen 🔒</button>
            </div>

            <!-- IN-APP CONFIRMATION DIALOG (OVERLAY) -->
            <div id="custom-confirm" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); border-radius: 12px; justify-content: center; align-items: center; z-index: 9999;">
                <div style="background: #2d2d2d; border: 2px solid #ff9800; padding: 30px; border-radius: 10px; text-align: center; max-width: 450px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <h3 style="color: #ff9800; margin-top: 0;">Platzierung ändern?</h3>
                    <p id="confirm-msg" style="font-size: 1.1rem; line-height: 1.4; color: #eee;"></p>
                    <div style="display: flex; gap: 15px; justify-content: center; margin-top: 25px;">
                        <button id="confirm-yes" style="background: #4caf50; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1rem;">Ja, verschieben</button>
                        <button id="confirm-no" style="background: #f44336; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1rem;">Abbrechen</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const maxChips = {aktuelle_punkte};
            const bank = document.getElementById('chip-bank');
            let gewetteterPlatz = null;
            let pendingChip = null;
            let pendingZone = null;

            // Generiere Chips
            for(let i=1; i<=maxChips; i++) {{
                const chip = document.createElement('div');
                chip.className = 'chip';
                chip.id = 'chip-' + i;
                chip.draggable = true;
                chip.style.cssText = "width: 45px; height: 45px; background: #e91e63; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.1rem; cursor: grab; border: 3px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.4); user-select: none; transition: transform 0.1s;";
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
                            // Öffne das In-App Custom Overlay
                            pendingChip = chip;
                            pendingZone = zone;
                            document.getElementById('confirm-msg').innerText = "Du hast bereits Chips auf Platz " + gewetteterPlatz + " liegen. Möchtest du deine Wette komplett auf Platz " + targetPlatz + " ändern?";
                            document.getElementById('custom-confirm').style.display = 'flex';
                        }} else {{
                            gewetteterPlatz = targetPlatz;
                            zone.querySelector('.chip-container').appendChild(chip);
                        }}
                    }}
                }});
            }});

            // Custom Dialog Handlers
            document.getElementById('confirm-yes').addEventListener('click', () => {{
                if(pendingChip && pendingZone) {{
                    const targetPlatz = pendingZone.getAttribute('data-platz');
                    // Verschiebe alle existierenden Chips aus allen Zonen zur neuen Zone
                    document.querySelectorAll('.dropzone .chip').forEach(c => {{
                        pendingZone.querySelector('.chip-container').appendChild(c);
                    }});
                    pendingZone.querySelector('.chip-container').appendChild(pendingChip);
                    gewetteterPlatz = targetPlatz;
                }}
                closeDialog();
            }});

            document.getElementById('confirm-no').addEventListener('click', () => {{
                closeDialog();
            }});

            function closeDialog() {{
                document.getElementById('custom-confirm').style.display = 'none';
                pendingChip = null;
                pendingZone = null;
            }}

            // Wette abschicken
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
        
        # Rendert die interaktive JS-Komponente mit erhöhter Höhe für Fullscreen-Look
        data = components.html(html_code, height=620)
        
        if data:
            st.session_state[f"submitted_wette_{mein_team}"] = data
            st.rerun()