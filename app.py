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
    vorhandene_autos = sorted(df["Fahrzeug"].dropna().unique().tolist())
else:
    vorhandene_autos = []

# EINGABE-FORMULAR
with st.form("ausgabe_form"):
    st.subheader("Neuen Eintrag hinzufügen")
    col1, col2 = st.columns(2)
    
    with col1:
        datum = st.date_input("Datum", datetime.date.today())
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
            # Neuen Datensatz erstellen
            new_data = pd.DataFrame([{
                "Nutzer": user_name,
                "Datum": str(datum),
                "Fahrzeug": fahrzeug,
                "Kategorie": kat,
                "Betrag_CHF": betrag,
                "Notiz": notiz
            }])
            
            # KORREKTUR DER ZEILE 68: Klammern sauber schliessen
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # Zurück in Google Sheets schreiben
            conn.update(worksheet="Daten", data=updated_df)
            st.success(f"Eintrag für {fahrzeug} gespeichert!")
            st.rerun()

# AUSWERTUNG & DIAGRAMME
if not df.empty and "Nutzer" in df.columns:
    user_df = df[df["Nutzer"] == user_name].copy()

    if not user_df.empty:
        st.divider()
        st.subheader(f"Statistiken für {user_name}")
        
        col_m1, col_m2 = st.columns(2)
        total_chf = user_df["Betrag_CHF"].sum()
        col_m1.metric("Gesamtkosten", f"CHF {total_chf:,.2f}")
        col_m2.metric("Anzahl Einträge", len(user_df))

        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_pie = px.pie(user_df, values='Betrag_CHF', names='Kategorie', 
                             title='Kosten nach Kategorie',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            fig_bar = px.bar(user_df.groupby("Fahrzeug")["Betrag_CHF"].sum().reset_index(), 
                             x='Fahrzeug', y='Betrag_CHF', title='Kosten pro Fahrzeug')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Deine letzten Einträge")
        st.dataframe(user_df.sort_values(by="Datum", ascending=False), use_container_width=True)
    else:
        st.info(f"Hallo {user_name}! Du hast noch keine Einträge erfasst.")
