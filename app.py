import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Auto-Kosten Tracker", page_icon="🚗")

st.title("🚗 Fahrzeug-Kosten Tracker (CHF)")
st.markdown("Erfasse deine Ausgaben und speichere sie direkt in Google Sheets.")

# Verbindung zu Google Sheets definieren
conn = st.connection("gsheets", type=GSheetsConnection)

# NUTZER-EINSTELLUNG
user_name = st.sidebar.text_input("Dein Name / Kürzel", value="Gast")

# Daten aus Google Sheets laden (ttl=0 für Echtzeit-Aktualisierung)
try:
    df = conn.read(worksheet="Daten", ttl=0)
except Exception:
    st.error("Konnte keine Daten laden. Prüfe, ob das Tabellenblatt 'Daten' heisst.")
    df = pd.DataFrame(columns=["Nutzer", "Datum", "Fahrzeug", "Kategorie", "Betrag_CHF", "Notiz"])

# EINGABE-FORMULAR
with st.form("ausgabe_form"):
    st.subheader("Neuen Eintrag hinzufügen")
    col1, col2 = st.columns(2)
    
    with col1:
        datum = st.date_input("Datum", datetime.date.today())
        fahrzeug = st.text_input("Fahrzeug", placeholder="z.B. Audi A3")
    
    with col2:
        kat = st.selectbox("Kategorie", ["Tanken", "Service/Reparatur", "Versicherung", "Busse", "Parkgebühren", "Sonstiges"])
        betrag = st.number_input("Betrag in CHF", min_value=0.0, step=0.05, format="%.2f")
    
    notiz = st.text_area("Notiz (optional)")
    submit = st.form_submit_button("Speichern")

    if submit:
        # Neuen Datensatz erstellen
        new_data = pd.DataFrame([{
            "Nutzer": user_name,
            "Datum": str(datum),
            "Fahrzeug": fahrzeug,
            "Kategorie": kat,
            "Betrag_CHF": betrag,
            "Notiz": notiz
        }])
        
        # Bestehende Daten mit neuen Daten zusammenführen
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        # Zurück in Google Sheets schreiben
        conn.update(worksheet="Daten", data=updated_df)
        st.success("Erfolgreich gespeichert!")
        st.rerun()

# AUSWERTUNG
st.subheader(f"Übersicht für {user_name}")

# Filter auf den aktuellen Nutzer
if not df.empty:
    user_df = df[df["Nutzer"] == user_name].copy()

    if not user_df.empty:
        total_chf = user_df["Betrag_CHF"].sum()
        st.metric("Gesamtkosten", f"CHF {total_chf:,.2f}")
        
        # Tabelle anzeigen
        st.dataframe(user_df.sort_values(by="Datum", ascending=False), use_container_width=True)
    else:
        st.info("Noch keine Einträge für dich gefunden.")
else:
    st.info("Die Datenbank ist noch leer.")
