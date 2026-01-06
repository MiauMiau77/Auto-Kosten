import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import plotly.express as px

# SEITEN-KONFIGURATION
st.set_page_config(page_title="Auto-Kosten Tracker", page_icon="🚗", layout="wide")

st.title("🚗 Fahrzeug-Kosten Tracker (CHF)")

# Verbindung zu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# NUTZER-EINSTELLUNG (Sidebar)
user_name = st.sidebar.text_input("Dein Name / Kürzel", value="Gast")

# Daten aus Google Sheets laden
try:
    df = conn.read(worksheet="Daten", ttl=0)
except Exception:
    st.error("Konnte keine Daten laden. Prüfe dein Google Sheet.")
    df = pd.DataFrame(columns=["Nutzer", "Datum", "Fahrzeug", "Kategorie", "Betrag_CHF", "Notiz"])

# FAHRZEUG-LISTE FÜR DROPDOWN VORBEREITEN
if not df.empty and "Fahrzeug" in df.columns:
    # Wir nehmen alle eindeutigen Fahrzeugnamen aus dem Sheet
    vorhandene_autos = sorted(df["Fahrzeug"].dropna().unique().tolist())
else:
    vorhandene_autos = []

# EINGABE-FORMULAR
with st.form("ausgabe_form"):
    st.subheader("Neuen Eintrag hinzufügen")
    col1, col2 = st.columns(2)
    
    with col1:
        datum = st.date_input("Datum", datetime.date.today())
        
        # Fahrzeug-Wahl via Dropdown
        auto_wahl = st.selectbox("Fahrzeug wählen", ["+ Neues Fahrzeug hinzufügen"] + vorhandene_autos)
        
        if auto_wahl == "+ Neues Fahrzeug hinzufügen":
            fahrzeug = st.text_input("Name des neuen Fahrzeugs", placeholder="z.B. Tesla Model 3")
        else:
            fahrzeug = auto_wahl
            
    with col2:
        kat = st.selectbox("Kategorie", ["Tanken", "Service/Reparatur", "Versicherung", "Busse", "Parkgebühren", "Sonstiges"])
        betrag = st.number_input("Betrag in CHF", min_value=0.0, step=0.05, format="%.2f")
    
    notiz = st.text_area("Notiz (optional)")
    submit = st.form_submit_button("Speichern")

    if submit:
        if fahrzeug.strip() == "":
            st.error("Bitte gib einen Fahrzeugnamen ein!")
        else:
            new_data = pd.DataFrame([{
                "Nutzer": user_name,
                "Datum": str(datum),
                "Fahrzeug": fahrzeug,
                "Kategorie": kat,
                "Betrag_CHF": betrag,
                "Notiz": notiz
            }])
            
            updated_df = pd.concat([df, new_data
